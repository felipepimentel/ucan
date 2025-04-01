import logging
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

    def get_project(self, project_id: int) -> Optional[dict]:
        """Get a project by ID"""
        try:
            cursor = self.conn.execute(
                """
                SELECT * FROM projects WHERE id = ?
            """,
                (project_id,),
            )
            project = cursor.fetchone()

            if not project:
                return None

            # Get project conversations
            cursor = self.conn.execute(
                """
                SELECT * FROM project_conversations
                WHERE project_id = ?
                ORDER BY created_at ASC
            """,
                (project_id,),
            )
            conversations = [dict(row) for row in cursor.fetchall()]

            # Get project files
            cursor = self.conn.execute(
                """
                SELECT * FROM project_files
                WHERE project_id = ?
                ORDER BY created_at ASC
            """,
                (project_id,),
            )
            files = [dict(row) for row in cursor.fetchall()]

            # Convert to dict and add conversations and files
            project_dict = dict(project)
            project_dict["conversations"] = conversations
            project_dict["files"] = files

            return project_dict

        except Exception as e:
            logger.error(f"Error getting project: {str(e)}")
            return None

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

    def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        try:
            with self.conn:
                self.conn.execute(
                    """
                    DELETE FROM projects WHERE id = ?
                """,
                    (project_id,),
                )
                return True

        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return False

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
        """Generate test data for projects and conversations"""
        # Sample projects
        projects = [
            {
                "name": "Projeto E-commerce",
                "description": "Desenvolvimento de uma plataforma de e-commerce com React e Node.js",
                "instructions": "Desenvolver uma plataforma moderna e responsiva usando React no frontend e Node.js no backend.",
                "conversations": [
                    {
                        "sender": "Você",
                        "content": "Preciso começar o desenvolvimento do e-commerce. Por onde sugere começar?",
                    },
                    {
                        "sender": "Assistente IA",
                        "content": "Sugiro começarmos pelo planejamento da arquitetura. Vamos usar:\n\n1. React + Vite para o frontend\n2. Node.js + Express para o backend\n3. PostgreSQL para o banco de dados\n\nQuer que eu crie a estrutura inicial do projeto?",
                    },
                    {
                        "sender": "Você",
                        "content": "Sim, por favor! Comece pelo frontend.",
                    },
                ],
            },
            {
                "name": "API REST Documentation",
                "description": "Documentação completa da API REST do sistema de pagamentos",
                "instructions": "Criar documentação detalhada de todos os endpoints da API de pagamentos usando OpenAPI/Swagger.",
                "conversations": [
                    {
                        "sender": "Você",
                        "content": "Preciso documentar todos os endpoints da API de pagamentos.",
                    },
                    {
                        "sender": "Assistente IA",
                        "content": "Vou ajudar você a criar a documentação usando OpenAPI 3.0. Primeiro, vamos listar todos os endpoints principais:\n\n1. POST /payments\n2. GET /payments/{id}\n3. PUT /payments/{id}/status\n\nQuer que eu crie um template inicial?",
                    },
                ],
            },
            {
                "name": "Bug Tracking System",
                "description": "Sistema de rastreamento de bugs e issues para equipe de desenvolvimento",
                "instructions": "Desenvolver um sistema interno para gerenciamento de bugs e issues usando Python e Django.",
                "conversations": [
                    {
                        "sender": "Você",
                        "content": "Como podemos estruturar o modelo de dados para o sistema de bugs?",
                    },
                    {
                        "sender": "Assistente IA",
                        "content": "Para o sistema de bugs, sugiro a seguinte estrutura de modelos:\n\n1. Bug\n   - título\n   - descrição\n   - status\n   - prioridade\n   - assignee\n\n2. Comment\n   - conteúdo\n   - autor\n   - timestamp\n\n3. Project\n   - nome\n   - descrição\n   - membros\n\nQuer que eu crie os modelos em Django?",
                    },
                    {
                        "sender": "Você",
                        "content": "Sim, pode criar os modelos por favor.",
                    },
                ],
            },
            {
                "name": "ML Image Classifier",
                "description": "Classificador de imagens usando machine learning com TensorFlow",
                "instructions": "Desenvolver um modelo de ML para classificação de imagens de produtos.",
                "conversations": [
                    {
                        "sender": "Você",
                        "content": "Qual seria a melhor arquitetura para classificar imagens de produtos?",
                    },
                    {
                        "sender": "Assistente IA",
                        "content": "Para classificação de imagens de produtos, recomendo usar:\n\n1. Transfer Learning com ResNet50 ou EfficientNet\n2. Fine-tuning nas últimas camadas\n3. Data augmentation para melhorar generalização\n\nQuer que eu mostre um exemplo de implementação?",
                    },
                ],
            },
            {
                "name": "DevOps Pipeline",
                "description": "Configuração de pipeline CI/CD usando GitHub Actions",
                "instructions": "Implementar pipeline completo de CI/CD com testes, build e deploy automático.",
                "conversations": [
                    {
                        "sender": "Você",
                        "content": "Preciso configurar um pipeline CI/CD para um projeto React.",
                    },
                    {
                        "sender": "Assistente IA",
                        "content": "Vou ajudar você a criar um workflow do GitHub Actions. O pipeline terá:\n\n1. Install dependencies\n2. Run tests\n3. Build\n4. Deploy to staging/production\n\nQuer que eu crie o arquivo yaml de configuração?",
                    },
                    {
                        "sender": "Você",
                        "content": "Sim, pode criar o arquivo de configuração.",
                    },
                ],
            },
        ]

        # Insert projects and conversations
        for project in projects:
            conversations = project.pop("conversations")
            project_id = self.save_project(
                name=project["name"],
                description=project["description"],
                instructions=project["instructions"],
            )

            for conv in conversations:
                self.save_conversation(project_id, conv["sender"], conv["content"])

        # Sample templates
        templates = [
            {
                "name": "Code Review Request",
                "content": "Poderia fazer uma revisão de código do seguinte trecho?\n\n```\n[Cole seu código aqui]\n```\n\nPrincipais pontos a serem avaliados:\n1. Performance\n2. Boas práticas\n3. Segurança",
            },
            {
                "name": "Bug Report",
                "content": "Encontrei um bug no sistema:\n\nDescrição:\n[Descreva o bug]\n\nPassos para reproduzir:\n1.\n2.\n3.\n\nComportamento esperado:\n[Descreva]\n\nComportamento atual:\n[Descreva]",
            },
            {
                "name": "Feature Request",
                "content": "Gostaria de sugerir uma nova feature:\n\nDescrição:\n[Descreva a feature]\n\nCaso de uso:\n[Explique quando/como seria usada]\n\nBenefícios:\n[Liste os benefícios]",
            },
        ]

        # Insert templates
        for template in templates:
            self.save_template(template["name"], template["content"])

    def __del__(self):
        """Close database connection"""
        try:
            self.conn.close()
        except:
            pass
