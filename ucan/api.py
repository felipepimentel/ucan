import base64
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class API:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.headers = {"Content-Type": "application/json"}
        self.message_history = []
        self.max_history = 50

    def send_message(self, message: str, attachment: Optional[dict] = None) -> str:
        """Send a message to the API with optional attachment"""
        try:
            # Prepare message
            data = {
                "messages": self.message_history
                + [{"role": "user", "content": message}]
            }

            # Add attachment if present
            if attachment:
                with open(attachment["path"], "rb") as f:
                    content = base64.b64encode(f.read()).decode()

                data["attachment"] = {
                    "name": attachment["name"],
                    "type": attachment["type"],
                    "content": content,
                }

            # Send request
            response = requests.post(
                f"{self.base_url}/chat", headers=self.headers, json=data, timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")

            result = response.json()

            # Update history
            self.message_history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": result["response"]},
            ])

            # Trim history if too long
            if len(self.message_history) > self.max_history:
                self.message_history = self.message_history[-self.max_history :]

            return result["response"]

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
