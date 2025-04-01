import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("UCAN")


class ProjectManager:
    def __init__(self, db):
        self.db = db
        self.current_project: Optional[Dict] = None
        self.projects_dir = os.path.join(os.path.dirname(__file__), "projects")
        os.makedirs(self.projects_dir, exist_ok=True)

    def create_project(
        self, name: str, description: str, instructions: str = ""
    ) -> int:
        """Create a new project"""
        return self.db.save_project(name, description, instructions)

    def update_project(self, project_id: int, project_data: dict) -> bool:
        """Update an existing project"""
        try:
            self.db.save_project(
                name=project_data["name"],
                description=project_data["description"],
                instructions=project_data.get("instructions", ""),
            )
            return True
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return False

    def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        return self.db.delete_project(project_id)

    def list_projects(self):
        """List all projects"""
        return self.db.get_all_projects()

    def get_project(self, project_id: int):
        """Get a project by ID"""
        return self.db.get_project(project_id)

    def add_conversation(self, project_id: int, conversation: dict):
        """Add a conversation to a project"""
        return self.db.save_conversation(
            project_id, conversation["sender"], conversation["content"]
        )

    def update_conversation(self, project_id: int, conversation: dict):
        """Update a conversation in a project"""
        # TODO: Implement conversation update
        pass

    def load_project(self, project_id: str) -> Optional[Dict]:
        """Load a project by ID"""
        try:
            # Try to load from database first
            project = self.db.get_project(project_id)
            if project:
                self.current_project = project
                return project

            # If not in database, try to load from file
            project_file = os.path.join(self.projects_dir, project_id, "metadata.json")
            if os.path.exists(project_file):
                with open(project_file, "r", encoding="utf-8") as f:
                    project = json.load(f)
                    self.current_project = project
                    return project

            return None

        except Exception as e:
            logger.error(f"Error loading project: {str(e)}")
            return None

    def add_file(self, project_id: str, file_info: Dict) -> bool:
        """Add a file to a project"""
        try:
            project = self.load_project(project_id)
            if not project:
                return False

            file_info["id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_info["added_at"] = datetime.now().isoformat()
            project["files"].append(file_info)
            project["updated_at"] = datetime.now().isoformat()

            # Save updated metadata
            self._save_project_metadata(project)

            # Update database
            self.db.update_project(project_id, {"files": project["files"]})

            return True

        except Exception as e:
            logger.error(f"Error adding file: {str(e)}")
            return False

    def _save_project_metadata(self, project: Dict) -> None:
        """Save project metadata to file"""
        try:
            project_dir = os.path.join(self.projects_dir, project["id"])
            metadata_file = os.path.join(project_dir, "metadata.json")
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving project metadata: {str(e)}")
            raise
