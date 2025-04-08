import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("UCAN")


class ProjectManager:
    """Manages projects and conversations"""

    def __init__(self, db):
        self.db = db
        self.current_project: Optional[Dict] = None
        self.projects_dir = os.path.join(os.path.dirname(__file__), "projects")
        os.makedirs(self.projects_dir, exist_ok=True)
        self.project_frames = {}  # Map project frames to project data

    def list_projects(self) -> List[Dict]:
        """List all projects"""
        try:
            return self.db.get_all_projects()
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return []

    def list_conversations(self) -> List[Dict]:
        """List all standalone conversations"""
        try:
            return self.db.get_all_conversations()
        except Exception as e:
            logger.error(f"Error listing conversations: {str(e)}")
            return []

    def create_project(
        self, name: str, description: str, instructions: str = ""
    ) -> Optional[int]:
        """Create a new project"""
        try:
            project_data = {
                "name": name,
                "description": description,
                "instructions": instructions,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            return self.db.create_project(project_data)
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return None

    def create_conversation(self, title: str = None) -> Optional[int]:
        """Create a new standalone conversation"""
        try:
            default_title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            conversation_data = {
                "title": title or default_title,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "messages": [],
            }
            return self.db.create_conversation(conversation_data)
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            return None

    def update_project(self, project_id: int, data: dict) -> bool:
        """Update project data"""
        try:
            data["updated_at"] = datetime.now()
            return self.db.update_project(project_id, data)
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return False

    def update_conversation(self, conversation_id: int, data: dict) -> bool:
        """Update conversation data"""
        try:
            data["updated_at"] = datetime.now()
            return self.db.update_conversation(conversation_id, data)
        except Exception as e:
            logger.error(f"Error updating conversation: {str(e)}")
            return False

    def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        try:
            return self.db.delete_project(project_id)
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return False

    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation"""
        try:
            return self.db.delete_conversation(conversation_id)
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False

    def convert_to_project(
        self, conversation_id: int, name: str, description: str
    ) -> Optional[int]:
        """Convert a conversation to a project"""
        try:
            # Get conversation data
            conversation = self.db.get_conversation(conversation_id)
            if not conversation:
                return None

            # Create new project
            project_data = {
                "name": name,
                "description": description,
                "instructions": "",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            # Create project
            project_id = self.db.create_project(project_data)
            if not project_id:
                return None

            # Move messages to project
            for message in conversation.get("messages", []):
                self.db.add_message_to_project(project_id, message)

            # Delete the original conversation
            self.db.delete_conversation(conversation_id)

            return project_id
        except Exception as e:
            logger.error(f"Error converting conversation to project: {str(e)}")
            return None

    def add_message(
        self, conversation_id: int, content: str, sender: str
    ) -> Optional[int]:
        """Add a message to a conversation"""
        try:
            message = {
                "content": content,
                "sender": sender,
                "created_at": datetime.now(),
            }

            message_id = self.db.add_message(conversation_id, message)

            # Update conversation last update time
            self.db.update_conversation(conversation_id, {"updated_at": datetime.now()})

            return message_id
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return None

    def add_message_to_project(
        self, project_id: int, content: str, sender: str
    ) -> Optional[int]:
        """Add a message to a project"""
        try:
            message = {
                "content": content,
                "sender": sender,
                "created_at": datetime.now(),
                "project_id": project_id,
            }

            message_id = self.db.add_message(None, message)

            # Update project last update time
            self.db.update_project(project_id, {"updated_at": datetime.now()})

            return message_id
        except Exception as e:
            logger.error(f"Error adding message to project: {str(e)}")
            return None

    def get_messages(self, conversation_id: int) -> List[Dict]:
        """Get all messages from a conversation"""
        try:
            return self.db.get_messages(conversation_id)
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []

    def get_project_messages(self, project_id: int) -> List[Dict]:
        """Get all messages from a project"""
        try:
            return self.db.get_project_messages(project_id)
        except Exception as e:
            logger.error(f"Error getting project messages: {str(e)}")
            return []

    def mark_as_read(self, conversation_id: int) -> bool:
        """Mark a conversation as read"""
        try:
            return self.db.update_conversation(
                conversation_id, {"unread": False, "updated_at": datetime.now()}
            )
        except Exception as e:
            logger.error(f"Error marking conversation as read: {str(e)}")
            return False

    def mark_as_unread(self, conversation_id: int) -> bool:
        """Mark a conversation as unread"""
        try:
            return self.db.update_conversation(
                conversation_id, {"unread": True, "updated_at": datetime.now()}
            )
        except Exception as e:
            logger.error(f"Error marking conversation as unread: {str(e)}")
            return False

    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get a project by ID"""
        try:
            return self.db.get_project(project_id)
        except Exception as e:
            logger.error(f"Error getting project: {str(e)}")
            return None

    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """Get a conversation by ID"""
        try:
            return self.db.get_conversation(conversation_id)
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            return None

    def search(self, query: str) -> Dict[str, List[Dict]]:
        """Search in projects and conversations"""
        try:
            return self.db.search(query)
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return {"projects": [], "conversations": []}
