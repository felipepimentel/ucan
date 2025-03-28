import base64
import io
import json
import os
import random
import sys
from datetime import datetime
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageTk


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
ctk.set_appearance_mode("System")  # Modos: "System" (padrão), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (padrão), "green", "dark-blue"

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

# Configurações consistentes de fonte
FONTS = {
    "heading": ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
    "subheading": ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
    "body": ctk.CTkFont(family="Helvetica", size=13),
    "body_bold": ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
    "small": ctk.CTkFont(family="Helvetica", size=11),
    "emoji": ctk.CTkFont(family="Segoe UI Emoji", size=16),
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

    def __init__(self, master, username, save_callback):
        super().__init__(master)
        self.title("Configurações de Perfil")
        self.geometry("400x500")
        self.resizable(False, False)

        self.current_username = username
        self.save_callback = save_callback
        self.avatar_data = None

        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Configurações de Perfil",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.pack(pady=(0, 20))

        # Avatar
        self.avatar_frame = ctk.CTkFrame(self.main_frame)
        self.avatar_frame.pack(pady=10)

        self.avatar_image = ctk.CTkLabel(
            self.avatar_frame, text="", width=100, height=100
        )
        self.avatar_image.pack(side="top", pady=5)

        # Botão para alterar avatar
        self.change_avatar_btn = ctk.CTkButton(
            self.avatar_frame, text="Alterar Avatar", command=self.change_avatar
        )
        self.change_avatar_btn.pack(side="bottom", pady=5)

        # Nome de usuário
        self.username_frame = ctk.CTkFrame(self.main_frame)
        self.username_frame.pack(fill="x", pady=10)

        self.username_label = ctk.CTkLabel(self.username_frame, text="Nome de Usuário:")
        self.username_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.username_entry = ctk.CTkEntry(
            self.username_frame, placeholder_text="Seu nome de usuário", width=300
        )
        self.username_entry.pack(padx=10, pady=(5, 10))
        self.username_entry.insert(0, self.current_username)

        # Status personalizado
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill="x", pady=10)

        self.status_label = ctk.CTkLabel(
            self.status_frame, text="Status Personalizado:"
        )
        self.status_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.status_entry = ctk.CTkEntry(
            self.status_frame,
            placeholder_text="Ex: Disponível, Ocupado, etc.",
            width=300,
        )
        self.status_entry.pack(padx=10, pady=(5, 10))

        # Opções de notificações
        self.notif_frame = ctk.CTkFrame(self.main_frame)
        self.notif_frame.pack(fill="x", pady=10)

        self.notif_label = ctk.CTkLabel(self.notif_frame, text="Notificações:")
        self.notif_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.notif_var = ctk.BooleanVar(value=True)
        self.notif_switch = ctk.CTkSwitch(
            self.notif_frame,
            text="Ativar notificações de mensagens",
            variable=self.notif_var,
        )
        self.notif_switch.pack(anchor="w", padx=20, pady=(5, 10))

        self.sound_var = ctk.BooleanVar(value=True)
        self.sound_switch = ctk.CTkSwitch(
            self.notif_frame, text="Sons de notificação", variable=self.sound_var
        )
        self.sound_switch.pack(anchor="w", padx=20, pady=(0, 10))

        # Botões de ação
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=(20, 0))

        self.cancel_btn = ctk.CTkButton(
            self.button_frame,
            text="Cancelar",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self.destroy,
        )
        self.cancel_btn.pack(side="left", padx=10)

        self.save_btn = ctk.CTkButton(
            self.button_frame, text="Salvar", command=self.save_profile
        )
        self.save_btn.pack(side="right", padx=10)

        # Carregar avatar padrão
        self.load_default_avatar()

    def load_default_avatar(self):
        """Carrega um avatar padrão"""
        # Cria um círculo colorido como avatar padrão
        size = 100
        img = Image.new("RGB", (size, size), color=(100, 149, 237))

        # Desenha um círculo
        from PIL import ImageDraw

        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size, size), fill=(65, 105, 225))

        # Adiciona iniciais
        from PIL import ImageFont

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        initials = self.current_username[0].upper() if self.current_username else "U"
        text_width, text_height = (
            draw.textsize(initials, font=font)
            if hasattr(draw, "textsize")
            else (30, 30)
        )
        position = ((size - text_width) // 2, (size - text_height) // 2)
        draw.text(position, initials, fill=(255, 255, 255), font=font)

        self.avatar_pil = img
        self.update_avatar(img)

    def update_avatar(self, img):
        """Atualiza a imagem do avatar"""
        # Redimensionar para garantir que seja 100x100
        img = img.resize((100, 100), Image.LANCZOS)

        # Converter para o formato CTk
        photo_img = ImageTk.PhotoImage(img)

        # Atualizar o label
        self.avatar_image.configure(image=photo_img)
        self.avatar_image.image = photo_img  # Manter referência

        # Salvar dados do avatar
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        self.avatar_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    def change_avatar(self):
        """Abre o seletor de arquivo para escolher um novo avatar"""
        file_path = filedialog.askopenfilename(
            title="Selecionar Avatar",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp")],
        )

        if file_path:
            try:
                img = Image.open(file_path)
                # Cortar para um quadrado se necessário
                width, height = img.size
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                right = left + size
                bottom = top + size
                img = img.crop((left, top, right, bottom))

                self.update_avatar(img)
            except Exception as e:
                print(f"Erro ao abrir a imagem: {e}")

    def save_profile(self):
        """Salva as configurações de perfil"""
        new_username = self.username_entry.get().strip()
        if not new_username:
            # Mostrar erro
            self.show_error("O nome de usuário não pode estar vazio!")
            return

        # Coletar dados do perfil
        profile_data = {
            "username": new_username,
            "status": self.status_entry.get().strip(),
            "notifications": self.notif_var.get(),
            "sound": self.sound_var.get(),
            "avatar": self.avatar_data,
        }

        # Chamar callback com os dados
        self.save_callback(profile_data)
        self.destroy()

    def show_error(self, message):
        """Exibe uma mensagem de erro"""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Erro")
        error_window.geometry("300x150")
        error_window.resizable(False, False)

        error_label = ctk.CTkLabel(
            error_window, text=message, font=ctk.CTkFont(size=14)
        )
        error_label.pack(pady=20)

        ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
        ok_button.pack(pady=10)


class MessageBubble(ctk.CTkFrame):
    """Bolha de mensagem personalizada com suporte a reações e opções"""

    def __init__(self, master, sender, message, timestamp, is_user, **kwargs):
        self.main_app = kwargs.pop("main_app", None)
        super().__init__(
            master,
            corner_radius=15,
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
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))

        # Avatar (placeholder circular)
        self.avatar_label = ctk.CTkLabel(
            self.header_frame, text="", width=30, height=30
        )
        self.avatar_label.pack(side="left", padx=(0, 5))
        self.update_avatar()

        # Nome do remetente
        self.sender_label = ctk.CTkLabel(
            self.header_frame,
            text=self.sender,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "gray70"),
        )
        self.sender_label.pack(side="left", fill="x", expand=True, anchor="w")

        # Timestamp
        self.time_label = ctk.CTkLabel(
            self.header_frame,
            text=self.format_timestamp(),
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "gray70"),
        )
        self.time_label.pack(side="right")

        # Conteúdo da mensagem
        self.message_label = ctk.CTkLabel(
            self,
            text=self.message_text,
            font=ctk.CTkFont(size=14),
            wraplength=400,
            justify="left",
            anchor="w",
        )
        self.message_label.grid(row=1, column=0, sticky="w", padx=10, pady=(5, 10))

        # Opções da mensagem (aparecem ao passar o mouse)
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.grid(row=2, column=0, sticky="e", padx=10, pady=(0, 5))

        # Botão de reação
        self.react_button = ctk.CTkButton(
            self.options_frame,
            text="😊",
            width=30,
            height=30,
            command=self.show_reaction_selector,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
        )
        self.react_button.pack(side="left", padx=2)

        # Botão de responder
        self.reply_button = ctk.CTkButton(
            self.options_frame,
            text="↩️",
            width=30,
            height=30,
            command=self.reply_to_message,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
        )
        self.reply_button.pack(side="left", padx=2)

        # Área de reações
        self.reactions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.reactions_frame.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 5))
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
        from PIL import ImageDraw

        draw = ImageDraw.Draw(img)
        draw.ellipse(
            (0, 0, size, size), fill=(65, 105, 225) if self.is_user else (127, 140, 141)
        )

        # Adiciona iniciais
        from PIL import ImageFont

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
                font=ctk.CTkFont(size=12),
                fg_color=("gray80", "gray30"),
                hover_color=("gray70", "gray40"),
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


