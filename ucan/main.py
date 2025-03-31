import datetime
import functools
import json
import logging
import os
import sqlite3
import sys
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageTk

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ucan.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("UCAN")


# Verifica e instala dependências automaticamente se necessário
def check_dependencies():
    try:
        import customtkinter
    except ImportError:
        print("Instalando dependências necessárias...")
        import subprocess

        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "customtkinter",
            "pillow",
        ])
        print("Dependências instaladas com sucesso!")


# Executa verificação de dependências
check_dependencies()

# Configuração do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Definir algumas cores e estilos consistentes para a aplicação
COLORS = {
    "primary": "#1E88E5",
    "primary_hover": "#1976D2",
    "secondary": "#78909C",
    "success": "#43A047",
    "danger": "#E53935",
    "warning": "#FFB300",
    "background_light": "#F5F5F5",
    "background_dark": "#2D2D2D",
    "text_light": "#212121",
    "text_dark": "#EEEEEE",
}

# Constantes de estilo
TEXT_STYLES = {
    "h1": {"size": 24, "weight": "bold"},
    "h2": {"size": 20, "weight": "bold"},
    "subtitle": {"size": 16, "weight": "normal"},
    "body": {"size": 14, "weight": "normal"},
    "small": {"size": 12, "weight": "normal"},
}

LAYOUT = {
    "padding": {
        "small": 5,
        "medium": 10,
        "large": 20,
    },
    "border_radius": {
        "small": 5,
        "medium": 10,
        "large": 15,
    },
}

BUTTON_STYLES = {
    "default": {
        "font": ("Arial", 14),
        "corner_radius": 8,
    },
    "outline": {
        "font": ("Arial", 14),
        "corner_radius": 8,
        "border_width": 2,
    },
}


