import datetime
import logging
import random
import sqlite3
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("UCAN")


class Database:
    def __init__(self):
        """Initialize database connection"""
        try:
            # Ensure data directory exists
            data_dir = Path.home() / ".ucan"
            data_dir.mkdir(exist_ok=True)

            # Connect to database
            self.db_path = data_dir / "chat.db"
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row

            # Create tables if they don't exist
            self._create_tables()

        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise

    def _create_tables(self):
        """Create necessary database tables"""
        try:
            with self.conn:
                # Contacts table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        icon TEXT NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Messages table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        contact_id INTEGER NOT NULL,
                        sender TEXT NOT NULL,
                        content TEXT NOT NULL,
                        is_file BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (contact_id) REFERENCES contacts (id)
                    )
                """)

                # Message reactions table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS reactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER NOT NULL,
                        reaction TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (message_id) REFERENCES messages (id)
                    )
                """)

                # Templates table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Attachments table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS attachments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER,
                        name TEXT NOT NULL,
                        path TEXT NOT NULL,
                        mime_type TEXT NOT NULL,
                        preview_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (message_id) REFERENCES messages (id)
                            ON DELETE CASCADE
                    )
                """)

                # Projects table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        instructions TEXT,
                        settings TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Project conversations table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS project_conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        sender TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                            ON DELETE CASCADE
                    )
                """)

                # Project files table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS project_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        path TEXT NOT NULL,
                        mime_type TEXT NOT NULL,
                        preview_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                            ON DELETE CASCADE
                    )
                """)

        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise

    def create_project(self, project_data: dict):
        """Create a new project"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO projects (name, description, instructions, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    project_data["name"],
                    project_data["description"],
                    project_data.get("instructions", ""),
                    project_data["created_at"],
                    project_data["updated_at"],
                ),
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return None

    def create_conversation(self, conversation_data: dict):
        """Create a new conversation"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversations (title, created_at, updated_at)
                VALUES (?, ?, ?)
            """,
                (
                    conversation_data["title"],
                    conversation_data["created_at"],
                    conversation_data["updated_at"],
                ),
            )
            self.conn.commit()

            # Add initial messages if any
            conversation_id = cursor.lastrowid
            if "messages" in conversation_data:
                for message in conversation_data["messages"]:
                    self.add_message(conversation_id, message)

            return conversation_id
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            return None

    def update_project(self, project_id: int, data: dict):
        """Update project data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE projects
                SET name = ?,
                    description = ?,
                    instructions = ?,
                    updated_at = ?
                WHERE id = ?
            """,
                (
                    data["name"],
                    data["description"],
                    data.get("instructions", ""),
                    data["updated_at"],
                    project_id,
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return False

    def update_conversation(self, conversation_id: int, data: dict):
        """Update conversation data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE conversations
                SET title = ?,
                    unread = ?,
                    updated_at = ?
                WHERE id = ?
            """,
                (
                    data["title"],
                    data.get("unread", False),
                    data["updated_at"],
                    conversation_id,
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating conversation: {str(e)}")
            return False

    def delete_project(self, project_id: int):
        """Delete a project"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return False

    def delete_conversation(self, conversation_id: int):
        """Delete a conversation"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False

    def get_all_projects(self):
        """Get all projects"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT p.*, COUNT(m.id) as message_count
                FROM projects p
                LEFT JOIN messages m ON m.project_id = p.id
                GROUP BY p.id
                ORDER BY p.updated_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            return []

    def get_all_conversations(self):
        """Get all standalone conversations"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT c.*, 
                       COUNT(m.id) as message_count,
                       MAX(m.content) as last_message
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
            """)
            conversations = []
            for row in cursor.fetchall():
                conversation = dict(row)
                # Get preview from last message
                if conversation["last_message"]:
                    conversation["preview"] = conversation["last_message"][:100]
                conversations.append(conversation)
            return conversations
        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            return []

    def get_project(self, project_id: int):
        """Get a project by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT p.*, COUNT(m.id) as message_count
                FROM projects p
                LEFT JOIN messages m ON m.project_id = p.id
                WHERE p.id = ?
                GROUP BY p.id
            """,
                (project_id,),
            )
            project = cursor.fetchone()
            if project:
                return dict(project)
            return None
        except Exception as e:
            logger.error(f"Error getting project: {str(e)}")
            return None

    def get_conversation(self, conversation_id: int):
        """Get a conversation by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT c.*, COUNT(m.id) as message_count
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                WHERE c.id = ?
                GROUP BY c.id
            """,
                (conversation_id,),
            )
            conversation = cursor.fetchone()
            if conversation:
                # Get messages
                cursor.execute(
                    """
                    SELECT * FROM messages
                    WHERE conversation_id = ?
                    ORDER BY created_at
                """,
                    (conversation_id,),
                )
                messages = [dict(row) for row in cursor.fetchall()]
                result = dict(conversation)
                result["messages"] = messages
                return result
            return None
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            return None

    def add_message(self, conversation_id: int, message: dict):
        """Add a message to a conversation"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, content, sender, created_at)
                VALUES (?, ?, ?, ?)
            """,
                (
                    conversation_id,
                    message["content"],
                    message["sender"],
                    message.get("created_at", datetime.datetime.now()),
                ),
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return None

    def get_messages(self, conversation_id: int):
        """Get all messages from a conversation"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at
            """,
                (conversation_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []

    def search(self, query: str):
        """Search in projects and conversations"""
        try:
            cursor = self.conn.cursor()

            # Search in projects
            cursor.execute(
                """
                SELECT p.*, 'project' as type
                FROM projects p
                WHERE p.name LIKE ? OR p.description LIKE ?
            """,
                (f"%{query}%", f"%{query}%"),
            )
            projects = [dict(row) for row in cursor.fetchall()]

            # Search in conversations
            cursor.execute(
                """
                SELECT c.*, 'conversation' as type,
                       m.content as matching_message
                FROM conversations c
                JOIN messages m ON m.conversation_id = c.id
                WHERE c.title LIKE ? OR m.content LIKE ?
                GROUP BY c.id
            """,
                (f"%{query}%", f"%{query}%"),
            )
            conversations = [dict(row) for row in cursor.fetchall()]

            return {"projects": projects, "conversations": conversations}
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return {"projects": [], "conversations": []}

    def save_message(
        self, sender: str, contact_name: str, content: str, is_file: bool = False
    ):
        """Save a message to the database"""
        try:
            with self.conn:
                # Get or create contact
                contact_id = self._get_or_create_contact(contact_name)

                # Insert message
                self.conn.execute(
                    """
                    INSERT INTO messages (contact_id, sender, content, is_file)
                    VALUES (?, ?, ?, ?)
                """,
                    (contact_id, sender, content, is_file),
                )

        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")

    def get_messages(
        self, contact_name: str, limit: Optional[int] = None
    ) -> List[dict]:
        """Get messages for a contact"""
        try:
            query = """
                SELECT m.* FROM messages m
                JOIN contacts c ON m.contact_id = c.id
                WHERE c.name = ?
                ORDER BY m.created_at ASC
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor = self.conn.execute(query, (contact_name,))
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []

    def save_template(self, name: str, content: str):
        """Save a message template"""
        try:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO templates (name, content)
                    VALUES (?, ?)
                    ON CONFLICT (name) DO UPDATE SET
                    content = excluded.content
                """,
                    (name, content),
                )

        except Exception as e:
            logger.error(f"Error saving template: {str(e)}")

    def get_templates(self) -> List[dict]:
        """Get all message templates"""
        try:
            cursor = self.conn.execute("SELECT * FROM templates ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            return []

    def _get_or_create_contact(self, name: str) -> int:
        """Get contact ID or create if doesn't exist"""
        try:
            cursor = self.conn.execute(
                "SELECT id FROM contacts WHERE name = ?", (name,)
            )
            result = cursor.fetchone()

            if result:
                return result[0]

            # Create new contact
            cursor = self.conn.execute(
                """
                INSERT INTO contacts (name, icon)
                VALUES (?, ?)
            """,
                (name, "👤"),
            )

            return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error getting/creating contact: {str(e)}")
            raise

    def add_reaction(self, message_id: int, reaction: str):
        """Add a reaction to a message"""
        try:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO reactions (message_id, reaction)
                    VALUES (?, ?)
                """,
                    (message_id, reaction),
                )

        except Exception as e:
            logger.error(f"Error adding reaction: {str(e)}")

    def get_reactions(self, message_id: int) -> List[str]:
        """Get reactions for a message"""
        try:
            cursor = self.conn.execute(
                "SELECT reaction FROM reactions WHERE message_id = ?", (message_id,)
            )
            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error getting reactions: {str(e)}")
            return []

    def search_messages(self, query: str) -> List[dict]:
        """Search messages by content"""
        try:
            cursor = self.conn.execute(
                """
                SELECT m.*, c.name as contact_name
                FROM messages m
                JOIN contacts c ON m.contact_id = c.id
                WHERE m.content LIKE ?
                ORDER BY m.created_at DESC
                LIMIT 50
            """,
                (f"%{query}%",),
            )

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []

    def add_message(
        self, role: str, content: str, attachment: Optional[dict] = None
    ) -> int:
        """Add a message to the database with optional attachment"""
        try:
            # Add message
            self.conn.execute(
                "INSERT INTO messages (role, content) VALUES (?, ?)", (role, content)
            )
            message_id = self.conn.lastrowid

            # Add attachment if present
            if attachment:
                self.conn.execute(
                    """
                    INSERT INTO attachments (
                        message_id, name, path, mime_type, preview_path
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        message_id,
                        attachment["name"],
                        attachment["path"],
                        attachment["type"],
                        attachment.get("preview"),
                    ),
                )

            self.conn.commit()
            return message_id

        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            self.conn.rollback()
            raise

    def get_message_with_attachment(self, message_id: int) -> Optional[dict]:
        """Get a message and its attachment if present"""
        try:
            cursor = self.conn.execute(
                """
                SELECT m.*, a.name, a.path, a.mime_type, a.preview_path
                FROM messages m
                LEFT JOIN attachments a ON a.message_id = m.id
                WHERE m.id = ?
                """,
                (message_id,),
            )

            result = cursor.fetchone()
            if not result:
                return None

            message = {
                "id": result[0],
                "role": result[1],
                "content": result[2],
                "created_at": result[3],
            }

            if result[4]:  # Has attachment
                message["attachment"] = {
                    "name": result[4],
                    "path": result[5],
                    "type": result[6],
                    "preview": result[7],
                }

            return message

        except Exception as e:
            logger.error(f"Error getting message: {str(e)}")
            raise

    def get_messages_with_attachments(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[dict]:
        """Get messages with their attachments"""
        try:
            query = """
                SELECT m.*, a.name, a.path, a.mime_type, a.preview_path
                FROM messages m
                LEFT JOIN attachments a ON a.message_id = m.id
                ORDER BY m.created_at DESC
            """

            if limit is not None:
                query += f" LIMIT {limit}"

            if offset is not None:
                query += f" OFFSET {offset}"

            cursor = self.conn.execute(query)
            results = cursor.fetchall()

            messages = []
            for result in results:
                message = {
                    "id": result[0],
                    "role": result[1],
                    "content": result[2],
                    "created_at": result[3],
                }

                if result[4]:  # Has attachment
                    message["attachment"] = {
                        "name": result[4],
                        "path": result[5],
                        "type": result[6],
                        "preview": result[7],
                    }

                messages.append(message)

            return messages

        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            raise

    def save_project(
        self, name: str, description: str, instructions: str = "", settings: str = "{}"
    ) -> int:
        """Save a project to the database"""
        try:
            with self.conn:
                cursor = self.conn.execute(
                    """
                    INSERT INTO projects (name, description, instructions, settings)
                    VALUES (?, ?, ?, ?)
                """,
                    (name, description, instructions, settings),
                )
                return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error saving project: {str(e)}")
            raise

    def get_all_projects(self) -> List[dict]:
        """Get all projects"""
        try:
            cursor = self.conn.execute(
                """
                SELECT * FROM projects
                ORDER BY updated_at DESC
            """
            )
            projects = [dict(row) for row in cursor.fetchall()]

            # Get conversations and files for each project
            for project in projects:
                # Get conversations
                cursor = self.conn.execute(
                    """
                    SELECT * FROM project_conversations
                    WHERE project_id = ?
                    ORDER BY created_at ASC
                """,
                    (project["id"],),
                )
                project["conversations"] = [dict(row) for row in cursor.fetchall()]

                # Get files
                cursor = self.conn.execute(
                    """
                    SELECT * FROM project_files
                    WHERE project_id = ?
                    ORDER BY created_at ASC
                """,
                    (project["id"],),
                )
                project["files"] = [dict(row) for row in cursor.fetchall()]

            return projects

        except Exception as e:
            logger.error(f"Error getting all projects: {str(e)}")
            return []

    def add_project_conversation(
        self, project_id: int, sender: str, content: str
    ) -> int:
        """Add a conversation to a project"""
        try:
            with self.conn:
                cursor = self.conn.execute(
                    """
                    INSERT INTO project_conversations
                        (project_id, sender, content)
                    VALUES (?, ?, ?)
                """,
                    (project_id, sender, content),
                )
                return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error adding project conversation: {str(e)}")
            raise

    def add_project_file(
        self,
        project_id: int,
        name: str,
        path: str,
        mime_type: str,
        preview_path: Optional[str] = None,
    ) -> int:
        """Add a file to a project"""
        try:
            with self.conn:
                cursor = self.conn.execute(
                    """
                    INSERT INTO project_files
                        (project_id, name, path, mime_type, preview_path)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (project_id, name, path, mime_type, preview_path),
                )
                return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error adding project file: {str(e)}")
            raise

    def save_conversation(self, project_id: int, sender: str, content: str) -> int:
        """Save a conversation to a project"""
        try:
            with self.conn:
                cursor = self.conn.execute(
                    """
                    INSERT INTO project_conversations (project_id, sender, content)
                    VALUES (?, ?, ?)
                """,
                    (project_id, sender, content),
                )
                return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            raise

    def generate_test_data(self):
        """Generate test data for the application"""
        try:
            # Clear existing test data
            self._clear_test_data()

            # Generate test projects
            project_ids = []

            # Project 1: E-commerce
            project_ids.append(
                self.save_project(
                    "E-commerce Platform",
                    "Desenvolvimento de uma plataforma completa de comércio eletrônico com integração de pagamentos e gestão de estoque",
                    "Este projeto visa criar uma plataforma de e-commerce moderna e escalável",
                )
            )

            # Project 2: API REST
            project_ids.append(
                self.save_project(
                    "API REST Documentation",
                    "Documentação completa da API REST para integração com parceiros e desenvolvedores externos",
                    "Projeto para documentar e padronizar a API REST da plataforma",
                )
            )

            # Project 3: Bug Tracking
            project_ids.append(
                self.save_project(
                    "Bug Tracking System",
                    "Sistema de acompanhamento de bugs e problemas encontrados no desenvolvimento",
                    "Sistema interno para gerenciamento de bugs e issues",
                )
            )

            # Project 4: Mobile App
            project_ids.append(
                self.save_project(
                    "Aplicativo Mobile",
                    "Desenvolvimento do aplicativo mobile para iOS e Android com React Native",
                    "Projeto para criar a versão mobile da plataforma",
                )
            )

            # Project 5: Data Analytics
            project_ids.append(
                self.save_project(
                    "Data Analytics Dashboard",
                    "Dashboard de análise de dados e métricas de negócio para tomada de decisões",
                    "Projeto para visualização e análise de dados de negócio",
                )
            )

            # Generate conversations for each project
            for i, project_id in enumerate(project_ids):
                # Create 2-3 conversations per project
                for j in range(1, random.randint(3, 5)):
                    conversation_title = f"Conversa {j} - Projeto {i + 1}"
                    self.add_project_conversation(
                        project_id,
                        "Sistema",
                        f"Iniciando conversa: {conversation_title}",
                    )

            # Create standalone messages with contacts
            for i in range(1, 6):
                contact_name = f"Contato {i}"
                # Ensure contact exists
                self._get_or_create_contact(contact_name)

                # Add messages
                self.save_message(
                    "Você",
                    contact_name,
                    f"Olá, esta é uma mensagem de teste {i}",
                    False,
                )

                self.save_message(
                    "Assistente",
                    contact_name,
                    f"Olá! Como posso ajudar com sua solicitação? Esta é uma resposta automática de teste {i}",
                    False,
                )

            # Create sample templates
            sample_templates = [
                {
                    "name": "Relatório de Status",
                    "content": "Status do projeto: [status]\n\nProgressos realizados:\n- [progresso 1]\n- [progresso 2]\n- [progresso 3]\n\nPendências:\n- [pendência 1]\n- [pendência 2]\n\nPróximos passos:\n1. [próximo passo 1]\n2. [próximo passo 2]",
                },
                {
                    "name": "Solicitação de Feedback",
                    "content": "Olá equipe,\n\nPreciso de feedback sobre [assunto]. Especificamente, gostaria de saber:\n\n1. O que está funcionando bem?\n2. O que pode ser melhorado?\n3. Há alguma preocupação ou bloqueio que devemos resolver?\n\nPor favor, respondam até [data].",
                },
                {
                    "name": "Daily Standup",
                    "content": "Daily Standup - [data]\n\nO que fiz ontem:\n- [tarefa 1]\n- [tarefa 2]\n\nO que farei hoje:\n- [tarefa 1]\n- [tarefa 2]\n\nBloqueios:\n- [bloqueio] ou 'Nenhum bloqueio'",
                },
                {
                    "name": "Proposta de Solução",
                    "content": "# Proposta: [título]\n\n## Problema\n[descrição do problema]\n\n## Solução Proposta\n[descrição da solução]\n\n## Benefícios\n- [benefício 1]\n- [benefício 2]\n\n## Riscos\n- [risco 1]\n- [risco 2]\n\n## Próximos Passos\n1. [passo 1]\n2. [passo 2]",
                },
                {
                    "name": "Requisitos de Funcionalidade",
                    "content": "# Requisitos: [nome da funcionalidade]\n\n## Descrição\n[descrição breve]\n\n## Critérios de Aceitação\n- [ ] [critério 1]\n- [ ] [critério 2]\n- [ ] [critério 3]\n\n## Dependências\n- [dependência 1]\n- [dependência 2]\n\n## Estimativa\n[estimativa de tempo]",
                },
            ]

            for template in sample_templates:
                self.save_template(template["name"], template["content"])

            # Create mock files for projects
            self.create_mock_project_files(project_ids)

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error generating test data: {str(e)}")
            return False

    def _clear_test_data(self):
        """Clear existing test data"""
        try:
            with self.conn:
                # Clear projects and related data (cascade will handle related tables)
                self.conn.execute("DELETE FROM projects")

                # Clear contacts and messages
                self.conn.execute("DELETE FROM contacts")

                # Clear templates
                self.conn.execute("DELETE FROM templates")

                self.conn.commit()

        except Exception as e:
            logger.error(f"Error clearing test data: {str(e)}")
            raise

    def add_sample_messages(self, conversation_id, project_id, variant):
        """Add sample messages to a conversation"""
        try:
            messages = []

            # Different conversation flows based on variant
            if variant % 4 == 0:
                # Project planning conversation
                messages = [
                    {
                        "sender": "Você",
                        "content": "Precisamos definir os próximos passos do projeto. Quais são as prioridades?",
                    },
                    {
                        "sender": "Assistente",
                        "content": "Baseado nas informações do projeto, sugiro focarmos nos seguintes pontos:\n\n1. Finalizar a documentação da API\n2. Implementar os testes automatizados\n3. Preparar o ambiente de homologação\n\nQual dessas áreas você gostaria de discutir primeiro?",
                    },
                    {
                        "sender": "Você",
                        "content": "Vamos falar sobre os testes. Como podemos melhorar a cobertura?",
                    },
                    {
                        "sender": "Assistente",
                        "content": "Para melhorar a cobertura de testes, sugiro:\n\n• Implementar testes unitários para todos os componentes principais\n• Adicionar testes de integração para os fluxos críticos\n• Configurar CI/CD para executar testes automaticamente\n• Estabelecer um mínimo de 80% de cobertura\n\nPodemos começar definindo quais são os fluxos mais críticos que precisam ser testados primeiro.",
                    },
                ]
            elif variant % 4 == 1:
                # Technical discussion
                messages = [
                    {
                        "sender": "Você",
                        "content": "Estou com um problema na implementação do sistema de autenticação. O token JWT não está sendo validado corretamente.",
                    },
                    {
                        "sender": "Assistente",
                        "content": "Vamos analisar esse problema. Alguns pontos para verificar:\n\n1. A chave secreta está configurada corretamente nos ambientes?\n2. O formato do token está seguindo o padrão esperado?\n3. As claims obrigatórias estão presentes?\n4. Qual é o erro específico que aparece nos logs?\n\nPoderia compartilhar mais detalhes sobre o erro?",
                    },
                    {
                        "sender": "Você",
                        "content": "O erro é 'invalid signature'. Acredito que pode ser um problema com as chaves.",
                    },
                    {
                        "sender": "Assistente",
                        "content": "O erro 'invalid signature' normalmente ocorre quando:\n\n• A chave usada para verificar o token é diferente da chave usada para gerá-lo\n• O token foi adulterado de alguma forma\n• Está usando algoritmos diferentes na geração e verificação\n\nSugiro verificar se há discrepância entre as chaves dos ambientes e se o algoritmo de assinatura é consistente (RS256, HS256, etc). Também seria útil verificar se o token está sendo transmitido corretamente, sem caracteres sendo perdidos.",
                    },
                ]
            elif variant % 4 == 2:
                # Feature discussion
                messages = [
                    {
                        "sender": "Você",
                        "content": "Estamos pensando em adicionar uma funcionalidade de notificações push no aplicativo. Qual seria a melhor abordagem?",
                    },
                    {
                        "sender": "Assistente",
                        "content": "Para implementar notificações push, você tem algumas opções:\n\n1. **Firebase Cloud Messaging (FCM)** - Solução do Google, funciona bem para Android e iOS\n2. **Amazon SNS** - Serviço da AWS para notificações em múltiplas plataformas\n3. **OneSignal** - Plataforma dedicada a notificações, com plano gratuito generoso\n\nAcredito que FCM seria uma boa escolha se já estiver usando outros serviços do Firebase. Qual é a sua stack atual?",
                    },
                    {
                        "sender": "Você",
                        "content": "Estamos usando Firebase para autenticação, então FCM faz sentido. Existe alguma limitação que deveríamos considerar?",
                    },
                    {
                        "sender": "Assistente",
                        "content": "Ótima escolha considerando que já utilizam Firebase para autenticação. Algumas limitações/considerações:\n\n• **iOS**: Requer configuração adicional com certificados Apple (APNs)\n• **Tamanho**: Limite de 4KB por mensagem\n• **Taxa**: Em casos raros, pode haver throttling para grandes volumes\n• **Persistência**: As mensagens têm TTL (Time To Live) configurável\n\nRecomendo também implementar um sistema de tópicos desde o início para permitir segmentação das notificações. Isso facilitará o envio de notificações para grupos específicos de usuários.",
                    },
                ]
            else:
                # Bug discussion
                messages = [
                    {
                        "sender": "Você",
                        "content": "Identificamos um bug crítico no sistema de pagamentos. O checkout está falhando quando o usuário tem mais de 5 itens no carrinho.",
                    },
                    {
                        "sender": "Assistente",
                        "content": "Isso é preocupante. Para resolver esse bug, precisamos:\n\n1. Verificar os logs de erro para entender exatamente o que está acontecendo\n2. Reproduzir o problema em ambiente de desenvolvimento\n3. Identificar se é um problema de front-end, back-end ou de integração\n\nVocê já tem informações sobre qual componente específico está falhando?",
                    },
                    {
                        "sender": "Você",
                        "content": "Pelos logs, parece ser um problema no cálculo de frete quando há muitos itens. A API está retornando erro 500.",
                    },
                    {
                        "sender": "Assistente",
                        "content": "Baseado nisso, parece ser um problema de backend, possivelmente relacionado ao cálculo de frete. Algumas possíveis causas:\n\n• Erro de lógica no algoritmo de cálculo de frete para múltiplos itens\n• Timeout na comunicação com a API de frete externa\n• Problema de performance ao processar muitos itens\n\nRecomendo:\n1. Verificar a função de cálculo de frete para garantir que ela lida corretamente com mais de 5 itens\n2. Aumentar o timeout da comunicação com serviços externos\n3. Implementar logs detalhados para rastrear o fluxo exato\n4. Adicionar tratamento de erro adequado para evitar que o checkout falhe completamente\n\nGostaria de ajuda para implementar alguma dessas soluções?",
                    },
                ]

            # Insert messages with timestamps
            for i, msg in enumerate(messages):
                # Calculate timestamp with progressive delay
                timestamp_offset = (
                    f"-{random.randint(1, 5)} hours, -{5 * (len(messages) - i)} minutes"
                )

                cursor = self.conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO messages (project_id, conversation_id, sender, content, created_at)
                    VALUES (?, ?, ?, ?, datetime('now', ?))
                """,
                    (
                        project_id,
                        conversation_id,
                        msg["sender"],
                        msg["content"],
                        timestamp_offset,
                    ),
                )

            # Update conversation with last message as preview
            if messages:
                last_message = messages[-1]["content"]
                preview = last_message[:100] + (
                    "..." if len(last_message) > 100 else ""
                )

                cursor = self.conn.cursor()
                cursor.execute(
                    """
                    UPDATE conversations
                    SET preview = ?
                    WHERE id = ?
                """,
                    (preview, conversation_id),
                )

            return True
        except Exception as e:
            print(f"Error adding sample messages: {str(e)}")
            return False

    def create_mock_project_files(self, project_ids):
        """Create mock files for projects"""
        try:
            # Check if project_files table exists
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='project_files'"
            )
            if not cursor.fetchone():
                # Create table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE project_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        filename TEXT NOT NULL,
                        filepath TEXT NOT NULL,
                        size INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                """)
                self.conn.commit()

            # Sample file data
            file_types = [
                {
                    "extension": ".pdf",
                    "names": [
                        "Documentação",
                        "Requisitos",
                        "Manual",
                        "Contrato",
                        "Proposta",
                    ],
                },
                {
                    "extension": ".docx",
                    "names": ["Relatório", "Análise", "Escopo", "Plano", "Estratégia"],
                },
                {
                    "extension": ".txt",
                    "names": ["Notas", "Log", "Changelog", "TODO", "README"],
                },
                {
                    "extension": ".png",
                    "names": [
                        "Screenshot",
                        "Wireframe",
                        "Mockup",
                        "Diagrama",
                        "Fluxograma",
                    ],
                },
                {
                    "extension": ".xlsx",
                    "names": ["Orçamento", "Cronograma", "Dados", "Métricas", "KPIs"],
                },
            ]

            import os

            app_dir = os.path.join(os.path.expanduser("~"), ".ucan", "files")
            os.makedirs(app_dir, exist_ok=True)

            # Add 3-6 files per project
            for project_id in project_ids:
                for _ in range(random.randint(3, 6)):
                    # Choose random file type and name
                    file_type = random.choice(file_types)
                    file_name = (
                        random.choice(file_type["names"]) + file_type["extension"]
                    )

                    # Create a mock filepath
                    import uuid

                    unique_id = str(uuid.uuid4())
                    file_path = os.path.join(app_dir, f"{unique_id}_{file_name}")

                    # Random file size between 10KB and 5MB
                    file_size = random.randint(10 * 1024, 5 * 1024 * 1024)

                    # Insert file record
                    cursor.execute(
                        """
                        INSERT INTO project_files (project_id, filename, filepath, size)
                        VALUES (?, ?, ?, ?)
                    """,
                        (project_id, file_name, file_path, file_size),
                    )

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating mock project files: {str(e)}")
            return False

    def __del__(self):
        """Close database connection"""
        try:
            self.conn.close()
        except:
            pass

    def get_project_messages(self, project_id: int):
        """Get all messages related to a project"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE project_id = ?
                ORDER BY created_at
            """,
                (project_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting project messages: {str(e)}")
            return []

    def add_message_to_project(self, project_id: int, message: dict):
        """Add a message to a project"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (project_id, content, sender, created_at)
                VALUES (?, ?, ?, ?)
            """,
                (
                    project_id,
                    message["content"],
                    message["sender"],
                    message.get("created_at", datetime.datetime.now()),
                ),
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding message to project: {str(e)}")
            return None