class ChatApp(ctk.CTk):
    """Classe principal da aplicação de chat"""

    def __init__(self):
        super().__init__()

        # Inicializar listas e variáveis de estado
        self.message_bubbles = []
        self.message_history = []
        self.replying_to = None
        self.typing_indicator = None

        # Respostas do bot para demonstração
        self.bot_responses = [
            "Como posso ajudar você hoje?",
            "Entendi. Você poderia fornecer mais detalhes?",
            "Estou processando sua solicitação.",
            "Isso é interessante! Conte-me mais.",
            "Vou pesquisar sobre isso para você.",
            "Claro, posso auxiliar com isso.",
            "Preciso de algumas informações adicionais para continuar.",
            "Sua solicitação foi recebida. Estou trabalhando nisso.",
            "Obrigado por compartilhar isso comigo!",
            "Vamos explorar algumas opções para resolver isso.",
        ]

        # Configurar janela principal
        self.title("UCAN - Universal Conversational Assistant Navigator")
        self.geometry("1200x800")
        self.minsize(800, 600)
        self.iconbitmap("assets/icon.ico") if os.path.exists(
            "assets/icon.ico"
        ) else None

        # Carregar configurações
        self.load_settings()
        self.load_message_history()

        # Criar widgets
        self.create_widgets()

        # Carregar histórico na UI
        self.load_history_to_ui()

        # Configurar atalhos de teclado
        self.bind("<Control-Return>", lambda e: self.send_message())
        self.bind("<Control-l>", lambda e: self.clear_chat())
        self.bind(
            "<Escape>", lambda e: self.cancel_reply() if self.replying_to else None
        )

        # Adicionar mensagem de boas-vindas se não houver histórico
        if not self.message_history:
            self.add_message(
                "ChatBot",
                "Olá! Bem-vindo ao Chat Conversacional. Como posso ajudar você hoje?",
            )

        # Centralizar janela
        self.center_window()

    def load_message_history(self):
        """Carrega o histórico de mensagens do arquivo"""
        try:
            with open("chat_history.json", "r", encoding="utf-8") as f:
                self.message_history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.message_history = []

    def save_message_history(self):
        """Salva o histórico de mensagens no arquivo"""
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(self.message_history, f, ensure_ascii=False, indent=2)

    def load_settings(self):
        """Carrega as configurações do usuário"""
        settings_file = "user_settings.json"
        default_settings = {
            "username": "Você",
            "status": "Online",
            "notifications": True,
            "sound": True,
            "theme": "Azul Clássico",
            "appearance_mode": "System",
            "avatar": None,
        }

        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    self.user_settings = json.load(f)
            except:
                self.user_settings = default_settings
        else:
            self.user_settings = default_settings

    def save_settings(self):
        """Salva as configurações do usuário"""
        settings_file = "user_settings.json"
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(self.user_settings, f, ensure_ascii=False, indent=2)

    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Configuração do grid principal
        self.grid_columnconfigure(0, weight=0)  # Barra lateral
        self.grid_columnconfigure(1, weight=1)  # Área principal
        self.grid_rowconfigure(0, weight=1)

        # ==== BARRA LATERAL ====
        self.sidebar = ctk.CTkFrame(
            self, width=250, corner_radius=0, fg_color=("gray90", "gray20")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=0)
        self.sidebar.grid_propagate(False)  # Impede que o frame encolha

        # Informações do usuário
        self.profile_frame = ctk.CTkFrame(
            self.sidebar, corner_radius=10, fg_color=("gray85", "gray25")
        )
        self.profile_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Avatar do usuário
        self.user_avatar = ctk.CTkLabel(
            self.profile_frame, text="", width=50, height=50
        )
        self.user_avatar.grid(row=0, column=0, padx=10, pady=10)
        self.update_user_avatar()

        # Nome e status
        self.user_info = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        self.user_info.grid(row=0, column=1, sticky="nsew", padx=5)

        self.username_label = ctk.CTkLabel(
            self.user_info,
            text=self.user_settings["username"],
            font=FONTS["body_bold"],
        )
        self.username_label.grid(row=0, column=0, sticky="w")

        self.status_indicator = ctk.CTkFrame(
            self.user_info,
            width=10,
            height=10,
            corner_radius=5,
            fg_color=COLORS["success"],
        )
        self.status_indicator.grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.status_indicator.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.user_info,
            text=self.user_settings["status"],
            font=FONTS["small"],
            text_color=("gray50", "gray70"),
        )
        self.status_label.grid(row=1, column=0, sticky="w", padx=(15, 0))

        # Botão de configurações
        self.settings_button = ctk.CTkButton(
            self.profile_frame,
            text="⚙️",
            width=30,
            command=self.open_profile_settings,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            font=FONTS["emoji"],
        )
        self.settings_button.grid(row=0, column=2, padx=5)

        # Barra de pesquisa
        self.search_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.search_frame.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 5))
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Pesquisar conversas...",
            height=35,
            corner_radius=17,
            border_width=1,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=0, pady=5)

        # Título das conversas
        self.conversations_title = ctk.CTkLabel(
            self.sidebar, text="Conversas", font=FONTS["subheading"], anchor="w"
        )
        self.conversations_title.grid(
            row=2, column=0, sticky="w", padx=15, pady=(10, 5)
        )

        # Lista de conversas
        self.conversations_frame = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent"
        )
        self.conversations_frame.grid(
            row=3, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )
        self.conversations_frame.grid_columnconfigure(0, weight=1)

        # Preencher a lista de conversas
        self.populate_conversation_list()

        # Barra inferior com botões de ação
        self.sidebar_bottom = ctk.CTkFrame(
            self.sidebar, fg_color=("gray85", "gray25"), height=50
        )
        self.sidebar_bottom.grid(row=4, column=0, sticky="ew", padx=0, pady=0)
        self.sidebar_bottom.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.sidebar_bottom.grid_propagate(False)

        # Botão de novo chat
        self.new_chat_btn = ctk.CTkButton(
            self.sidebar_bottom,
            text="➕",
            width=40,
            height=40,
            command=self.create_new_chat,
            fg_color="transparent",
            hover_color=("gray75", "gray35"),
            font=FONTS["emoji"],
        )
        self.new_chat_btn.grid(row=0, column=0, padx=5, pady=5)

        # Botão de tema
        self.theme_mode = ctk.StringVar(value=ctk.get_appearance_mode())
        self.theme_btn = ctk.CTkButton(
            self.sidebar_bottom,
            text="🌙" if self.theme_mode.get() == "Light" else "☀️",
            width=40,
            height=40,
            command=self.toggle_theme,
            fg_color="transparent",
            hover_color=("gray75", "gray35"),
            font=FONTS["emoji"],
        )
        self.theme_btn.grid(row=0, column=1, padx=5, pady=5)

        # Botão de ajuda
        self.help_btn = ctk.CTkButton(
            self.sidebar_bottom,
            text="❓",
            width=40,
            height=40,
            command=self.show_help,
            fg_color="transparent",
            hover_color=("gray75", "gray35"),
            font=FONTS["emoji"],
        )
        self.help_btn.grid(row=0, column=2, padx=5, pady=5)

        # Botão de logout
        self.logout_btn = ctk.CTkButton(
            self.sidebar_bottom,
            text="🚪",
            width=40,
            height=40,
            command=self.confirm_logout,
            fg_color="transparent",
            hover_color=("gray75", "gray35"),
            font=FONTS["emoji"],
        )
        self.logout_btn.grid(row=0, column=3, padx=5, pady=5)

        # ==== ÁREA PRINCIPAL ====
        self.setup_main_area()

    def setup_main_area(self):
        """Configura a área principal do chat"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)  # Cabeçalho
        self.main_frame.grid_rowconfigure(1, weight=1)  # Área de mensagens
        self.main_frame.grid_rowconfigure(2, weight=0)  # Área de resposta
        self.main_frame.grid_rowconfigure(3, weight=0)  # Área de entrada

        # Cabeçalho com design melhorado
        self.header_frame = ctk.CTkFrame(
            self.main_frame, height=70, fg_color=("gray90", "gray25"), corner_radius=0
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)  # Impede que o frame encolha

        # Avatar do contato atual
        self.chat_avatar = ctk.CTkLabel(
            self.header_frame,
            text="C",
            width=40,
            height=40,
            fg_color=COLORS["primary"],
            text_color=("white", "white"),
            corner_radius=20,
            font=FONTS["body_bold"],
        )
        self.chat_avatar.grid(row=0, column=0, padx=(20, 10), pady=15)

        # Informações do contato
        self.chat_info = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.chat_info.grid(row=0, column=1, sticky="w", pady=10)

        self.chat_title = ctk.CTkLabel(
            self.chat_info, text="ChatBot", font=FONTS["heading"]
        )
        self.chat_title.grid(row=0, column=0, sticky="w")

        self.chat_status = ctk.CTkLabel(
            self.chat_info,
            text="Online",
            font=FONTS["small"],
            text_color=("gray50", "gray70"),
        )
        self.chat_status.grid(row=1, column=0, sticky="w")

        # Botões do cabeçalho
        self.header_buttons = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_buttons.grid(row=0, column=2, padx=20)

        # Botão de chamada
        self.call_button = ctk.CTkButton(
            self.header_buttons,
            text="📞",
            width=40,
            command=lambda: self.show_feature_unavailable("Chamadas"),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            font=FONTS["emoji"],
        )
        self.call_button.grid(row=0, column=0, padx=5)

        # Botão de videochamada
        self.video_button = ctk.CTkButton(
            self.header_buttons,
            text="🎥",
            width=40,
            command=lambda: self.show_feature_unavailable("Videochamadas"),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            font=FONTS["emoji"],
        )
        self.video_button.grid(row=0, column=1, padx=5)

        # Botão de pesquisa
        self.search_button = ctk.CTkButton(
            self.header_buttons,
            text="🔍",
            width=40,
            command=self.open_search,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            font=FONTS["emoji"],
        )
        self.search_button.grid(row=0, column=2, padx=5)

        # Botão de limpar chat
        self.clear_button = ctk.CTkButton(
            self.header_buttons,
            text="🗑️",
            width=40,
            command=self.confirm_clear_chat,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            font=FONTS["emoji"],
        )
        self.clear_button.grid(row=0, column=3, padx=5)

        # Frame rolável para mensagens com visual melhorado
        self.chat_frame = ScrollableMessageFrame(
            self.main_frame, fg_color=("gray95", "gray15"), corner_radius=0
        )
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Frame para resposta (inicialmente oculto)
        self.reply_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray85", "gray30"),
            corner_radius=10,
            border_width=1,
            border_color=("gray75", "gray40"),
        )
        self.reply_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.reply_frame.grid_remove()  # Oculto inicialmente

        self.reply_label = ctk.CTkLabel(
            self.reply_frame, text="Respondendo a:", font=FONTS["small"]
        )
        self.reply_label.pack(side="left", padx=10, pady=5)

        self.reply_content = ctk.CTkLabel(
            self.reply_frame, text="", font=FONTS["small"], wraplength=300
        )
        self.reply_content.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.cancel_reply_button = ctk.CTkButton(
            self.reply_frame,
            text="✕",
            width=30,
            height=30,
            command=self.cancel_reply,
            fg_color="transparent",
            hover_color=("gray70", "gray40"),
            font=FONTS["small"],
        )
        self.cancel_reply_button.pack(side="right", padx=10, pady=5)

        # Área de entrada com design moderno
        self.setup_input_area()

    def update_user_avatar(self):
        """Atualiza o avatar do usuário"""
        # Se tiver um avatar personalizado
        if self.user_settings.get("avatar"):
            try:
                # Decodificar o avatar de base64
                avatar_data = base64.b64decode(self.user_settings["avatar"])
                img = Image.open(io.BytesIO(avatar_data))
                img = img.resize((50, 50), Image.LANCZOS)
                avatar_img = ImageTk.PhotoImage(img)
                self.user_avatar.configure(image=avatar_img)
                self.user_avatar.image = avatar_img
                return
            except Exception as e:
                print(f"Erro ao carregar avatar: {e}")

        # Avatar padrão se não tiver personalizado
        size = 50
        img = Image.new("RGB", (size, size), color=(65, 105, 225))

        # Desenha um círculo
        from PIL import ImageDraw

        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size, size), fill=(65, 105, 225))

        # Adiciona iniciais
        from PIL import ImageFont

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        initials = self.user_settings["username"][0].upper()
        text_width, text_height = (
            draw.textsize(initials, font=font)
            if hasattr(draw, "textsize")
            else (15, 15)
        )
        position = ((size - text_width) // 2, (size - text_height) // 2)
        draw.text(position, initials, fill=(255, 255, 255), font=font)

        # Converter para o formato CTk
        avatar_img = ImageTk.PhotoImage(img)
        self.user_avatar.configure(image=avatar_img)
        self.user_avatar.image = avatar_img

    def create_chat_item(self, master, chat_data):
        """Cria um item de chat para a lista de conversas"""
        frame = ctk.CTkFrame(master)
        frame.bind("<Button-1>", lambda e: self.select_chat(chat_data["name"]))

        # Nome da conversa
        name_label = ctk.CTkLabel(
            frame,
            text=chat_data["name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        name_label.pack(anchor="w", padx=10, pady=(5, 0))

        # Última mensagem e hora
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=(0, 5))
        info_frame.grid_columnconfigure(0, weight=1)

        message_label = ctk.CTkLabel(
            info_frame,
            text=chat_data["last_message"],
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70"),
            anchor="w",
        )
        message_label.grid(row=0, column=0, sticky="w")

        time_label = ctk.CTkLabel(
            info_frame,
            text=chat_data["time"],
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray70"),
        )
        time_label.grid(row=0, column=1, sticky="e")

        return frame

    def select_chat(self, chat_name):
        """Seleciona uma conversa da lista"""
        self.chat_title.configure(text=chat_name)
        # Em uma implementação real, carregaria as mensagens específicas desse chat

    def show_emoji_selector(self):
        """Exibe o seletor de emojis"""
        emoji_window = EmojiSelector(self, self.input_textbox)
        emoji_window.focus()

    def on_enter_pressed(self, event):
        """Processa quando a tecla Enter é pressionada"""
        if not event.state & 0x1:  # Verifica se Shift não está pressionado
            self.send_message()
            return "break"  # Impede a inserção de uma nova linha

    def set_reply_to(self, sender, message):
        """Define uma mensagem para responder"""
        self.replying_to = {"sender": sender, "message": message}

        # Exibir o frame de resposta
        self.reply_content.configure(
            text=f"{sender}: {message[:50]}..."
            if len(message) > 50
            else f"{sender}: {message}"
        )
        self.reply_frame.grid()

        # Focar na caixa de texto
        self.input_textbox.focus_set()

    def cancel_reply(self):
        """Cancela a resposta a uma mensagem"""
        self.replying_to = None
        self.reply_frame.grid_remove()

    def send_message(self):
        """Envia a mensagem atual"""
        message = self.input_textbox.get("1.0", "end-1c").strip()
        if message:
            # Salvar informações de resposta se houver
            reply_info = None
            if self.replying_to:
                reply_info = self.replying_to
                self.cancel_reply()

            # Adiciona a mensagem do usuário
            self.add_message(
                self.user_settings["username"], message, reply_to=reply_info
            )

            self.input_textbox.delete("1.0", "end")

            # Simula resposta do bot após um pequeno atraso
            self.after(800, self.simulate_bot_response)

    def simulate_bot_response(self):
        """Simula uma resposta do bot para demonstração"""
        response = random.choice(self.bot_responses)
        # Simula digitação
        self.show_typing_indicator("ChatBot")

        # Atraso para simular processamento
        typing_time = len(response) * 0.05  # Tempo baseado no tamanho da resposta
        self.after(int(typing_time * 1000), lambda: self.finish_bot_response(response))

    def show_typing_indicator(self, sender):
        """Exibe um indicador de digitação"""
        # Frame para indicador
        typing_indicator = ctk.CTkFrame(self.chat_frame)

        # Label com texto "digitando..."
        typing_text = ctk.CTkLabel(
            typing_indicator,
            text=f"{sender} está digitando...",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"),
        )
        typing_text.pack(padx=10, pady=5)

        self.chat_frame.add_widget(typing_indicator)
        self.typing_indicator = typing_indicator

    def finish_bot_response(self, message):
        """Remove o indicador de digitação e mostra a resposta"""
        if hasattr(self, "typing_indicator"):
            self.typing_indicator.destroy()
        self.add_message("ChatBot", message)

    def add_message(self, sender, message, reply_to=None):
        """Adiciona uma mensagem ao chat"""
        # Adicionar ao histórico
        timestamp = datetime.now().isoformat()
        message_data = {
            "sender": sender,
            "message": message,
            "timestamp": timestamp,
            "reply_to": reply_to,
        }
        self.message_history.append(message_data)
        self.save_message_history()

        # Criar bolha de mensagem
        is_user = sender == self.user_settings["username"]
        message_bubble = MessageBubble(
            self.chat_frame, sender, message, timestamp, is_user, main_app=self
        )

        # Alinhar à direita se for mensagem do usuário atual
        sticky_direction = "e" if is_user else "w"
        message_bubble.configure(anchor=sticky_direction)
        self.chat_frame.add_widget(message_bubble)

        # Se estiver respondendo a uma mensagem, adicionar citação
        if reply_to:
            quote_text = (
                f"↪️ Respondendo a {reply_to['sender']}: {reply_to['message'][:30]}..."
                if len(reply_to["message"]) > 30
                else f"↪️ Respondendo a {reply_to['sender']}: {reply_to['message']}"
            )
            quote_label = ctk.CTkLabel(
                message_bubble,
                text=quote_text,
                font=ctk.CTkFont(size=10, slant="italic"),
                text_color=("gray40", "gray70"),
            )
            quote_label.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 5))

    def attach_file(self):
        """Abre o seletor de arquivos para anexar algo à mensagem"""
        file_path = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[
                ("Todos os arquivos", "*.*"),
                ("Imagens", "*.png *.jpg *.jpeg *.gif"),
                ("Documentos", "*.pdf *.docx *.txt"),
            ],
        )

        if file_path:
            # Nesta implementação, apenas adiciona o nome do arquivo à mensagem
            file_name = os.path.basename(file_path)
            current_text = self.input_textbox.get("1.0", "end-1c")

            if current_text:
                self.input_textbox.insert("end", f"\n[Arquivo: {file_name}]")
            else:
                self.input_textbox.insert("1.0", f"[Arquivo: {file_name}]")

    def open_search(self):
        """Abre a caixa de pesquisa no histórico de mensagens"""
        search_window = ctk.CTkToplevel(self)
        search_window.title("Pesquisar no Chat")
        search_window.geometry("500x400")
        search_window.resizable(True, True)

        # Frame de pesquisa
        search_frame = ctk.CTkFrame(search_window)
        search_frame.pack(fill="x", padx=20, pady=20)

        search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Digite para pesquisar...", width=350
        )
        search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)

        search_button = ctk.CTkButton(
            search_frame,
            text="Pesquisar",
            command=lambda: self.perform_search(search_entry.get(), results_frame),
        )
        search_button.pack(side="right")

        # Frame de resultados
        results_frame = ctk.CTkScrollableFrame(search_window)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Evento de pesquisa ao pressionar Enter
        search_entry.bind(
            "<Return>", lambda e: self.perform_search(search_entry.get(), results_frame)
        )

        # Focar na entrada
        search_entry.focus_set()

    def perform_search(self, query, results_frame):
        """Realiza a pesquisa no histórico de mensagens"""
        # Limpar resultados anteriores
        for widget in results_frame.winfo_children():
            widget.destroy()

        if not query.strip():
            no_results = ctk.CTkLabel(
                results_frame,
                text="Digite algo para pesquisar",
                font=ctk.CTkFont(size=14),
            )
            no_results.pack(pady=20)
            return

        # Filtrar mensagens
        results = []
        for msg in self.message_history:
            if query.lower() in msg["message"].lower():
                results.append(msg)

        if not results:
            no_results = ctk.CTkLabel(
                results_frame,
                text="Nenhum resultado encontrado",
                font=ctk.CTkFont(size=14),
            )
            no_results.pack(pady=20)
            return

        # Exibir resultados
        results_label = ctk.CTkLabel(
            results_frame,
            text=f"Encontrados {len(results)} resultados:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        results_label.pack(anchor="w", pady=(0, 10))

        for result in results:
            result_frame = ctk.CTkFrame(results_frame)
            result_frame.pack(fill="x", pady=5)

            header = ctk.CTkLabel(
                result_frame,
                text=f"{result['sender']} - {self.format_timestamp(result['timestamp'])}",
                font=ctk.CTkFont(size=12, weight="bold"),
            )
            header.pack(anchor="w", padx=10, pady=(5, 0))

            message = ctk.CTkLabel(
                result_frame,
                text=result["message"],
                font=ctk.CTkFont(size=12),
                wraplength=400,
                justify="left",
            )
            message.pack(anchor="w", padx=10, pady=(0, 5))

    def format_timestamp(self, timestamp):
        """Formata o timestamp para exibição"""
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return timestamp

    def load_history_to_ui(self):
        """Carrega o histórico de mensagens na interface"""
        try:
            with open("chat_history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
                for message in history:
                    is_user = message["sender"] != "ChatBot"
                    sticky_direction = "e" if is_user else "w"
                    message_bubble = MessageBubble(
                        master=self.chat_frame,
                        sender=message["sender"],
                        message=message["message"],
                        timestamp=message["timestamp"],
                        is_user=is_user,
                        main_app=self,
                    )
                    message_bubble.grid(
                        row=len(self.chat_frame.grid_slaves()),
                        column=0,
                        padx=10,
                        pady=5,
                        sticky=sticky_direction,
                    )
                    self.message_bubbles.append(message_bubble)
        except FileNotFoundError:
            pass  # No history file yet

    def confirm_clear_chat(self):
        """Confirma antes de limpar o chat"""
        confirm = ctk.CTkToplevel(self)
        confirm.title("Confirmar")
        confirm.geometry("300x150")
        confirm.resizable(False, False)

        question = ctk.CTkLabel(
            confirm,
            text="Tem certeza que deseja limpar\ntodo o histórico de mensagens?",
            font=ctk.CTkFont(size=14),
        )
        question.pack(pady=20)

        button_frame = ctk.CTkFrame(confirm, fg_color="transparent")
        button_frame.pack(pady=10)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=confirm.destroy,
        )
        cancel_btn.pack(side="left", padx=10)

        confirm_btn = ctk.CTkButton(
            button_frame,
            text="Limpar",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=lambda: [self.clear_chat(), confirm.destroy()],
        )
        confirm_btn.pack(side="right", padx=10)

    def clear_chat(self):
        """Limpa o histórico de chat"""
        # Limpar a interface
        self.chat_frame.clear_widgets()

        # Limpar histórico
        self.message_history = []
        self.save_message_history()

        # Adicionar mensagem de boas-vindas
        self.add_message("ChatBot", "Chat limpo. Como posso ajudar você hoje?")

    def center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def open_profile_settings(self):
        """Abre as configurações de perfil"""
        settings = ProfileSettings(
            self, self.user_settings["username"], self.update_profile
        )
        settings.focus()

    def update_profile(self, profile_data):
        """Atualiza os dados do perfil"""
        self.user_settings.update(profile_data)
        self.save_settings()

        # Atualizar UI
        self.username_label.configure(text=profile_data["username"])
        self.status_label.configure(text=profile_data["status"])
        self.update_user_avatar()

    def setup_input_area(self):
        """Configura a área de entrada de mensagens"""
        # Frame para área de entrada
        self.input_frame = ctk.CTkFrame(
            self.main_frame, fg_color=("gray90", "gray25"), corner_radius=0, height=100
        )
        self.input_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_propagate(False)

        # Área de entrada redesenhada
        self.input_area = ctk.CTkFrame(
            self.input_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=15,
            border_width=1,
            border_color=("gray80", "gray35"),
        )
        self.input_area.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        self.input_area.grid_columnconfigure(1, weight=1)

        # Botões à esquerda
        self.left_buttons = ctk.CTkFrame(self.input_area, fg_color="transparent")
        self.left_buttons.grid(row=0, column=0, padx=(10, 0), pady=5)

        # Botão para anexos
        self.attach_button = ctk.CTkButton(
            self.left_buttons,
            text="📎",
            width=35,
            height=35,
            command=self.attach_file,
            fg_color="transparent",
            hover_color=("gray85", "gray30"),
            font=FONTS["emoji"],
        )
        self.attach_button.grid(row=0, column=0, padx=2)

        # Botão para gravação de áudio
        self.audio_button = ctk.CTkButton(
            self.left_buttons,
            text="🎤",
            width=35,
            height=35,
            command=lambda: self.show_feature_unavailable("Gravação de Áudio"),
            fg_color="transparent",
            hover_color=("gray85", "gray30"),
            font=FONTS["emoji"],
        )
        self.audio_button.grid(row=0, column=1, padx=2)

        # Campo de entrada de texto com visual melhorado
        self.input_textbox = ctk.CTkTextbox(
            self.input_area,
            height=70,
            wrap="word",
            fg_color="transparent",
            corner_radius=10,
            font=FONTS["body"],
            activate_scrollbars=False,
        )
        self.input_textbox.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.input_textbox.bind("<Return>", self.on_enter_pressed)
        self.input_textbox.bind(
            "<Shift-Return>", lambda e: None
        )  # Permite quebra de linha com Shift+Enter
        self.input_textbox.insert("1.0", "")  # Texto inicial vazio

        # Placeholder para o input
        self.input_placeholder = "Digite uma mensagem..."
        self.show_input_placeholder()
        self.input_textbox.bind("<FocusIn>", self.on_input_focus_in)
        self.input_textbox.bind("<FocusOut>", self.on_input_focus_out)

        # Botões à direita
        self.right_buttons = ctk.CTkFrame(self.input_area, fg_color="transparent")
        self.right_buttons.grid(row=0, column=2, padx=(0, 10), pady=5)

        # Botão de emoji
        self.emoji_button = ctk.CTkButton(
            self.right_buttons,
            text="😊",
            width=35,
            height=35,
            command=self.show_emoji_selector,
            fg_color="transparent",
            hover_color=("gray85", "gray30"),
            font=FONTS["emoji"],
        )
        self.emoji_button.grid(row=0, column=0, padx=2)

        # Botão de enviar
        self.send_button = ctk.CTkButton(
            self.right_buttons,
            text="➤",
            width=35,
            height=35,
            command=self.send_message,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=FONTS["emoji"],
            corner_radius=17,
        )
        self.send_button.grid(row=0, column=1, padx=2)

    def show_input_placeholder(self):
        """Mostra o placeholder no campo de input"""
        current_text = self.input_textbox.get("1.0", "end-1c")
        if not current_text:
            self.input_textbox.insert("1.0", self.input_placeholder)
            self.input_textbox.configure(text_color=("gray60", "gray60"))

    def on_input_focus_in(self, event):
        """Limpa o placeholder quando o input recebe foco"""
        current_text = self.input_textbox.get("1.0", "end-1c")
        if current_text == self.input_placeholder:
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.configure(text_color=("gray10", "gray90"))

    def on_input_focus_out(self, event):
        """Restaura o placeholder quando o input perde foco"""
        current_text = self.input_textbox.get("1.0", "end-1c")
        if not current_text:
            self.show_input_placeholder()

    def show_feature_unavailable(self, feature_name):
        """Exibe notificação de recurso não disponível"""
        notification = ctk.CTkToplevel(self)
        notification.title("Recurso Indisponível")
        notification.geometry("350x150")
        notification.resizable(False, False)
        notification.grab_set()

        label = ctk.CTkLabel(
            notification,
            text=f"O recurso '{feature_name}' não está\ndisponível na versão atual.",
            font=FONTS["body"],
            justify="center",
        )
        label.pack(pady=(30, 20))

        ok_button = ctk.CTkButton(
            notification, text="OK", command=notification.destroy, width=100
        )
        ok_button.pack(pady=10)


def main():
    app = ChatApp()
    app.mainloop()


if __name__ == "__main__":
    main()