class ScrollableMessageFrame(ctk.CTkScrollableFrame):
    """Frame rolável customizado para exibir as mensagens do chat"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.message_widgets = []  # Lista para rastrear widgets de mensagem
        self.current_row = 0  # Contador de linha atual

    def add_widget(self, widget):
        """Adiciona um widget ao frame e o rastreia"""
        widget.grid(row=self.current_row, column=0, sticky="ew", padx=10, pady=5)
        self.message_widgets.append(widget)
        self.current_row += 1

        # Rolar para a última mensagem
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1.0)

    def clear_widgets(self):
        """Remove todos os widgets do frame"""
        for widget in self.message_widgets:
            widget.destroy()
        self.message_widgets = []
        self.current_row = 0


class EmojiSelector(ctk.CTkToplevel):
    """Seletor de emojis flutuante"""

    def __init__(self, master, input_widget):
        super().__init__(master)
        self.input_widget = input_widget
        self.title("Emojis")
        self.geometry("320x240")
        self.resizable(False, False)

        # Emojis organizados por categoria
        self.emoji_categories = {
            "Rostos": [
                "😊",
                "😂",
                "😍",
                "🥰",
                "😎",
                "🤔",
                "😁",
                "😉",
                "😢",
                "😭",
                "😡",
                "🥺",
                "😴",
                "🤮",
                "🤒",
                "😷",
            ],
            "Gestos": [
                "👍",
                "👎",
                "👌",
                "✌️",
                "🤘",
                "👏",
                "🙌",
                "🤝",
                "💪",
                "🙏",
                "👆",
                "👉",
                "👈",
                "✋",
            ],
            "Objetos": [
                "💻",
                "📱",
                "💡",
                "🔥",
                "⭐",
                "💯",
                "🎉",
                "🎁",
                "🎮",
                "🏆",
                "💰",
                "🔒",
                "⏰",
                "📷",
            ],
            "Símbolos": [
                "❤️",
                "💙",
                "💚",
                "💛",
                "💜",
                "💔",
                "✅",
                "❌",
                "⚠️",
                "🚫",
                "♻️",
                "🔄",
                "➕",
                "➖",
            ],
        }

        # Criar abas para categorias
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)

        # Adicionar uma aba para cada categoria
        for category in self.emoji_categories:
            tab = self.tab_view.add(category)
            tab.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

            # Adicionar emojis à aba
            emojis = self.emoji_categories[category]
            row, col = 0, 0
            for emoji in emojis:
                emoji_btn = ctk.CTkButton(
                    tab,
                    text=emoji,
                    width=35,
                    height=35,
                    command=lambda e=emoji: self.add_emoji(e),
                    font=ctk.CTkFont(size=16),
                )
                emoji_btn.grid(row=row, column=col, padx=2, pady=2)
                col += 1
                if col > 7:  # 8 emojis por linha
                    col = 0
                    row += 1

    def add_emoji(self, emoji):
        """Adiciona o emoji selecionado ao campo de input"""
        current_text = self.input_widget.get("1.0", "end-1c")
        self.input_widget.delete("1.0", "end")
        self.input_widget.insert("1.0", current_text + emoji)
        self.destroy()  # Fecha a janela após a seleção


class ProfileSettings(ctk.CTkToplevel):
    """Janela de configurações de perfil"""

    def __init__(self, parent, current_contact, save_callback):
        super().__init__(parent)
        self.title("Configurações")
        self.save_callback = save_callback
        self.current_contact = current_contact

        # Configuração da janela
        self.geometry("400x500")
        self.resizable(False, False)

        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Configurações de Perfil",
            font=ctk.CTkFont(**TEXT_STYLES["h1"]),
        )
        self.title_label.pack(pady=10)

        # Campo de nome de usuário
        self.username_label = ctk.CTkLabel(
            self.main_frame,
            text="Nome de usuário:",
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
        )
        self.username_label.pack(pady=5)
        self.username_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Digite seu nome de usuário",
            width=300,
        )
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, self.current_contact)

        # Campo de status
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Status:",
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
        )
        self.status_label.pack(pady=5)
        self.status_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Digite seu status",
            width=300,
        )
        self.status_entry.pack(pady=5)

        # Campo de avatar (URL)
        self.avatar_label = ctk.CTkLabel(
            self.main_frame,
            text="URL do Avatar:",
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
        )
        self.avatar_label.pack(pady=5)
        self.avatar_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Cole a URL do seu avatar",
            width=300,
        )
        self.avatar_entry.pack(pady=5)

        # Configurações de notificação
        self.notifications_var = ctk.BooleanVar(value=True)
        self.notifications_switch = ctk.CTkSwitch(
            self.main_frame,
            text="Notificações",
            variable=self.notifications_var,
        )
        self.notifications_switch.pack(pady=10)

        # Configurações de som
        self.sound_var = ctk.BooleanVar(value=True)
        self.sound_switch = ctk.CTkSwitch(
            self.main_frame,
            text="Som",
            variable=self.sound_var,
        )
        self.sound_switch.pack(pady=10)

        # Botões
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20)

        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Salvar",
            command=self.save_settings,
        )
        self.save_button.pack(side="left", padx=10)

        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancelar",
            command=self.destroy,
        )
        self.cancel_button.pack(side="left", padx=10)

    def save_settings(self):
        """Salva as configurações"""
        profile_data = {
            "username": self.username_entry.get(),
            "status": self.status_entry.get(),
            "avatar": self.avatar_entry.get(),
            "notifications": self.notifications_var.get(),
            "sound": self.sound_var.get(),
        }
        self.save_callback(profile_data)
        self.destroy()


class MessageBubble(ctk.CTkFrame):
    """Bolha de mensagem personalizada com suporte a reações e opções"""

    def __init__(self, master, sender, message, timestamp, is_user, **kwargs):
        self.main_app = kwargs.pop("main_app", None)
        super().__init__(
            master,
            corner_radius=LAYOUT["border_radius"]["large"],
            fg_color=kwargs.pop(
                "fg_color", ("gray90", "gray20") if is_user else ("gray85", "gray25")
            ),
            **kwargs,
        )

        self.sender = sender
        self.message_text = message
        self.timestamp = timestamp
        self.is_user = is_user
        self.reactions = {}

        self.setup_ui()

    def setup_ui(self):
        """Configura a interface da bolha de mensagem"""
        self.grid_columnconfigure(0, weight=1)

        # Cabeçalho com avatar e nome
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT["padding"]["medium"],
            pady=(LAYOUT["padding"]["small"], 0),
        )

        # Avatar (placeholder circular)
        self.avatar_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            width=30,
            height=30,
        )
        self.avatar_label.pack(side="left", padx=(0, LAYOUT["padding"]["small"]))
        self.update_avatar()

        # Nome do remetente
        self.sender_label = ctk.CTkLabel(
            self.header_frame,
            text=self.sender,
            font=ctk.CTkFont(**TEXT_STYLES["subtitle"]),
            text_color=COLORS["primary"] if self.is_user else ("gray40", "gray70"),
        )
        self.sender_label.pack(side="left", fill="x", expand=True, anchor="w")

        # Timestamp
        self.time_label = ctk.CTkLabel(
            self.header_frame,
            text=self.format_timestamp(),
            font=ctk.CTkFont(**TEXT_STYLES["small"]),
            text_color=("gray40", "gray70"),
        )
        self.time_label.pack(side="right")

        # Conteúdo da mensagem
        self.message_label = ctk.CTkLabel(
            self,
            text=self.message_text,
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
            wraplength=400,
            justify="left",
            anchor="w",
        )
        self.message_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=LAYOUT["padding"]["medium"],
            pady=(LAYOUT["padding"]["small"], LAYOUT["padding"]["medium"]),
        )

        # Opções da mensagem (aparecem ao passar o mouse)
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.grid(
            row=2,
            column=0,
            sticky="e",
            padx=LAYOUT["padding"]["medium"],
            pady=(0, LAYOUT["padding"]["small"]),
        )

        # Botão de reação
        self.react_button = ctk.CTkButton(
            self.options_frame,
            text="😊",
            width=30,
            height=30,
            command=self.show_reaction_selector,
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
            **BUTTON_STYLES["outline"],
        )
        self.react_button.pack(side="left", padx=2)

        # Botão de responder
        self.reply_button = ctk.CTkButton(
            self.options_frame,
            text="↩️",
            width=30,
            height=30,
            command=self.reply_to_message,
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
            **BUTTON_STYLES["outline"],
        )
        self.reply_button.pack(side="left", padx=2)

        # Área de reações
        self.reactions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.reactions_frame.grid(
            row=3,
            column=0,
            sticky="w",
            padx=LAYOUT["padding"]["medium"],
            pady=(0, LAYOUT["padding"]["small"]),
        )
        self.update_reactions_display()

    def update_avatar(self):
        """Atualiza o avatar do remetente"""
        # Cria um círculo colorido como avatar
        size = 30
        img = Image.new(
            "RGB",
            (size, size),
            color=(100, 149, 237) if self.is_user else (149, 165, 166),
        )

        # Desenha um círculo
        draw = ImageDraw.Draw(img)
        draw.ellipse(
            (0, 0, size, size), fill=(65, 105, 225) if self.is_user else (127, 140, 141)
        )

        # Adiciona iniciais
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()

        initials = self.sender[0].upper() if self.sender else "U"
        text_width, text_height = (
            draw.textsize(initials, font=font)
            if hasattr(draw, "textsize")
            else (10, 10)
        )
        position = ((size - text_width) // 2, (size - text_height) // 2)
        draw.text(position, initials, fill=(255, 255, 255), font=font)

        # Converter para o formato CTk
        self.avatar_img = ImageTk.PhotoImage(img)
        self.avatar_label.configure(image=self.avatar_img)

    def format_timestamp(self):
        """Formata o timestamp para exibição"""
        try:
            dt = datetime.fromisoformat(self.timestamp)
            return dt.strftime("%H:%M")
        except:
            return self.timestamp

    def add_reaction(self, emoji):
        """Adiciona uma reação à mensagem"""
        if emoji in self.reactions:
            self.reactions[emoji] += 1
        else:
            self.reactions[emoji] = 1
        self.update_reactions_display()

    def update_reactions_display(self):
        """Atualiza a exibição de reações"""
        # Limpa o frame de reações
        for widget in self.reactions_frame.winfo_children():
            widget.destroy()

        # Adiciona as reações existentes
        for emoji, count in self.reactions.items():
            reaction_button = ctk.CTkButton(
                self.reactions_frame,
                text=f"{emoji} {count}",
                width=45,
                height=25,
                font=ctk.CTkFont(**TEXT_STYLES["small"]),
                **BUTTON_STYLES["outline"],
                command=lambda e=emoji: self.add_reaction(e),
            )
            reaction_button.pack(side="left", padx=2, pady=2)

    def show_reaction_selector(self):
        """Mostra o seletor de reações"""
        selector = ReactionSelector(self, self.add_reaction)
        selector.focus()

    def reply_to_message(self):
        """Define esta mensagem como a mensagem sendo respondida"""
        if self.main_app:
            self.main_app.set_reply_to(self.sender, self.message_text)


class ReactionSelector(ctk.CTkToplevel):
    """Seletor de reações para mensagens"""

    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Adicionar Reação")
        self.geometry("300x150")
        self.resizable(False, False)

        self.callback = callback

        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # Emojis comuns para reações
        self.reactions = [
            "👍",
            "❤️",
            "😂",
            "😮",
            "😢",
            "👏",
            "🔥",
            "🎉",
            "🤔",
            "👀",
            "💯",
            "✅",
        ]

        # Criar botões de reação
        row, col = 0, 0
        for reaction in self.reactions:
            reaction_btn = ctk.CTkButton(
                self,
                text=reaction,
                width=40,
                height=40,
                command=lambda r=reaction: self.select_reaction(r),
                font=ctk.CTkFont(size=20),
            )
            reaction_btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 5:
                col = 0
                row += 1

    def select_reaction(self, reaction):
        """Seleciona uma reação e fecha o seletor"""
        self.callback(reaction)
        self.destroy()


class LoadingScreen(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("UCAN")
        self.geometry("300x200")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Loading text
        self.loading_label = ctk.CTkLabel(
            self, text="Carregando UCAN...", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.loading_label.pack(pady=(40, 20))

        # Progress bar
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=20, padx=40, fill="x")
        self.progress.set(0)

        # Status text
        self.status_label = ctk.CTkLabel(
            self, text="Inicializando...", font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)

        # Start loading animation
        self.loading_steps = [
            "Carregando configurações...",
            "Inicializando interface...",
            "Preparando chat...",
            "Pronto!",
        ]
        self.current_step = 0
        self.animate_loading()

    def animate_loading(self):
        if self.current_step < len(self.loading_steps):
            self.status_label.configure(text=self.loading_steps[self.current_step])
            self.progress.set((self.current_step + 1) / len(self.loading_steps))
            self.current_step += 1
            self.after(500, self.animate_loading)
        else:
            self.destroy()


class Contact:
    def __init__(self, name, status):
        self.name = name
        self.status = status

    def create_frame(self, master, on_click):
        frame = ctk.CTkFrame(
            master,
            corner_radius=LAYOUT["border_radius"]["small"],
        )
        frame.grid(sticky="ew", padx=LAYOUT["padding"]["small"], pady=2)
        frame.grid_columnconfigure(1, weight=1)

        # Avatar
        avatar = ctk.CTkLabel(
            frame,
            text=self.name[0],
            width=40,
            height=40,
            font=ctk.CTkFont(**TEXT_STYLES["h2"]),
        )
        avatar.grid(
            row=0,
            column=0,
            padx=LAYOUT["padding"]["small"],
            pady=LAYOUT["padding"]["small"],
        )

        # Nome
        name_label = ctk.CTkLabel(
            frame,
            text=self.name,
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
        )
        name_label.grid(
            row=0,
            column=1,
            padx=LAYOUT["padding"]["small"],
            pady=LAYOUT["padding"]["small"],
            sticky="w",
        )

        # Status
        status_color = (
            COLORS["success"] if self.status == "online" else COLORS["secondary"]
        )
        status_label = ctk.CTkLabel(
            frame,
            text=self.status,
            font=ctk.CTkFont(**TEXT_STYLES["small"]),
            text_color=status_color,
        )
        status_label.grid(
            row=0,
            column=2,
            padx=LAYOUT["padding"]["small"],
            pady=LAYOUT["padding"]["small"],
        )

        # Bind click
        frame.bind("<Button-1>", lambda e: on_click(self.name, self.status))
        return frame


class CallbackManager:
    """Gerenciador de callbacks para evitar problemas com o garbage collector"""

    def __init__(self, app):
        self.app = app
        self.callbacks = {}

    def create_contact_callback(self, name, status):
        """Cria um callback para o clique em um contato"""
        key = f"contact_{name}_{status}"
        if key not in self.callbacks:
            self.callbacks[key] = lambda e: self.app.start_chat(name, status)
        return self.callbacks[key]

    def create_welcome_callback(self, contact_name):
        """Cria um callback para a mensagem de boas-vindas"""
        key = f"welcome_{contact_name}"
        if key not in self.callbacks:
            self.callbacks[key] = lambda: self.app.add_message(
                f"Olá! Bem-vindo ao chat com {contact_name}!", contact_name
            )
        return self.callbacks[key]

    def create_bot_response_callback(self):
        """Cria um callback para a resposta do bot"""
        key = "bot_response"
        if key not in self.callbacks:
            self.callbacks[key] = lambda: self.app._simulate_bot_response()
        return self.callbacks[key]


class Database:
    def __init__(self):
        self.db_path = "ucan.db"
        self.init_db()

    def init_db(self):
        """Inicializa o banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabela de usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    status TEXT,
                    avatar TEXT,
                    notifications BOOLEAN DEFAULT 1,
                    sound BOOLEAN DEFAULT 1
                )
            """)

            # Tabela de mensagens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    receiver TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT 0
                )
            """)

            conn.commit()
            conn.close()
            logger.info("Banco de dados inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            raise

    def save_message(self, sender, receiver, content):
        """Salva uma mensagem no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO messages (sender, receiver, content, timestamp)
                VALUES (?, ?, ?, ?)
            """,
                (sender, receiver, content, datetime.now().isoformat()),
            )

            conn.commit()
            conn.close()
            logger.info(f"Mensagem salva: {sender} -> {receiver}")
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {str(e)}")
            raise

    def get_messages(self, user1, user2, limit=50):
        """Recupera mensagens entre dois usuários"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT sender, content, timestamp
                FROM messages
                WHERE (sender = ? AND receiver = ?)
                   OR (sender = ? AND receiver = ?)
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (user1, user2, user2, user1, limit),
            )

            messages = cursor.fetchall()
            conn.close()
            return messages
        except Exception as e:
            logger.error(f"Erro ao recuperar mensagens: {str(e)}")
            raise

    def save_profile(self, username, status, avatar, notifications, sound):
        """Salva ou atualiza o perfil do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO users 
                (username, status, avatar, notifications, sound)
                VALUES (?, ?, ?, ?, ?)
            """,
                (username, status, avatar, notifications, sound),
            )

            conn.commit()
            conn.close()
            logger.info(f"Perfil salvo: {username}")
        except Exception as e:
            logger.error(f"Erro ao salvar perfil: {str(e)}")
            raise

    def get_profile(self, username):
        """Recupera o perfil do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT username, status, avatar, notifications, sound
                FROM users
                WHERE username = ?
            """,
                (username,),
            )

            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao recuperar perfil: {str(e)}")
            raise


class ThemeManager:
    def __init__(self):
        self.themes = {
            "dark": {
                "primary": "#1E88E5",
                "primary_hover": "#1976D2",
                "secondary": "#78909C",
                "success": "#43A047",
                "danger": "#E53935",
                "warning": "#FFB300",
                "background": "#2D2D2D",
                "surface": "#3D3D3D",
                "text": "#EEEEEE",
                "text_secondary": "#BDBDBD",
            },
            "light": {
                "primary": "#2196F3",
                "primary_hover": "#1976D2",
                "secondary": "#78909C",
                "success": "#4CAF50",
                "danger": "#F44336",
                "warning": "#FFC107",
                "background": "#F5F5F5",
                "surface": "#FFFFFF",
                "text": "#212121",
                "text_secondary": "#757575",
            },
            "blue": {
                "primary": "#1976D2",
                "primary_hover": "#1565C0",
                "secondary": "#78909C",
                "success": "#43A047",
                "danger": "#E53935",
                "warning": "#FFB300",
                "background": "#1A237E",
                "surface": "#283593",
                "text": "#FFFFFF",
                "text_secondary": "#B3E5FC",
            },
        }
        self.current_theme = "dark"
        self.load_theme()

    def load_theme(self):
        """Carrega o tema salvo"""
        try:
            if os.path.exists("theme.json"):
                with open("theme.json", "r") as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", "dark")
        except Exception as e:
            logger.error(f"Erro ao carregar tema: {str(e)}")

    def save_theme(self):
        """Salva o tema atual"""
        try:
            with open("theme.json", "w") as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            logger.error(f"Erro ao salvar tema: {str(e)}")

    def get_theme(self):
        """Retorna o tema atual"""
        return self.themes[self.current_theme]

    def set_theme(self, theme_name):
        """Define o tema atual"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.save_theme()
            return True
        return False


