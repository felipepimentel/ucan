import customtkinter as ctk

from .helpers import create_avatar, format_timestamp


class MessageBubble(ctk.CTkFrame):
    """Bubble de mensagem"""

    def __init__(
        self, parent, message: str, timestamp: str, is_user: bool = True, **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.message = message
        self.timestamp = timestamp
        self.is_user = is_user
        self._image_references = []
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface da bubble"""
        # Avatar
        self.avatar_label = ctk.CTkLabel(
            self,
            text="",
            width=40,
            height=40,
            fg_color="transparent",
        )
        self.avatar_label.pack(side="left" if self.is_user else "right", padx=5)
        self.update_avatar()

        # Frame da mensagem
        message_frame = ctk.CTkFrame(
            self,
            fg_color=("#DCF8C6" if self.is_user else "#E8E8E8"),
            corner_radius=10,
        )
        message_frame.pack(side="left" if self.is_user else "right", padx=5)

        # Mensagem
        message_label = ctk.CTkLabel(
            message_frame,
            text=self.message,
            wraplength=300,
            justify="left",
        )
        message_label.pack(padx=10, pady=5)

        # Timestamp
        timestamp_label = ctk.CTkLabel(
            message_frame,
            text=format_timestamp(self.timestamp),
            font=("Helvetica", 8),
            fg_color="transparent",
        )
        timestamp_label.pack(padx=10, pady=2)

    def update_avatar(self):
        """Atualiza o avatar da mensagem"""
        try:
            ctk_image = create_avatar(
                self.message[0] if self.message else "U",
                size=40,
                is_user=self.is_user,
            )
            self._image_references = [ctk_image]
            self.avatar_label.configure(image=ctk_image)
        except Exception as e:
            print(f"Erro ao atualizar avatar: {e}")


class TypingIndicator(ctk.CTkFrame):
    """Indicador de digitação"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._image_references = []
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface do indicador"""
        # Avatar
        self.avatar_label = ctk.CTkLabel(
            self,
            text="",
            width=40,
            height=40,
            fg_color="transparent",
        )
        self.avatar_label.pack(side="left", padx=5)
        self.update_avatar()

        # Frame do indicador
        indicator_frame = ctk.CTkFrame(
            self,
            fg_color="#E8E8E8",
            corner_radius=10,
        )
        indicator_frame.pack(side="left", padx=5)

        # Dots
        dots_label = ctk.CTkLabel(
            indicator_frame,
            text="...",
            font=("Helvetica", 12),
        )
        dots_label.pack(padx=10, pady=5)

    def update_avatar(self):
        """Atualiza o avatar do indicador"""
        try:
            ctk_image = create_avatar(
                "B",
                size=40,
                is_user=False,
            )
            self._image_references = [ctk_image]
            self.avatar_label.configure(image=ctk_image)
        except Exception as e:
            print(f"Erro ao atualizar avatar: {e}")


class ChatHeader(ctk.CTkFrame):
    """Cabeçalho do chat"""

    def __init__(self, parent, contact_name: str, contact_status: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.contact_name = contact_name
        self.contact_status = contact_status
        self._image_references = []
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface do cabeçalho"""
        # Avatar
        self.avatar_label = ctk.CTkLabel(
            this,
            text="",
            width=40,
            height=40,
            fg_color="transparent",
        )
        self.avatar_label.pack(side="left", padx=10)
        self.update_avatar()

        # Nome e status
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10)

        name_label = ctk.CTkLabel(
            info_frame,
            text=self.contact_name,
            font=("Helvetica", 14, "bold"),
        )
        name_label.pack(anchor="w")

        status_label = ctk.CTkLabel(
            info_frame,
            text=self.contact_status,
            font=("Helvetica", 12),
            fg_color="gray",
        )
        status_label.pack(anchor="w")

        # Botões de ação
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(side="right", padx=10)

        # Chamada
        call_btn = ctk.CTkButton(
            actions_frame,
            text="📞",
            width=30,
            height=30,
            command=self.call,
        )
        call_btn.pack(side="left", padx=2)

        # Vide chamada
        video_btn = ctk.CTkButton(
            actions_frame,
            text="📹",
            width=30,
            height=30,
            command=self.video_call,
        )
        video_btn.pack(side="left", padx=2)

        # Buscar
        search_btn = ctk.CTkButton(
            actions_frame,
            text="🔍",
            width=30,
            height=30,
            command=self.search,
        )
        search_btn.pack(side="left", padx=2)

        # Limpar chat
        clear_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=30,
            height=30,
            command=self.clear_chat,
        )
        clear_btn.pack(side="left", padx=2)

    def update_avatar(self):
        """Atualiza o avatar do contato"""
        try:
            ctk_image = create_avatar(
                self.contact_name[0] if self.contact_name else "C",
                size=40,
                is_user=False,
            )
            self._image_references = [ctk_image]
            self.avatar_label.configure(image=ctk_image)
        except Exception as e:
            print(f"Erro ao atualizar avatar: {e}")

    def call(self):
        """Inicia uma chamada"""
        print(f"Chamando {self.contact_name}...")

    def video_call(self):
        """Inicia uma vide chamada"""
        print(f"Iniciando vide chamada com {self.contact_name}...")

    def search(self):
        """Abre a busca no chat"""
        print("Abrindo busca...")

    def clear_chat(self):
        """Limpa o histórico do chat"""
        print("Limpando chat...")
