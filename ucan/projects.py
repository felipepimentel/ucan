import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from .database import Database

logger = logging.getLogger("UCAN")


class ProjectManager:
    def __init__(self, db: Database):
        self.db = db
        self.current_project: Optional[Dict] = None
        self.projects_dir = os.path.join(os.path.dirname(__file__), "projects")
        os.makedirs(self.projects_dir, exist_ok=True)

    def create_project(self, name: str, description: str, instructions: str) -> Dict:
        """Create a new project"""
        try:
            # Create project directory
            project_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_dir = os.path.join(self.projects_dir, project_id)
            os.makedirs(project_dir, exist_ok=True)

            # Create project metadata
            project = {
                "id": project_id,
                "name": name,
                "description": description,
                "instructions": instructions,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "conversations": [],
                "files": [],
                "settings": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
            }

            # Save project metadata
            self._save_project_metadata(project)

            # Save to database
            self.db.save_project(project)

            return project

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

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

    def update_project(self, project_id: str, updates: Dict) -> bool:
        """Update project metadata"""
        try:
            # Update project metadata
            project = self.load_project(project_id)
            if not project:
                return False

            project.update(updates)
            project["updated_at"] = datetime.now().isoformat()

            # Save updated metadata
            self._save_project_metadata(project)

            # Update database
            self.db.update_project(project_id, updates)

            return True

        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return False

    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        try:
            # Delete project directory
            project_dir = os.path.join(self.projects_dir, project_id)
            if os.path.exists(project_dir):
                for root, dirs, files in os.walk(project_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(project_dir)

            # Delete from database
            self.db.delete_project(project_id)

            return True

        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return False

    def list_projects(self) -> List[Dict]:
        """List all projects"""
        try:
            # Get projects from database
            projects = self.db.get_all_projects()
            if projects:
                return projects

            # If no projects in database, scan directory
            projects = []
            for project_id in os.listdir(self.projects_dir):
                project = self.load_project(project_id)
                if project:
                    projects.append(project)

            return projects

        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return []

    def add_conversation(self, project_id: str, conversation: Dict) -> bool:
        """Add a conversation to a project"""
        try:
            project = self.load_project(project_id)
            if not project:
                return False

            conversation["id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
            conversation["created_at"] = datetime.now().isoformat()
            project["conversations"].append(conversation)
            project["updated_at"] = datetime.now().isoformat()

            # Save updated metadata
            self._save_project_metadata(project)

            # Update database
            self.db.update_project(
                project_id, {"conversations": project["conversations"]}
            )

            return True

        except Exception as e:
            logger.error(f"Error adding conversation: {str(e)}")
            return False

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