class ChatApp(ctk.CTk):
    def __init__(self):
        try:
            super().__init__()
            logger.info("Iniciando aplicação UCAN")

            # Inicializa banco de dados
            self.db = Database()

            # Inicializa gerenciador de temas
            self.theme_manager = ThemeManager()

            # Configurações de notificação
            self.notifications_enabled = True
            self.sound_enabled = True

            # Configuração da janela
            self.title("UCAN Chat")
            self.geometry("1200x800")
            self.minsize(800, 600)

            # Configuração do grid
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # Configuração da sidebar
            self.setup_sidebar()

            # Configuração da área principal
            self.setup_main_area()

            # Configuração do chat
            self.setup_chat()

            # Centralizar janela
            self.center_window()

            logger.info("Aplicação inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar aplicação: {str(e)}")
            messagebox.showerror(
                "Erro",
                "Não foi possível inicializar a aplicação. Verifique o arquivo de log para mais detalhes.",
            )
            sys.exit(1)

    def _handle_contact_click(self, name, status, event=None):
        """Manipula o clique em um contato"""
        self.start_chat(name, status)

    def _send_welcome_message(self, contact_name):
        """Envia uma mensagem de boas-vindas"""
        self.add_message(f"Olá! Bem-vindo ao chat com {contact_name}!", contact_name)

    def populate_contacts(self):
        """Popula a lista de contatos"""
        # Lista de contatos de exemplo
        contacts = [
            ("João", "online"),
            ("Maria", "offline"),
            ("Pedro", "online"),
            ("Ana", "offline"),
            ("Carlos", "online"),
            ("Julia", "offline"),
        ]

        for name, status in contacts:
            contact_frame = ctk.CTkFrame(
                self.contacts_frame,
                corner_radius=LAYOUT["border_radius"]["small"],
            )
            contact_frame.grid(sticky="ew", padx=LAYOUT["padding"]["small"], pady=2)
            contact_frame.grid_columnconfigure(1, weight=1)

            # Avatar
            avatar = ctk.CTkLabel(
                contact_frame,
                text=name[0],
                width=40,
                height=40,
                font=ctk.CTkFont(**TEXT_STYLES["h2"]),
            )
            avatar.grid(
                row=0,
                column=0,
                padx=LAYOUT["padding"]["small"],
                pady=LAYOUT["padding"]["small"],
            )

            # Nome
            name_label = ctk.CTkLabel(
                contact_frame,
                text=name,
                font=ctk.CTkFont(**TEXT_STYLES["body"]),
            )
            name_label.grid(
                row=0,
                column=1,
                padx=LAYOUT["padding"]["small"],
                pady=LAYOUT["padding"]["small"],
                sticky="w",
            )

            # Status
            status_color = (
                COLORS["success"] if status == "online" else COLORS["secondary"]
            )
            status_label = ctk.CTkLabel(
                contact_frame,
                text=status,
                font=ctk.CTkFont(**TEXT_STYLES["small"]),
                text_color=status_color,
            )
            status_label.grid(
                row=0,
                column=2,
                padx=LAYOUT["padding"]["small"],
                pady=LAYOUT["padding"]["small"],
            )

            # Bind click usando functools.partial
            callback = functools.partial(self._handle_contact_click, name, status)
            contact_frame.bind("<Button-1>", callback)

    def start_chat(self, contact_name, status):
        """Inicia uma conversa com um contato"""
        try:
            self.current_contact = contact_name
            self.contact_name.configure(text=contact_name)
            self.contact_status.configure(text=status)
            self.messages_frame.clear_widgets()
            self.title(f"UCAN Chat - {contact_name}")

            # Carrega histórico de mensagens
            messages = self.db.get_messages("Você", contact_name)
            for sender, content, timestamp in reversed(messages):
                self.add_message(content, sender, timestamp)

            # Simula uma mensagem de boas-vindas após 500ms
            welcome_callback = functools.partial(
                self._send_welcome_message, contact_name
            )
            self.after(500, welcome_callback)
        except Exception as e:
            logger.error(f"Erro ao iniciar chat: {str(e)}")
            messagebox.showerror(
                "Erro", "Não foi possível iniciar o chat. Tente novamente."
            )

    def send_message(self):
        """Envia uma mensagem"""
        try:
            message = self.message_entry.get("1.0", "end-1c").strip()
            if not message:
                return

            # Adiciona mensagem
            self.add_message(message, "Você")
            logger.info(f"Mensagem enviada: {message}")

            # Salva mensagem no banco de dados
            self.db.save_message("Você", self.current_contact, message)

            # Limpa campo
            self.message_entry.delete("1.0", "end")

            # Simula resposta do bot após 1 segundo
            self.after(1000, self._simulate_bot_response)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            messagebox.showerror(
                "Erro", "Não foi possível enviar a mensagem. Tente novamente."
            )

    def setup_sidebar(self):
        """Configura a barra lateral"""
        # Frame da sidebar
        self.sidebar = ctk.CTkFrame(
            self, width=250, corner_radius=LAYOUT["border_radius"]["medium"]
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["medium"],
        )
        self.sidebar.grid_rowconfigure(1, weight=1)

        # Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="UCAN",
            font=ctk.CTkFont(**TEXT_STYLES["h1"]),
            text_color=COLORS["primary"],
        )
        self.logo_label.grid(
            row=0,
            column=0,
            padx=LAYOUT["padding"]["large"],
            pady=LAYOUT["padding"]["large"],
        )

        # Lista de contatos
        self.contacts_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            corner_radius=LAYOUT["border_radius"]["small"],
        )
        self.contacts_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["medium"],
        )
        self.contacts_frame.grid_columnconfigure(0, weight=1)

        # Botões de ação
        self.settings_button = ctk.CTkButton(
            self.sidebar,
            text="Configurações",
            command=self.open_settings,
            **BUTTON_STYLES["outline"],
        )
        self.settings_button.grid(
            row=2,
            column=0,
            padx=LAYOUT["padding"]["large"],
            pady=LAYOUT["padding"]["medium"],
        )

        # Adiciona seletor de tema
        self.theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.theme_frame.grid(
            row=3,
            column=0,
            padx=LAYOUT["padding"]["large"],
            pady=LAYOUT["padding"]["medium"],
        )

        self.theme_label = ctk.CTkLabel(
            self.theme_frame,
            text="Tema:",
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
        )
        self.theme_label.pack(side="left", padx=LAYOUT["padding"]["small"])

        self.theme_var = ctk.StringVar(value=self.theme_manager.current_theme)
        self.theme_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            values=list(self.theme_manager.themes.keys()),
            variable=self.theme_var,
            command=self.change_theme,
        )
        self.theme_menu.pack(side="left", padx=LAYOUT["padding"]["small"])

        # Populando contatos
        self.populate_contacts()

    def setup_main_area(self):
        """Configura a área principal"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self, corner_radius=LAYOUT["border_radius"]["medium"]
        )
        self.main_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["medium"],
        )
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Barra superior
        self.top_bar = ctk.CTkFrame(
            self.main_frame, corner_radius=LAYOUT["border_radius"]["small"]
        )
        self.top_bar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["small"],
        )
        self.top_bar.grid_columnconfigure(0, weight=1)

        # Nome do contato
        self.contact_name = ctk.CTkLabel(
            self.top_bar,
            text="Selecione um contato",
            font=ctk.CTkFont(**TEXT_STYLES["h2"]),
        )
        self.contact_name.grid(
            row=0,
            column=0,
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["small"],
        )

        # Status do contato
        self.contact_status = ctk.CTkLabel(
            self.top_bar,
            text="Status: Offline",
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
        )
        self.contact_status.grid(
            row=0,
            column=1,
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["small"],
        )

    def setup_chat(self):
        """Configura a área de chat"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        # Top bar
        self.top_bar = ctk.CTkFrame(self.main_frame)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        # Nome do contato
        self.contact_name = ctk.CTkLabel(
            self.top_bar,
            text="Selecione um contato",
            font=ctk.CTkFont(**TEXT_STYLES["h2"]),
        )
        self.contact_name.grid(row=0, column=0, padx=10)

        # Status do contato
        self.contact_status = ctk.CTkLabel(
            self.top_bar,
            text="Status: Offline",
            font=ctk.CTkFont(**TEXT_STYLES["body"]),
        )
        self.contact_status.grid(row=0, column=1, padx=10)

        # Frame de mensagens
        self.messages_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.messages_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Frame de entrada
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # Botão de emoji
        self.emoji_button = ctk.CTkButton(
            self.input_frame,
            text="😊",
            width=40,
            command=self.show_emoji_selector,
        )
        self.emoji_button.grid(row=0, column=0, padx=5)

        # Campo de entrada
        self.message_entry = ctk.CTkTextbox(
            self.input_frame,
            height=40,
            wrap="word",
        )
        self.message_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.message_entry.bind("<Return>", self.handle_enter)

        # Botão de enviar
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Enviar",
            width=100,
            command=lambda: self.send_message(),
        )
        self.send_button.grid(row=0, column=2, padx=5)

        # Configurar pesos das colunas e linhas
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.top_bar.grid_columnconfigure(1, weight=1)

    def open_settings(self):
        """Abre a janela de configurações"""
        settings = ProfileSettings(self, self.current_contact, self.save_profile)
        settings.grab_set()

    def save_profile(self, profile_data):
        """Salva as configurações de perfil"""
        try:
            # Atualiza configurações de notificação
            self.notifications_enabled = profile_data["notifications"]
            self.sound_enabled = profile_data["sound"]

            # Salva no banco de dados
            self.db.save_profile(
                profile_data["username"],
                profile_data["status"],
                profile_data["avatar"],
                self.notifications_enabled,
                self.sound_enabled,
            )
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao salvar perfil: {str(e)}")
            messagebox.showerror(
                "Erro", "Não foi possível salvar as configurações. Tente novamente."
            )

    def change_theme(self, theme_name):
        """Altera o tema da aplicação"""
        if theme_name in self.theme_manager.themes:
            self.theme_manager.set_theme(theme_name)
            self.update_widget_colors()

    def update_widget_colors(self):
        """Atualiza as cores dos widgets com base no tema atual"""
        theme = self.theme_manager.get_theme()

        # Atualiza cores do frame principal
        self.configure(fg_color=theme["bg_primary"])

        # Atualiza cores da sidebar
        if hasattr(self, "sidebar_frame"):
            self.sidebar_frame.configure(fg_color=theme["bg_secondary"])

        # Atualiza cores do frame de mensagens
        if hasattr(self, "messages_frame"):
            self.messages_frame.configure(fg_color=theme["bg_primary"])

        # Atualiza cores do frame de entrada
        if hasattr(self, "input_frame"):
            self.input_frame.configure(fg_color=theme["bg_secondary"])
            self.message_entry.configure(
                fg_color=theme["bg_input"], text_color=theme["text_primary"]
            )

        # Atualiza cores dos botões
        if hasattr(self, "send_button"):
            self.send_button.configure(
                fg_color=theme["button_primary"], hover_color=theme["button_hover"]
            )

        if hasattr(self, "emoji_button"):
            self.emoji_button.configure(
                fg_color=theme["button_secondary"], hover_color=theme["button_hover"]
            )

    def handle_enter(self, event):
        """Manipula o evento de pressionar Enter"""
        if not event.state & 0x1:  # Shift não está pressionado
            self.send_message()
            return "break"  # Previne a quebra de linha

    def show_emoji_selector(self):
        """Mostra o seletor de emojis"""
        selector = EmojiSelector(self, self.message_entry)
        selector.grab_set()

    def center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """Função principal"""
    # Inicia aplicação
    app = ChatApp()

    # Mostra tela de carregamento
    loading = LoadingScreen(app)

    # Inicia o loop principal
    app.mainloop()


if __name__ == "__main__":
    main()

__all__ = ["main"]
