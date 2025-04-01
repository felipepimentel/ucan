import logging

import customtkinter as ctk

from .theme import COLORS, LAYOUT

logger = logging.getLogger("UCAN")


class ScrollableMessageFrame(ctk.CTkScrollableFrame):
    """Frame com scroll para mensagens"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.messages = []
        self.animation_delay = 50  # ms entre cada mensagem

    def add_message(self, message: str, sender: str, is_file: bool = False):
        """Adiciona uma mensagem ao frame com animação"""
        try:
            # Frame para a mensagem
            message_frame = ctk.CTkFrame(self, fg_color="transparent")
            message_frame.grid(
                row=len(self.messages), column=0, sticky="ew", padx=10, pady=5
            )
            message_frame.grid_columnconfigure(1, weight=1)

            # Avatar com efeito de hover
            avatar_frame = ctk.CTkFrame(
                message_frame,
                width=36,
                height=36,
                corner_radius=18,
                fg_color="transparent",
            )
            avatar_frame.grid(row=0, column=0, padx=(0, 10))
            avatar_frame.grid_propagate(False)

            avatar_label = ctk.CTkLabel(
                avatar_frame,
                text=sender[0],
                width=36,
                height=36,
                corner_radius=18,
                fg_color=COLORS["primary"]
                if sender == "Assistente IA"
                else COLORS["secondary"],
                text_color=COLORS["text_light"],
                font=ctk.CTkFont(size=16, weight="bold"),
            )
            avatar_label.pack(expand=True)

            # Efeito de hover no avatar
            avatar_label.bind(
                "<Enter>",
                lambda e: avatar_label.configure(
                    fg_color=COLORS["primary_hover"]
                    if sender == "Assistente IA"
                    else COLORS["secondary_hover"]
                ),
            )
            avatar_label.bind(
                "<Leave>",
                lambda e: avatar_label.configure(
                    fg_color=COLORS["primary"]
                    if sender == "Assistente IA"
                    else COLORS["secondary"]
                ),
            )

            # Frame para o conteúdo da mensagem
            content_frame = ctk.CTkFrame(
                message_frame,
                fg_color=COLORS["surface"],
                corner_radius=LAYOUT["border_radius"]["medium"],
                border_width=1,
                border_color=COLORS["border"],
            )
            content_frame.grid(row=0, column=1, sticky="ew")
            content_frame.grid_columnconfigure(0, weight=1)

            # Nome do remetente com ícone
            sender_frame = ctk.CTkFrame(
                content_frame,
                fg_color="transparent",
            )
            sender_frame.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))

            # Ícone baseado no remetente
            icon = "🤖" if sender == "Assistente IA" else "👤"
            icon_label = ctk.CTkLabel(
                sender_frame,
                text=icon,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"],
            )
            icon_label.pack(side="left", padx=(0, 5))

            # Nome do remetente
            sender_label = ctk.CTkLabel(
                sender_frame,
                text=sender,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_primary"],
            )
            sender_label.pack(side="left")

            # Mensagem com efeito de hover
            message_label = ctk.CTkLabel(
                content_frame,
                text=message,
                anchor="w",
                justify="left",
                wraplength=600,
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_primary"],
            )
            message_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))

            # Efeito de hover na mensagem
            content_frame.bind(
                "<Enter>",
                lambda e: content_frame.configure(
                    fg_color=COLORS["surface_light"],
                    border_color=COLORS["primary"],
                ),
            )
            content_frame.bind(
                "<Leave>",
                lambda e: content_frame.configure(
                    fg_color=COLORS["surface"],
                    border_color=COLORS["border"],
                ),
            )

            # Se for um arquivo, adiciona um ícone com efeito
            if is_file:
                file_icon = ctk.CTkLabel(
                    content_frame,
                    text="📎",
                    font=ctk.CTkFont(size=14),
                    text_color=COLORS["text_primary"],
                )
                file_icon.grid(row=1, column=1, sticky="e", padx=5)

                # Efeito de hover no ícone
                file_icon.bind(
                    "<Enter>",
                    lambda e: file_icon.configure(
                        text_color=COLORS["primary"],
                        font=ctk.CTkFont(size=16),
                    ),
                )
                file_icon.bind(
                    "<Leave>",
                    lambda e: file_icon.configure(
                        text_color=COLORS["text_primary"],
                        font=ctk.CTkFont(size=14),
                    ),
                )

            # Adiciona à lista de mensagens
            self.messages.append((message_frame, message_label, content_frame))

            # Anima a entrada da mensagem
            self._animate_message(content_frame)

            # Rola para a última mensagem após a animação
            self.after(300, self._scroll_to_bottom)

        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem: {str(e)}")

    def _animate_message(self, container):
        """Anima a entrada de uma mensagem"""
        try:
            # Calcula a altura necessária
            container.update_idletasks()
            target_height = container.winfo_reqheight()

            # Animação de altura
            steps = 10
            for i in range(steps):
                height = int((target_height * (i + 1)) / steps)
                self.after(
                    i * self.animation_delay,
                    lambda h=height: container.configure(height=h),
                )

        except Exception as e:
            logger.error(f"Erro na animação da mensagem: {str(e)}")

    def _scroll_to_bottom(self):
        """Rola para a última mensagem com animação suave"""
        try:
            canvas = self._parent_canvas
            if not canvas.winfo_exists():
                return

            # Animação suave
            current_pos = canvas.yview()[0]
            steps = 10
            for i in range(steps):
                pos = current_pos + ((1.0 - current_pos) * (i + 1) / steps)
                self.after(int(i * 20), lambda p=pos: canvas.yview_moveto(p))

        except Exception as e:
            logger.error(f"Erro ao rolar para o final: {str(e)}")

    def clear_messages(self):
        """Limpa todas as mensagens com animação"""
        try:
            # Anima a saída de cada mensagem
            for i, (frame, _, container) in enumerate(self.messages):
                self.after(
                    i * self.animation_delay,
                    lambda c=container: self._animate_out(c, frame),
                )

            # Limpa a lista após todas as animações
            self.after(
                len(self.messages) * self.animation_delay + 300,
                self._clear_messages_list,
            )

        except Exception as e:
            logger.error(f"Erro ao limpar mensagens: {str(e)}")

    def _animate_out(self, container, frame):
        """Anima a saída de uma mensagem"""
        try:
            # Animação de altura
            steps = 10
            for i in range(steps):
                height = int(container.winfo_height() * (steps - i) / steps)
                self.after(
                    i * self.animation_delay,
                    lambda h=height: container.configure(height=h),
                )

            # Remove o frame após a animação
            self.after(steps * self.animation_delay, frame.destroy)

        except Exception as e:
            logger.error(f"Erro na animação de saída: {str(e)}")

    def _clear_messages_list(self):
        """Limpa a lista de mensagens"""
        self.messages.clear()


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
