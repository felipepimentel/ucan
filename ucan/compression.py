import logging
from datetime import datetime, timedelta
from typing import Dict, List

from transformers import pipeline

logger = logging.getLogger("UCAN")


class MessageCompressor:
    def __init__(self, db):
        self.db = db
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.max_context_length = 4096  # Maximum tokens to keep in context
        self.compression_threshold = 10  # Number of messages before compression
        self.summary_cache = {}

    def compress_history(self, contact_name: str) -> None:
        """Compress chat history for a contact"""
        try:
            messages = self.db.get_messages(contact_name)

            if len(messages) < self.compression_threshold:
                return

            # Group messages by date
            grouped_messages = self._group_messages_by_date(messages)

            # Compress old message groups
            for date, msgs in grouped_messages.items():
                if self._should_compress(date):
                    summary = self._summarize_messages(msgs)
                    self._store_summary(contact_name, date, summary, msgs)

        except Exception as e:
            logger.error(f"Error compressing history: {str(e)}")

    def get_compressed_context(
        self, contact_name: str, limit: int = None
    ) -> List[Dict]:
        """Get compressed context for conversation"""
        try:
            messages = self.db.get_messages(contact_name)

            if not messages:
                return []

            # Get recent messages
            recent_cutoff = datetime.now() - timedelta(days=7)
            recent_messages = [
                msg
                for msg in messages
                if datetime.fromisoformat(msg["created_at"]) > recent_cutoff
            ]

            # Get summaries for older messages
            summaries = self.db.get_message_summaries(contact_name)

            # Combine summaries and recent messages
            context = []

            # Add relevant summaries
            for summary in summaries:
                context.append({
                    "content": f"[Resumo {summary['date']}]: {summary['content']}",
                    "sender": "Sistema",
                    "is_summary": True,
                })

            # Add recent messages
            context.extend(recent_messages)

            # Apply token limit if specified
            if limit:
                context = self._trim_context(context, limit)

            return context

        except Exception as e:
            logger.error(f"Error getting compressed context: {str(e)}")
            return []

    def _group_messages_by_date(self, messages: List[Dict]) -> Dict:
        """Group messages by date"""
        groups = {}
        for msg in messages:
            date = datetime.fromisoformat(msg["created_at"]).date()
            if date not in groups:
                groups[date] = []
            groups[date].append(msg)
        return groups

    def _should_compress(self, date) -> bool:
        """Check if messages from date should be compressed"""
        return datetime.now().date() - date > timedelta(days=7)

    def _summarize_messages(self, messages: List[Dict]) -> str:
        """Summarize a group of messages"""
        try:
            # Combine messages into a single text
            text = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in messages])

            # Check cache
            cache_key = hash(text)
            if cache_key in self.summary_cache:
                return self.summary_cache[cache_key]

            # Generate summary
            summary = self.summarizer(
                text, max_length=130, min_length=30, do_sample=False
            )[0]["summary_text"]

            # Cache summary
            self.summary_cache[cache_key] = summary

            return summary

        except Exception as e:
            logger.error(f"Error summarizing messages: {str(e)}")
            return "Não foi possível gerar resumo."

    def _store_summary(
        self, contact_name: str, date, summary: str, original_messages: List[Dict]
    ) -> None:
        """Store message summary"""
        try:
            self.db.save_message_summary(
                contact_name=contact_name,
                date=date.isoformat(),
                content=summary,
                original_messages=[msg["id"] for msg in original_messages],
            )
        except Exception as e:
            logger.error(f"Error storing summary: {str(e)}")

    def _trim_context(self, context: List[Dict], limit: int) -> List[Dict]:
        """Trim context to fit within token limit"""
        total_tokens = 0
        trimmed_context = []

        for item in reversed(context):
            # Rough token estimation
            tokens = len(item["content"].split())

            if total_tokens + tokens > limit:
                break

            total_tokens += tokens
            trimmed_context.insert(0, item)

        return trimmed_context
