import base64
from io import BytesIO

import customtkinter as ctk
from PIL import Image

from .helpers import center_window, create_avatar, process_avatar_image


class ProfileSettings(ctk.CTkToplevel):
    """Janela de configurações de perfil"""

    def __init__(self, parent, settings: dict, on_save: callable):
        super().__init__(parent)
        self.settings = settings
        self.on_save = on_save
        self._image_references = []
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface da janela"""
        self.title("Configurações de Perfil")
        self.geometry("400x500")
        self.resizable(False, False)
        center_window(self)

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Avatar
        self.avatar_label = ctk.CTkLabel(
            main_frame,
            text="",
            width=100,
            height=100,
            fg_color="transparent",
        )
        self.avatar_label.pack(pady=10)
        self.update_avatar()

        # Botão de upload
        upload_btn = ctk.CTkButton(
            main_frame,
            text="Alterar Foto",
            command=self.upload_avatar,
        )
        upload_btn.pack(pady=5)

        # Nome de usuário
        username_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        username_frame.pack(fill="x", pady=10)

        username_label = ctk.CTkLabel(
            username_frame,
            text="Nome de Usuário:",
            fg_color="transparent",
        )
        username_label.pack(anchor="w")

        self.username_entry = ctk.CTkEntry(username_frame)
        self.username_entry.pack(fill="x", pady=5)
        self.username_entry.insert(0, self.settings.get("username", ""))

        # Status
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=10)

        status_label = ctk.CTkLabel(
            status_frame,
            text="Status:",
            fg_color="transparent",
        )
        status_label.pack(anchor="w")

        self.status_entry = ctk.CTkEntry(status_frame)
        self.status_entry.pack(fill="x", pady=5)
        self.status_entry.insert(0, self.settings.get("status", ""))

        # Notificações
        self.notifications_var = ctk.BooleanVar(
            value=self.settings.get("notifications", True)
        )
        notifications_check = ctk.CTkCheckBox(
            main_frame,
            text="Ativar Notificações",
            variable=self.notifications_var,
        )
        notifications_check.pack(pady=10)

        # Som
        self.sound_var = ctk.BooleanVar(value=self.settings.get("sound", True))
        sound_check = ctk.CTkCheckBox(
            main_frame,
            text="Ativar Som",
            variable=self.sound_var,
        )
        sound_check.pack(pady=10)

        # Tema
        theme_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=10)

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Tema:",
            fg_color="transparent",
        )
        theme_label.pack(anchor="w")

        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "dark"))
        theme_radio1 = ctk.CTkRadioButton(
            theme_frame,
            text="Escuro",
            variable=self.theme_var,
            value="dark",
        )
        theme_radio1.pack(anchor="w", pady=5)

        theme_radio2 = ctk.CTkRadioButton(
            theme_frame,
            text="Claro",
            variable=self.theme_var,
            value="light",
        )
        theme_radio2.pack(anchor="w", pady=5)

        # Botões
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)

        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Salvar",
            command=self.save_settings,
        )
        save_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=5)

    def update_avatar(self):
        """Atualiza o avatar do perfil"""
        try:
            if self.settings.get("avatar"):
                # Converter base64 para imagem
                img_data = base64.b64decode(self.settings["avatar"])
                img = Image.open(BytesIO(img_data))
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                self._image_references.append(img)
                ctk_image = ctk.CTkImage(
                    light_image=img, dark_image=img, size=(100, 100)
                )
                self._image_references.append(ctk_image)
                self.avatar_label.configure(image=ctk_image)
            else:
                # Criar avatar com iniciais
                ctk_image = create_avatar(
                    self.settings.get("username", "U"),
                    size=100,
                    is_user=True,
                )
                self._image_references = [ctk_image]
                self.avatar_label.configure(image=ctk_image)
        except Exception as e:
            print(f"Erro ao atualizar avatar: {e}")

    def upload_avatar(self):
        """Permite o upload de uma nova foto de perfil"""
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            img, avatar_data = process_avatar_image(file_path)
            if img:
                self.settings["avatar"] = avatar_data
                self.update_avatar()

    def save_settings(self):
        """Salva as configurações do perfil"""
        self.settings.update({
            "username": self.username_entry.get(),
            "status": self.status_entry.get(),
            "notifications": self.notifications_var.get(),
            "sound": self.sound_var.get(),
            "theme": self.theme_var.get(),
        })
        self.on_save(self.settings)
        self.destroy()


class EmojiSelector(ctk.CTkToplevel):
    """Janela de seletor de emojis"""

    def __init__(self, parent, input_widget, **kwargs):
        super().__init__(parent)
        self.input_widget = input_widget
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface da janela"""
        self.title("Seletor de Emojis")
        self.geometry("300x400")
        self.resizable(False, False)
        center_window(self)

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Categorias
        categories_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        categories_frame.pack(fill="x", pady=5)

        for category in ["Rostos", "Gestos", "Objetos", "Símbolos"]:
            btn = ctk.CTkButton(
                categories_frame,
                text=category,
                command=lambda c=category: self.show_category(c),
            )
            btn.pack(side="left", padx=2)

        # Grid de emojis
        self.emoji_frame = ctk.CTkFrame(main_frame)
        self.emoji_frame.pack(fill="both", expand=True, pady=5)

        # Mostrar primeira categoria
        self.show_category("Rostos")

    def show_category(self, category: str):
        """Mostra os emojis de uma categoria"""
        # Limpar frame
        for widget in self.emoji_frame.winfo_children():
            widget.destroy()

        # Configurar grid
        self.emoji_frame.grid_columnconfigure(tuple(range(8)), weight=1)

        # Emojis da categoria
        emojis = {
            "Rostos": [
                "😀",
                "😃",
                "😄",
                "😁",
                "😅",
                "😂",
                "🤣",
                "😊",
                "😇",
                "🙂",
                "🙃",
                "😉",
                "😌",
                "😍",
                "🥰",
                "😘",
            ],
            "Gestos": [
                "👍",
                "👎",
                "👌",
                "✌️",
                "🤞",
                "🤝",
                "👏",
                "🙌",
                "👋",
                "🤚",
                "✋",
                "🖐️",
                "👊",
                "🤛",
                "🤜",
                "🤞",
            ],
            "Objetos": [
                "📱",
                "💻",
                "⌚",
                "📷",
                "🎮",
                "🎲",
                "🎯",
                "🎨",
                "🎭",
                "🎪",
                "🎟️",
                "🎠",
                "🎡",
                "🎢",
                "🎣",
                "🎤",
            ],
            "Símbolos": [
                "❤️",
                "💔",
                "💖",
                "💗",
                "💓",
                "💞",
                "💕",
                "💟",
                "❣️",
                "💝",
                "💘",
                "💌",
                "💋",
                "💯",
                "💢",
                "💥",
            ],
        }

        # Adicionar emojis
        for i, emoji in enumerate(emojis[category]):
            btn = ctk.CTkButton(
                self.emoji_frame,
                text=emoji,
                width=30,
                height=30,
                command=lambda e=emoji: self.insert_emoji(e),
            )
            btn.grid(row=i // 8, column=i % 8, padx=2, pady=2)

    def insert_emoji(self, emoji: str):
        """Insere um emoji no campo de entrada"""
        current = self.input_widget.get()
        self.input_widget.delete(0, "end")
        self.input_widget.insert(0, current + emoji)
        self.input_widget.focus()
        self.destroy()


class LoadingScreen(ctk.CTk):
    """Tela de carregamento"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface da tela de carregamento"""
        # Configurar janela
        self.title("UCAN Chat")
        self.geometry("300x200")
        self.resizable(False, False)
        center_window(self)

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Logo
        logo_label = ctk.CTkLabel(
            main_frame,
            text="UCAN",
            font=("Helvetica", 24, "bold"),
        )
        logo_label.pack(pady=20)

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)

        # Status
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Inicializando...",
            font=("Helvetica", 12),
        )
        self.status_label.pack(pady=10)

        # Iniciar animação
        self.load()
