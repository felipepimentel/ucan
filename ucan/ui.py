import logging
import os
import threading
import tkinter
from tkinter import filedialog, messagebox
from typing import Dict

import customtkinter as ctk
from PIL import Image, ImageTk

from .ai_provider import AIProvider
from .attachments import AttachmentManager
from .database import Database
from .projects import ProjectManager
from .theme import LAYOUT, ThemeManager
from .widgets import ScrollableMessageFrame, ThinkingIndicator

logger = logging.getLogger("UCAN")


class ChatApp(ctk.CTk):
    def __init__(self):
        """Inicializa a interface do usuário"""
        super().__init__()

        # Configura a janela principal
        self.title("UCAN - Chat com IA")
        self.geometry("1200x800")  # Aumentado para melhor visualização
        self.minsize(800, 600)  # Tamanho mínimo para garantir usabilidade

        # Inicializa gerenciador de temas
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

        # Configura o tema
        ctk.set_appearance_mode(self.theme_manager.current_theme)
        ctk.set_default_color_theme("blue")

        # Configura o grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Frame lateral (contatos)
        self.sidebar = ctk.CTkFrame(
            self,
            width=300,  # Fixed width for better consistency
            corner_radius=0,
            fg_color=self.colors["surface"],
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=0,
            pady=0,
        )

        # Configure grid weights for better responsiveness
        self.sidebar.grid_rowconfigure(
            4, weight=1
        )  # Projects frame gets the extra space
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_propagate(False)  # Prevent auto-resizing

        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.colors["background"],
            border_width=0,
        )
        self.main_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=0,
            pady=0,
        )
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Barra superior
        self.top_bar = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["surface"],
            corner_radius=0,
            height=60,
            border_width=0,
        )
        self.top_bar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=0,
            pady=(0, 1),  # Borda inferior fina
        )
        self.top_bar.grid_propagate(False)
        self.top_bar.grid_columnconfigure(0, weight=1)

        # Container para informações do assistente
        contact_info = ctk.CTkFrame(
            self.top_bar,
            fg_color="transparent",
        )
        contact_info.pack(
            side="left", fill="both", expand=True, padx=LAYOUT["padding"]["medium"]
        )

        # Theme toggle button
        self.theme_button = ctk.CTkButton(
            self.top_bar,
            text="🌙",
            width=36,
            height=36,
            corner_radius=LAYOUT["border_radius"]["circle"],
            font=ctk.CTkFont(size=16),
            fg_color=self.colors["surface_light"],
            hover_color=self.colors["primary"],
            text_color=self.colors["text"],
            command=self.toggle_theme,
        )
        self.theme_button.pack(side="right", padx=LAYOUT["padding"]["medium"])

        # Ícone do assistente
        avatar_size = 36
        self.contact_avatar = ctk.CTkFrame(
            contact_info,
            width=avatar_size,
            height=avatar_size,
            corner_radius=LAYOUT["border_radius"]["circle"],
            fg_color=self.colors["primary"],
        )
        self.contact_avatar.pack(side="left", padx=(0, LAYOUT["padding"]["medium"]))
        self.contact_avatar.pack_propagate(False)

        self.contact_avatar_label = ctk.CTkLabel(
            self.contact_avatar,
            text="🤖",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color=self.colors["text"],
        )
        self.contact_avatar_label.pack(expand=True)

        # Container para nome e status
        contact_text = ctk.CTkFrame(
            contact_info,
            fg_color="transparent",
        )
        contact_text.pack(side="left", fill="both", expand=True)

        # Nome do assistente
        self.contact_name = ctk.CTkLabel(
            contact_text,
            text="Assistente IA",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        self.contact_name.pack(anchor="w")

        # Status do assistente
        self.contact_status = ctk.CTkLabel(
            contact_text,
            text="Pronto para conversar",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.colors["text_secondary"],
            anchor="w",
        )
        self.contact_status.pack(anchor="w")

        # Indicador de "pensando"
        self.thinking_indicator = ThinkingIndicator(contact_text)
        self.thinking_indicator.pack(anchor="w")
        self.thinking_indicator.pack_forget()  # Hide initially

        # Frame de mensagens com overlay para botão de rolagem
        self.messages_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=0,
            fg_color="transparent",
        )
        self.messages_container.grid(
            row=1, column=0, sticky="nsew", padx=LAYOUT["padding"]["medium"]
        )
        self.messages_container.grid_rowconfigure(0, weight=1)
        self.messages_container.grid_columnconfigure(0, weight=1)

        # Frame de mensagens
        self.messages_frame = ScrollableMessageFrame(
            self.messages_container,
            corner_radius=LAYOUT["border_radius"]["medium"],
            fg_color=self.colors["background"],
            scrollbar_fg_color=self.colors["surface"],
            scrollbar_button_color=self.colors["primary"],
            scrollbar_button_hover_color=self.colors["secondary"],
        )
        self.messages_frame.grid(
            row=0, column=0, sticky="nsew", pady=LAYOUT["padding"]["medium"]
        )

        # Botão de rolar para baixo
        self.scroll_button = ctk.CTkButton(
            self.messages_container,
            text="↓",
            width=36,
            height=36,
            corner_radius=LAYOUT["border_radius"]["circle"],
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors["surface"],
            hover_color=self.colors["surface"],
            text_color=self.colors["primary"],
        )
        self.scroll_button.grid(row=0, column=0, sticky="se", padx=20, pady=20)
        self.scroll_button.configure(command=self._scroll_to_bottom)
        self.scroll_button.grid_remove()  # Inicialmente oculto

        # Input frame reorganization
        self.input_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["surface"],
            corner_radius=0,
            height=140,  # Increased for auxiliary buttons
            border_width=0,
        )
        self.input_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=0,
            pady=(1, 0),
        )
        self.input_frame.grid_propagate(False)

        # Container para os widgets de entrada
        input_container = ctk.CTkFrame(
            self.input_frame,
            fg_color="transparent",
        )
        input_container.pack(
            fill="both",
            expand=True,
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["medium"],
        )

        # Frame do input com fundo
        input_background = ctk.CTkFrame(
            input_container,
            fg_color=self.colors["surface_light"],
            corner_radius=LAYOUT["border_radius"]["medium"],
        )
        input_background.pack(
            fill="both",
            expand=True,
            padx=0,
            pady=0,
        )

        # Container principal para texto e botões
        main_input_container = ctk.CTkFrame(
            input_background,
            fg_color="transparent",
        )
        main_input_container.pack(
            fill="both",
            expand=True,
            padx=LAYOUT["padding"]["small"],
            pady=LAYOUT["padding"]["small"],
        )

        # Campo de texto
        self.message_entry = ctk.CTkTextbox(
            main_input_container,
            height=80,  # Increased height
            corner_radius=LAYOUT["border_radius"]["medium"],
            fg_color="transparent",
            border_width=0,
            text_color=self.colors["text"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
            wrap="word",  # Word wrap
        )
        self.message_entry.pack(
            fill="both",
            expand=True,
            padx=0,
            pady=0,
        )

        # Container para botões auxiliares
        aux_buttons = ctk.CTkFrame(
            input_background,
            fg_color="transparent",
            height=32,
        )
        aux_buttons.pack(
            fill="x",
            expand=False,
            padx=LAYOUT["padding"]["small"],
            pady=(0, LAYOUT["padding"]["small"]),
        )

        # Botões de ação à esquerda
        action_buttons = ctk.CTkFrame(
            aux_buttons,
            fg_color="transparent",
        )
        action_buttons.pack(side="left")

        # Botão de anexo
        self.attach_button = ctk.CTkButton(
            action_buttons,
            text="📎",
            width=32,
            height=32,
            corner_radius=LAYOUT["border_radius"]["circle"],
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=self.colors["surface"],
            text_color=self.colors["text_secondary"],
            command=self.show_file_dialog,
        )
        self.attach_button.pack(side="left", padx=(0, 4))

        # Template button
        self.template_button = ctk.CTkButton(
            action_buttons,
            text="📋",
            width=32,
            height=32,
            corner_radius=LAYOUT["border_radius"]["circle"],
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=self.colors["surface"],
            text_color=self.colors["text_secondary"],
            command=self.show_template_dialog,
        )
        self.template_button.pack(side="left")

        # Container direito para contador e botão de enviar
        right_container = ctk.CTkFrame(
            aux_buttons,
            fg_color="transparent",
        )
        right_container.pack(side="right")

        # Contador de tokens mais elegante
        self.char_counter = ctk.CTkLabel(
            right_container,
            text="0",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors["text_secondary"],
            width=40,
            height=20,
            fg_color=self.colors["surface"],
            corner_radius=10,
        )
        self.char_counter.pack(side="left", padx=(0, 8))

        # Botão de enviar mais elegante
        self.send_button = ctk.CTkButton(
            right_container,
            text="",  # Vazio para usar apenas o ícone
            width=32,
            height=32,
            corner_radius=16,  # Metade da largura/altura para garantir círculo perfeito
            font=ctk.CTkFont(size=18),
            fg_color=self.colors["surface"],
            hover_color=self.colors["primary"],
            text_color=self.colors["primary"],
            border_width=1,  # Adiciona borda
            border_color=self.colors["primary"],  # Cor da borda igual ao ícone
            command=self.send_message,
        )
        self.send_button.pack(side="right")

        # Adiciona o ícone de enviar usando um label sobreposto
        send_icon = ctk.CTkLabel(
            self.send_button,
            text="↗",  # Ícone de seta para enviar
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["primary"],
            fg_color="transparent",  # Garante transparência
            width=32,  # Mesma largura do botão
            height=32,  # Mesma altura do botão
        )
        send_icon.place(relx=0.5, rely=0.5, anchor="center")

        # Bind para mudar a cor do ícone no hover
        def on_enter(e):
            send_icon.configure(text_color=self.colors["text_light"])
            self.send_button.configure(
                fg_color=self.colors["primary"],
                border_color=self.colors["primary"],
                hover_color=self.colors["primary_hover"],
            )

        def on_leave(e):
            send_icon.configure(text_color=self.colors["primary"])
            self.send_button.configure(
                fg_color=self.colors["surface"],
                border_color=self.colors["primary"],
                hover_color=self.colors["primary"],
            )

        self.send_button.bind("<Enter>", on_enter)
        self.send_button.bind("<Leave>", on_leave)

        # Bind para efeito de clique
        def on_press(e):
            send_icon.configure(text_color=self.colors["text_light"])
            self.send_button.configure(
                fg_color=self.colors["primary_hover"],
                border_color=self.colors["primary_hover"],
            )

        def on_release(e):
            send_icon.configure(text_color=self.colors["text_light"])
            self.send_button.configure(
                fg_color=self.colors["primary"], border_color=self.colors["primary"]
            )

        self.send_button.bind("<Button-1>", on_press)
        self.send_button.bind("<ButtonRelease-1>", on_release)

        # Placeholder e bindings
        self._add_placeholder()
        self.message_entry.bind("<FocusIn>", self._clear_placeholder)
        self.message_entry.bind("<FocusOut>", self._add_placeholder)
        self.message_entry.bind("<KeyRelease>", self._update_char_count)
        self.message_entry.bind("<Return>", self.handle_enter)

        # Remove duplicate attach button
        if hasattr(self, "attach_btn"):
            self.attach_btn.destroy()
            delattr(self, "attach_btn")

        # Attachment preview frame
        self.attachment_frame = ctk.CTkFrame(
            input_container,
            fg_color=self.colors["surface"],
            corner_radius=LAYOUT["border_radius"]["medium"],
        )
        self.attachment_preview = ctk.CTkLabel(
            self.attachment_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text"],
        )
        self.attachment_preview.pack(side="left", padx=10)

        self.attachment_remove = ctk.CTkButton(
            self.attachment_frame,
            text="❌",
            width=24,
            height=24,
            corner_radius=LAYOUT["border_radius"]["circle"],
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=self.colors["surface"],
            text_color=self.colors["text_secondary"],
            command=self.remove_attachment,
        )
        self.attachment_remove.pack(side="right", padx=5)
        self.attachment_frame.pack_forget()

        # Bind para mostrar/ocultar botão de rolagem
        self.messages_frame.bind("<MouseWheel>", self._check_scroll_position)

        # Inicializa banco de dados
        self.db = Database()

        # Inicializa provedor de AI
        self.ai_provider = AIProvider()

        # Configurações de notificação
        self.notifications_enabled = True

        # Contato atual
        self.current_contact = "Assistente IA"

        # Popula a lista de contatos
        self.populate_contacts()

        # Ícone da janela
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
            if os.path.exists(icon_path):
                self.iconphoto(True, tkinter.PhotoImage(file=icon_path))
        except Exception as e:
            logger.warning(f"Não foi possível carregar o ícone: {str(e)}")

        # Centralizar janela
        self.center_window()

        # Iniciar chat com assistente
        self.after(500, lambda: self.start_chat())

        # Configura o tratamento de entrada
        self.setup_input_handling()

        # Inicializa gerenciador de anexos
        self.attachment_manager = AttachmentManager(self.db)
        self.current_attachment = None

        # Initialize project manager
        self.project_manager = ProjectManager(self.db)
        self.current_project = None

        # Load projects
        self.load_projects()

        logger.info("Aplicação inicializada com sucesso")

    def populate_contacts(self):
        """Popula a lista de contatos"""
        # Frame do logo com gradiente
        self.logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.colors["primary"],
            corner_radius=0,
            height=48,  # Fixed height
            border_width=0,
        )
        self.logo_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=0,
            pady=0,
        )
        self.logo_frame.grid_propagate(False)

        # Logo container para centralização
        logo_container = ctk.CTkFrame(
            self.logo_frame,
            fg_color="transparent",
            height=48,  # Match frame height
        )
        logo_container.pack(expand=True, fill="both")
        logo_container.pack_propagate(False)

        # Logo content container
        logo_content = ctk.CTkFrame(
            logo_container,
            fg_color="transparent",
            height=32,  # Fixed content height
        )
        logo_content.place(relx=0.5, rely=0.5, anchor="center")

        # Logo icon
        logo_icon = ctk.CTkLabel(
            logo_content,
            text="🤖",
            font=ctk.CTkFont(family="Segoe UI", size=20),
            text_color=self.colors["text"],
            height=32,  # Fixed height
        )
        logo_icon.pack(side="left", padx=(0, 8))

        # Logo text
        self.logo_label = ctk.CTkLabel(
            logo_content,
            text="UCAN",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=self.colors["text"],
            height=32,  # Fixed height
        )
        self.logo_label.pack(side="left")

        # Container para título e botão de nova conversa
        chat_header = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )
        chat_header.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=LAYOUT["padding"]["medium"],
            pady=(LAYOUT["padding"]["medium"], LAYOUT["padding"]["small"]),
        )

        # Título da seção
        self.chat_title = ctk.CTkLabel(
            chat_header,
            text="Assistente",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors["text"],
        )
        self.chat_title.pack(side="left")

        # Botão de nova conversa
        new_chat_btn = ctk.CTkButton(
            chat_header,
            text="＋",  # Ícone plus
            width=26,
            height=26,
            corner_radius=13,
            font=ctk.CTkFont(size=16),
            fg_color=self.colors["surface_light"],
            hover_color=self.colors["primary"],
            text_color=self.colors["text"],
            command=self.start_chat,
        )
        new_chat_btn.pack(side="right")

        # Assistente IA
        contact = {
            "name": "Assistente IA",
            "icon": "🤖",
            "description": "Chat principal",
        }

        # Frame do contato
        contact_frame = ctk.CTkFrame(
            self.sidebar,
            corner_radius=LAYOUT["border_radius"]["small"],
            fg_color="transparent",
            height=65,
        )
        contact_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=LAYOUT["padding"]["small"],
            pady=(0, LAYOUT["padding"]["small"]),
        )
        contact_frame.grid_propagate(False)

        # Container para avatar e informações
        info_container = ctk.CTkFrame(
            contact_frame,
            fg_color="transparent",
        )
        info_container.pack(fill="both", expand=True, padx=LAYOUT["padding"]["small"])

        # Avatar
        avatar_size = 36
        avatar_frame = ctk.CTkFrame(
            info_container,
            width=avatar_size,
            height=avatar_size,
            corner_radius=LAYOUT["border_radius"]["circle"],
            fg_color=self.colors["primary"],
        )
        avatar_frame.pack(side="left", padx=(0, LAYOUT["padding"]["small"]))
        avatar_frame.pack_propagate(False)

        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=contact["icon"],
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color=self.colors["text"],
        )
        avatar_label.pack(expand=True)

        # Container para textos
        text_container = ctk.CTkFrame(
            info_container,
            fg_color="transparent",
        )
        text_container.pack(side="left", fill="both", expand=True)

        # Nome do contato
        name_label = ctk.CTkLabel(
            text_container,
            text=contact["name"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        name_label.pack(anchor="w")

        # Descrição
        description_label = ctk.CTkLabel(
            text_container,
            text=contact["description"],
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.colors["text_secondary"],
            anchor="w",
        )
        description_label.pack(anchor="w")

        # Efeito hover no contato
        def create_hover_effect(frame):
            def on_enter(e):
                frame.configure(fg_color=self.colors["surface_light"])

            def on_leave(e):
                frame.configure(fg_color="transparent")

            frame.bind("<Enter>", on_enter)
            frame.bind("<Leave>", on_leave)

        create_hover_effect(contact_frame)

        # Bind para iniciar chat
        contact_frame.bind(
            "<Button-1>",
            lambda e, name=contact["name"]: self.start_chat_with(name),
        )

        # Container para título e botão de novo projeto
        projects_header = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )
        projects_header.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=LAYOUT["padding"]["medium"],
            pady=(LAYOUT["padding"]["medium"], LAYOUT["padding"]["small"]),
        )

        # Título da seção de projetos
        self.projects_title = ctk.CTkLabel(
            projects_header,
            text="Projetos",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors["text"],
        )
        self.projects_title.pack(side="left")

        # Botão de novo projeto
        new_project_btn = ctk.CTkButton(
            projects_header,
            text="＋",  # Ícone plus
            width=26,
            height=26,
            corner_radius=13,
            font=ctk.CTkFont(size=16),
            fg_color=self.colors["surface_light"],
            hover_color=self.colors["primary"],
            text_color=self.colors["text"],
            command=self.show_project_dialog,
        )
        new_project_btn.pack(side="right")

        # Project list
        self.projects_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            corner_radius=0,
            fg_color="transparent",
            border_width=0,
        )
        self.projects_frame.grid(
            row=4,
            column=0,
            sticky="nsew",
            padx=0,
            pady=0,
        )
        self.projects_frame.grid_columnconfigure(0, weight=1)

    def start_chat(self):
        """Inicia o chat com o assistente"""
        try:
            # Limpa o chat
            self.messages_frame.clear_messages()

            # Adiciona mensagem de boas-vindas com animação
            self.after(
                500,
                lambda: self.add_message(
                    "Olá! Sou o UCAN, seu assistente virtual. Como posso ajudar você hoje?",
                    "Assistente IA",
                ),
            )

            # Foca no campo de mensagem
            self.message_entry.focus()

        except Exception as e:
            logger.error(f"Erro ao iniciar chat: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível iniciar o chat.")

    def send_message(self):
        """Envia uma mensagem"""
        message = self.message_entry.get("1.0", "end-1c").strip()
        if not message or message == "Digite sua mensagem...":
            return

        # Clear input and reset placeholder
        self.message_entry.delete("1.0", "end")
        self._add_placeholder()

        # Add user message
        self.add_message(message, "Você")

        # If in a project, save to project
        if self.current_project:
            self.project_manager.add_conversation(
                self.current_project["id"],
                {"sender": "Você", "content": message},
            )

        # Show thinking indicator
        self.contact_status.pack_forget()
        self.thinking_indicator.pack(anchor="w")
        self.thinking_indicator.start()

        # Create thread for API call
        def api_call():
            try:
                # Get AI response
                response = self.ai_provider.get_response(message)

                # Schedule UI updates in main thread
                self.after(0, lambda: self.add_message(response, self.current_contact))
                self.after(0, lambda: self.thinking_indicator.stop())
                self.after(0, lambda: self.thinking_indicator.pack_forget())
                self.after(0, lambda: self.contact_status.pack(anchor="w"))

                # If in a project, save AI response
                if self.current_project:
                    self.after(
                        0,
                        lambda: self.project_manager.add_conversation(
                            self.current_project["id"],
                            {"sender": "Assistente IA", "content": response},
                        ),
                    )

            except Exception as e:
                logger.error(f"Error in API call: {str(e)}")
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", "Failed to get response from AI"
                    ),
                )
                self.after(0, lambda: self.thinking_indicator.stop())
                self.after(0, lambda: self.thinking_indicator.pack_forget())
                self.after(0, lambda: self.contact_status.pack(anchor="w"))

        # Start thread
        threading.Thread(target=api_call, daemon=True).start()

    def add_message(self, message: str, sender: str = "Você"):
        """Adiciona uma mensagem ao chat"""
        try:
            message_frame = self.messages_frame.add_message(message, sender)

            # Botões de ação
            copy_btn = ctk.CTkButton(
                message_frame.winfo_children()[1],  # actions_frame
                text="📋",
                width=24,
                height=24,
                fg_color="transparent",
                hover_color=self.colors["surface"],
                command=lambda: self.copy_message(message),
            )
            copy_btn.grid(row=0, column=0, padx=2)

            edit_btn = ctk.CTkButton(
                message_frame.winfo_children()[1],  # actions_frame
                text="✏️",
                width=24,
                height=24,
                fg_color="transparent",
                hover_color=self.colors["surface"],
                command=lambda: self.edit_message(message_frame),
            )
            edit_btn.grid(row=0, column=1, padx=2)

            delete_btn = ctk.CTkButton(
                message_frame.winfo_children()[1],  # actions_frame
                text="🗑️",
                width=24,
                height=24,
                fg_color="transparent",
                hover_color=self.colors["surface"],
                command=lambda: self.delete_message(message_frame),
            )
            delete_btn.grid(row=0, column=2, padx=2)

            # Esconde os botões inicialmente
            for btn in [copy_btn, edit_btn, delete_btn]:
                btn.grid_remove()

            # Mostra/esconde botões no hover
            def show_actions(event=None):
                for btn in [copy_btn, edit_btn, delete_btn]:
                    btn.grid()

            def hide_actions(event=None):
                if not any(
                    btn.winfo_containing(event.x_root, event.y_root)
                    in [copy_btn, edit_btn, delete_btn]
                    for btn in [copy_btn, edit_btn, delete_btn]
                ):
                    for btn in [copy_btn, edit_btn, delete_btn]:
                        btn.grid_remove()

            message_frame.bind("<Enter>", show_actions)
            message_frame.bind("<Leave>", hide_actions)
            for btn in [copy_btn, edit_btn, delete_btn]:
                btn.bind("<Enter>", show_actions)
                btn.bind("<Leave>", hide_actions)

            # Rola para a última mensagem
            self.messages_frame._scroll_to_bottom()

        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem: {str(e)}")

    def copy_message(self, message):
        """Copia uma mensagem e mostra feedback visual"""
        try:
            # Copia para o clipboard
            self.clipboard_clear()
            self.clipboard_append(message)

            # Feedback visual
            self.after(200, lambda: messagebox.showinfo("Sucesso", "Mensagem copiada!"))

        except Exception as e:
            logger.error(f"Erro ao copiar mensagem: {str(e)}")
            messagebox.showerror(
                "Erro", "Não foi possível copiar a mensagem. Tente novamente."
            )

    def edit_message(self, message_frame):
        """Edita uma mensagem"""
        try:
            # Get original message content
            original_text = (
                message_frame.winfo_children()[0].winfo_children()[0].cget("text")
            )
            original_text = original_text.split("\n", 1)[1]  # Remove sender line

            # Cria um campo de texto para edição
            edit_text = ctk.CTkTextbox(
                message_frame,
                height=60,
                fg_color=self.colors["surface_light"],
                border_width=0,
                text_color=self.colors["text"],
            )
            edit_text.insert("1.0", original_text)
            edit_text.pack(fill="both", expand=True, padx=5, pady=5)
            edit_text.focus()

            def save_edit():
                new_text = edit_text.get("1.0", "end-1c").strip()
                if new_text and new_text != original_text:
                    # Atualiza a mensagem no banco de dados
                    if self.current_project:
                        self.project_manager.update_conversation(
                            self.current_project["id"],
                            {"sender": "Você", "content": new_text},
                        )

                    # Atualiza a UI
                    message_frame.winfo_children()[0].winfo_children()[0].configure(
                        text=f"Você\n{new_text}"
                    )

                # Remove o campo de edição
                edit_text.destroy()
                save_button.destroy()
                cancel_button.destroy()

            def cancel_edit():
                edit_text.destroy()
                save_button.destroy()
                cancel_button.destroy()

            # Botões de salvar e cancelar
            button_frame = ctk.CTkFrame(
                message_frame,
                fg_color="transparent",
            )
            button_frame.pack(fill="x", padx=5, pady=(0, 5))

            save_button = ctk.CTkButton(
                button_frame,
                text="Salvar",
                width=60,
                height=24,
                command=save_edit,
            )
            save_button.pack(side="right", padx=2)

            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancelar",
                width=60,
                height=24,
                fg_color=self.colors["surface"],
                hover_color=self.colors["surface_light"],
                command=cancel_edit,
            )
            cancel_button.pack(side="right", padx=2)

        except Exception as e:
            logger.error(f"Erro ao editar mensagem: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível editar a mensagem.")

    def delete_message(self, message_frame):
        """Deleta uma mensagem"""
        try:
            if messagebox.askyesno(
                "Confirmar exclusão",
                "Tem certeza que deseja excluir esta mensagem?",
            ):
                message_frame.destroy()
                # TODO: Atualizar no banco de dados
        except Exception as e:
            logger.error(f"Erro ao deletar mensagem: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível deletar a mensagem.")

    def show_file_dialog(self):
        """Mostra o diálogo de seleção de arquivo"""
        try:
            # Desabilita o botão de envio durante o upload
            self.send_button.configure(state="disabled")

            # Mostra feedback visual
            self.contact_status.configure(text="Selecionando arquivo...")

            # Abre o diálogo
            file_path = filedialog.askopenfilename(
                title="Selecione um arquivo",
                filetypes=[
                    ("Todos os arquivos", "*.*"),
                    ("Arquivos de texto", "*.txt"),
                    ("Arquivos PDF", "*.pdf"),
                    ("Arquivos de código", "*.py;*.js;*.html;*.css"),
                ],
            )

            if file_path:
                # Atualiza status
                self.contact_status.configure(text="Processando arquivo...")

                # Processa o arquivo
                file_type = os.path.splitext(file_path)[1]
                response = self.ai_provider.analyze_file(file_path, file_type)

                # Adiciona mensagem com o arquivo
                self.add_message(
                    f"Arquivo: {os.path.basename(file_path)}", "Você", True
                )
                self.after(1000, lambda: self.add_message(response, "Assistente IA"))

                # Salva no banco de dados
                self.db.save_message(
                    "Você",
                    self.current_contact,
                    f"Arquivo: {os.path.basename(file_path)}",
                )
                self.db.save_message("Assistente IA", self.current_contact, response)

            # Restaura o status
            self.contact_status.configure(text="Pronto para conversar")

        except Exception as e:
            logger.error(f"Erro ao processar arquivo: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível processar o arquivo.")
        finally:
            # Reabilita o botão de envio
            self.send_button.configure(state="normal")

    def handle_enter(self, event):
        """Trata o pressionamento da tecla Enter"""
        if not event.state & 0x1:  # Shift não está pressionado
            self.send_message()
            return "break"  # Previne quebra de linha

    def center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _add_placeholder(self, event=None):
        """Adiciona placeholder quando o campo está vazio"""
        if not self.message_entry.get("1.0", "end-1c").strip():
            self.message_entry.delete("1.0", "end")
            self.message_entry.insert("1.0", "Envie uma mensagem...")
            self.message_entry.configure(text_color=self.colors["text_secondary"])

    def _clear_placeholder(self, event=None):
        """Remove placeholder quando o campo recebe foco"""
        if self.message_entry.get("1.0", "end-1c").strip() == "Envie uma mensagem...":
            self.message_entry.delete("1.0", "end")
            self.message_entry.configure(text_color=self.colors["text"])

    def _update_char_count(self, event=None):
        """Atualiza o contador de caracteres"""
        try:
            if (
                self.message_entry.get("1.0", "end-1c").strip()
                == "Envie uma mensagem..."
            ):
                count = 0
            else:
                count = len(self.message_entry.get("1.0", "end-1c"))

            # Atualiza o contador com animação
            self.char_counter.configure(
                text=str(count),
                fg_color=self.colors["surface"]
                if count <= 2000
                else self.colors["error"],
                text_color=self.colors["text_secondary"]
                if count <= 2000
                else self.colors["text_light"],
            )

            # Atualiza o estado do botão
            self.send_button.configure(
                state="normal" if count <= 2000 and count > 0 else "disabled",
                fg_color=self.colors["primary"]
                if count <= 2000 and count > 0
                else self.colors["surface"],
            )

        except Exception as e:
            logger.error(f"Erro ao atualizar contador: {str(e)}")

    def setup_input_handling(self):
        """Configura os atalhos de teclado"""
        # Send message
        self.bind("<Control-Return>", lambda e: self.send_message())

        # New chat
        self.bind("<Control-n>", lambda e: self.start_chat())

        # Clear chat
        self.bind("<Control-l>", lambda e: self.messages_frame.clear_messages())

        # Toggle theme
        self.bind("<Control-t>", lambda e: self.toggle_theme())

        # Export chat
        self.bind("<Control-e>", lambda e: self.export_chat())

        # Message history navigation
        self.bind("<Control-Up>", self._previous_message)
        self.bind("<Control-Down>", self._next_message)

    def _previous_message(self, event=None):
        """Navega para a mensagem anterior no histórico"""
        if not hasattr(self, "message_history"):
            return

        if not hasattr(self, "history_index"):
            self.history_index = -1

        if self.history_index < len(self.message_history) - 1:
            self.history_index += 1
            self.message_entry.delete("1.0", "end")
            self.message_entry.insert(
                "1.0", self.message_history[-(self.history_index + 1)]
            )

    def _next_message(self, event=None):
        """Navega para a próxima mensagem no histórico"""
        if not hasattr(self, "message_history") or not hasattr(self, "history_index"):
            return

        if self.history_index > 0:
            self.history_index -= 1
            self.message_entry.delete("1.0", "end")
            self.message_entry.insert(
                "1.0", self.message_history[-(self.history_index + 1)]
            )
        elif self.history_index == 0:
            self.history_index = -1
            self.message_entry.delete("1.0", "end")
            self._add_placeholder()

    def export_chat(self):
        """Exporta o chat atual"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("HTML files", "*.html"),
                    ("All files", "*.*"),
                ],
            )

            if not filename:
                return

            with open(filename, "w", encoding="utf-8") as f:
                if filename.endswith(".html"):
                    f.write("<html><body><div class='chat'>\\n")
                    for msg in self.messages_frame.messages:
                        sender = msg[1].cget("text").split("\\n")[0]
                        content = "\\n".join(msg[1].cget("text").split("\\n")[1:])
                        f.write(f"<div class='message {sender.lower()}'>\\n")
                        f.write(f"<strong>{sender}</strong><br>\\n")
                        f.write(f"{content}\\n</div>\\n")
                    f.write("</div></body></html>")
                else:
                    for msg in self.messages_frame.messages:
                        sender = msg[1].cget("text").split("\\n")[0]
                        content = "\\n".join(msg[1].cget("text").split("\\n")[1:])
                        f.write(f"{sender}:\\n{content}\\n\\n")

            messagebox.showinfo("Sucesso", "Chat exportado com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao exportar chat: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível exportar o chat.")

    def start_chat_with(self, contact_name):
        """Inicia chat com um contato específico"""
        try:
            # Atualiza o contato atual
            self.current_contact = contact_name

            # Atualiza informações do contato
            self.contact_name.configure(text=contact_name)

            # Define ícone baseado no contato
            icons = {
                "Assistente IA": "🤖",
                "Projeto Alpha": "📊",
                "Código Review": "💻",
                "Documentação": "📝",
            }
            self.contact_avatar_label.configure(text=icons.get(contact_name, "👤"))

            # Atualiza cor do avatar
            self.contact_avatar.configure(
                fg_color=self.colors["primary"]
                if contact_name == "Assistente IA"
                else self.colors["secondary"]
            )

            # Limpa o chat
            self.messages_frame.clear_messages()

            # Carrega mensagens do banco de dados
            messages = self.db.get_messages(contact_name)

            # Se não houver mensagens, adiciona mensagem de boas-vindas
            if not messages:
                welcome_messages = {
                    "Assistente IA": "Olá! Sou o UCAN, seu assistente virtual. Como posso ajudar você hoje?",
                    "Projeto Alpha": "Vamos analisar os dados do projeto!",
                    "Código Review": "Pronto para revisar seu código.",
                    "Documentação": "Vamos organizar a documentação!",
                }
                self.after(
                    500,
                    lambda: self.add_message(
                        welcome_messages.get(contact_name, "Olá! Como posso ajudar?"),
                        contact_name,
                    ),
                )
            else:
                # Adiciona mensagens existentes
                for msg in messages:
                    self.add_message(msg["content"], msg["sender"])

            # Atualiza status
            self.contact_status.configure(text="Pronto para conversar")

            # Foca no campo de mensagem
            self.message_entry.focus()

        except Exception as e:
            logger.error(f"Erro ao iniciar chat: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível iniciar o chat.")

    def toggle_theme(self):
        """Alterna o tema da aplicação"""
        ctk.set_appearance_mode(
            "dark" if ctk.get_appearance_mode() == "light" else "light"
        )
        self.theme_manager.apply_theme()

    def _resize_sidebar(self, event):
        """Redimensiona a sidebar"""
        new_width = event.x_root - self.sidebar.winfo_rootx()
        if 180 <= new_width <= 400:  # Min and max width
            self.sidebar.configure(width=new_width)
            self.sidebar.grid_propagate(False)

    def show_template_dialog(self):
        """Shows template management dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Templates")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Template list
        templates_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color="transparent",
        )
        templates_frame.pack(fill="both", expand=True, padx=10, pady=10)

        def load_templates():
            # Clear existing templates
            for widget in templates_frame.winfo_children():
                widget.destroy()

            # Load templates from database
            templates = self.db.get_templates()

            for template in templates:
                template_frame = ctk.CTkFrame(
                    templates_frame,
                    fg_color=self.colors["surface"],
                    corner_radius=LAYOUT["border_radius"]["small"],
                )
                template_frame.pack(fill="x", pady=5)

                # Template name
                name_label = ctk.CTkLabel(
                    template_frame,
                    text=template["name"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                )
                name_label.pack(anchor="w", padx=10, pady=(5, 0))

                # Template content preview
                preview = (
                    template["content"][:100] + "..."
                    if len(template["content"]) > 100
                    else template["content"]
                )
                content_label = ctk.CTkLabel(
                    template_frame,
                    text=preview,
                    wraplength=300,
                )
                content_label.pack(anchor="w", padx=10, pady=(0, 5))

                # Use template button
                use_button = ctk.CTkButton(
                    template_frame,
                    text="Usar",
                    width=60,
                    height=24,
                    command=lambda t=template: self.use_template(t["content"], dialog),
                )
                use_button.pack(side="right", padx=10, pady=5)

        # Add template button
        add_button = ctk.CTkButton(
            dialog, text="+ Novo Template", command=lambda: show_add_dialog(dialog)
        )
        add_button.pack(pady=10)

        def show_add_dialog(parent):
            add_dialog = ctk.CTkToplevel(parent)
            add_dialog.title("Novo Template")
            add_dialog.geometry("400x300")
            add_dialog.transient(parent)
            add_dialog.grab_set()

            # Center dialog
            add_dialog.update_idletasks()
            x = (
                parent.winfo_x()
                + (parent.winfo_width() // 2)
                - (add_dialog.winfo_width() // 2)
            )
            y = (
                parent.winfo_y()
                + (parent.winfo_height() // 2)
                - (add_dialog.winfo_height() // 2)
            )
            add_dialog.geometry(f"+{x}+{y}")

            # Name input
            name_label = ctk.CTkLabel(add_dialog, text="Nome:")
            name_label.pack(anchor="w", padx=10, pady=(10, 0))

            name_entry = ctk.CTkEntry(add_dialog)
            name_entry.pack(fill="x", padx=10, pady=(0, 10))

            # Content input
            content_label = ctk.CTkLabel(add_dialog, text="Conteúdo:")
            content_label.pack(anchor="w", padx=10, pady=(10, 0))

            content_text = ctk.CTkTextbox(add_dialog, height=150)
            content_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

            def save_template():
                name = name_entry.get().strip()
                content = content_text.get("1.0", "end-1c").strip()

                if name and content:
                    self.db.save_template(name, content)
                    add_dialog.destroy()
                    load_templates()

            # Save button
            save_button = ctk.CTkButton(
                add_dialog, text="Salvar", command=save_template
            )
            save_button.pack(pady=10)

        # Load initial templates
        load_templates()

    def use_template(self, content: str, dialog=None):
        """Uses a template"""
        if dialog:
            dialog.destroy()

        self.message_entry.delete("1.0", "end")
        self.message_entry.insert("1.0", content)
        self.message_entry.focus()

    def attach_file(self):
        """Open file dialog to attach a file"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo",
            filetypes=[
                ("All Files", "*.*"),
                ("Images", "*.jpg *.jpeg *.png *.gif"),
                ("Documents", "*.pdf *.doc *.docx"),
                ("Text Files", "*.txt *.md"),
                ("Code Files", "*.py *.js *.html *.css *.json"),
            ],
        )

        if file_path:
            self.process_attachment(file_path)

    def process_attachment(self, file_path):
        """Process an attached file"""
        try:
            # Get file info
            file_info = self.attachment_manager.get_file_info(file_path)

            if not file_info:
                messagebox.showerror("Erro", "Não foi possível processar o arquivo")
                return

            # Process file
            result = self.attachment_manager.process_file(file_path)
            if not result:
                messagebox.showerror("Erro", "Não foi possível processar o arquivo")
                return

            stored_path, mime_type, preview = result

            # Update UI
            self.current_attachment = {
                "path": stored_path,
                "type": mime_type,
                "name": os.path.basename(file_path),
                "preview": preview,
            }

            # Show preview
            if preview and mime_type.startswith(("image/", "application/pdf")):
                img = Image.open(preview)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                self.attachment_preview.configure(image=photo)
                self.attachment_preview.image = photo
            else:
                self.attachment_preview.configure(
                    text=f"📎 {os.path.basename(file_path)}"
                )

            self.attachment_frame.pack(side=ctk.LEFT, fill=ctk.X, expand=True)

        except Exception as e:
            logger.error(f"Error processing attachment: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível processar o arquivo")

    def remove_attachment(self):
        """Remove the current attachment"""
        self.current_attachment = None
        self.attachment_preview.configure(image="", text="")
        self.attachment_frame.pack_forget()

    def _create_gradient(self, frame):
        """Create a gradient effect on a frame"""
        colors = self.theme_manager.get_colors()
        gradient = ctk.CTkCanvas(
            frame,
            height=60,
            bg=colors["primary"],
            highlightthickness=0,
        )
        gradient.pack(fill="both", expand=True)

        # Create gradient effect
        for i in range(60):
            alpha = (60 - i) / 60  # Fade from bottom to top
            color = self._blend_colors(colors["primary"], colors["surface"], alpha)
            gradient.create_line(0, i, frame.winfo_width(), i, fill=color)

    def _blend_colors(self, color1, color2, alpha):
        """Blend two colors with alpha"""
        # Convert colors from hex to RGB
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)

        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)

        # Blend colors
        r = int(r1 * alpha + r2 * (1 - alpha))
        g = int(g1 * alpha + g2 * (1 - alpha))
        b = int(b1 * alpha + b2 * (1 - alpha))

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def show_project_dialog(self, project: Dict = None):
        """Show project creation/edit dialog"""
        dialog = ProjectDialog(self, project=project, on_save=self._handle_project_save)
        dialog.focus()

    def _handle_project_save(self, project_data: Dict):
        """Handle project save"""
        try:
            if "id" in project_data:
                # Update existing project
                self.project_manager.update_project(project_data["id"], project_data)
            else:
                # Create new project
                self.project_manager.create_project(
                    project_data["name"],
                    project_data["description"],
                    project_data["instructions"],
                )

            # Reload projects
            self.load_projects()

        except Exception as e:
            logger.error(f"Error handling project save: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível salvar o projeto.")

    def load_projects(self):
        """Load and display projects"""
        try:
            # Clear existing projects
            for widget in self.projects_frame.winfo_children():
                widget.destroy()

            # Get projects
            projects = self.project_manager.list_projects()

            # Configure scrollbar visibility
            if not projects:
                self.projects_frame._scrollbar.grid_remove()
            else:
                self.projects_frame._scrollbar.grid()

            # Display projects
            for project in projects:
                project_frame = ctk.CTkFrame(
                    self.projects_frame,
                    corner_radius=LAYOUT["border_radius"]["small"],
                    fg_color="transparent",
                    height=65,
                )
                project_frame.pack(
                    fill="x",
                    padx=LAYOUT["padding"]["small"],
                    pady=(0, LAYOUT["padding"]["small"]),
                )
                project_frame.pack_propagate(False)

                # Project info container
                info_container = ctk.CTkFrame(
                    project_frame,
                    fg_color="transparent",
                )
                info_container.pack(
                    fill="both", expand=True, padx=LAYOUT["padding"]["small"]
                )

                # Project icon
                icon_size = 36
                icon_frame = ctk.CTkFrame(
                    info_container,
                    width=icon_size,
                    height=icon_size,
                    corner_radius=LAYOUT["border_radius"]["circle"],
                    fg_color=self.colors["secondary"],
                )
                icon_frame.pack(side="left", padx=(0, LAYOUT["padding"]["small"]))
                icon_frame.pack_propagate(False)

                icon_label = ctk.CTkLabel(
                    icon_frame,
                    text="📁",
                    font=ctk.CTkFont(family="Segoe UI", size=16),
                    text_color=self.colors["text"],
                )
                icon_label.pack(expand=True)

                # Project details
                text_container = ctk.CTkFrame(
                    info_container,
                    fg_color="transparent",
                )
                text_container.pack(side="left", fill="both", expand=True)

                # Project name
                name_label = ctk.CTkLabel(
                    text_container,
                    text=project["name"],
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                    text_color=self.colors["text"],
                    anchor="w",
                )
                name_label.pack(anchor="w")

                # Project description
                desc_label = ctk.CTkLabel(
                    text_container,
                    text=project["description"][:40] + "..."
                    if len(project["description"]) > 40
                    else project["description"],
                    font=ctk.CTkFont(family="Segoe UI", size=11),
                    text_color=self.colors["text_secondary"],
                    anchor="w",
                )
                desc_label.pack(anchor="w")

                # Last updated
                last_updated = ctk.CTkLabel(
                    text_container,
                    text=f"Atualizado {project['updated_at'][:10]}",
                    font=ctk.CTkFont(family="Segoe UI", size=10),
                    text_color=self.colors["text_secondary"],
                    anchor="w",
                )
                last_updated.pack(anchor="w")

                # Project actions container
                actions_container = ctk.CTkFrame(
                    info_container,
                    fg_color="transparent",
                    width=80,
                )
                actions_container.pack(side="right", fill="y")
                actions_container.pack_propagate(False)

                # Edit button
                edit_button = ctk.CTkButton(
                    actions_container,
                    text="✏️",
                    width=26,
                    height=26,
                    corner_radius=13,
                    font=ctk.CTkFont(size=14),
                    fg_color="transparent",
                    hover_color=self.colors["surface"],
                    text_color=self.colors["text_secondary"],
                    command=lambda p=project: self.show_project_dialog(p),
                )
                edit_button.pack(side="left", padx=2)

                # Delete button
                delete_button = ctk.CTkButton(
                    actions_container,
                    text="🗑️",
                    width=26,
                    height=26,
                    corner_radius=13,
                    font=ctk.CTkFont(size=14),
                    fg_color="transparent",
                    hover_color=self.colors["error"],
                    text_color=self.colors["text_secondary"],
                    command=lambda p=project: self.delete_project(p),
                )
                delete_button.pack(side="left", padx=2)

                # Hover effect
                def create_hover_effect(frame, icon_frame):
                    def on_enter(e):
                        frame.configure(fg_color=self.colors["surface_light"])
                        icon_frame.configure(fg_color=self.colors["primary"])

                    def on_leave(e):
                        frame.configure(fg_color="transparent")
                        icon_frame.configure(fg_color=self.colors["secondary"])

                    for widget in [
                        frame,
                        info_container,
                        text_container,
                        name_label,
                        desc_label,
                        last_updated,
                    ]:
                        widget.bind("<Enter>", on_enter)
                        widget.bind("<Leave>", on_leave)
                        widget.bind(
                            "<Button-1>",
                            lambda e, p=project: self.load_project(p),
                        )

                create_hover_effect(project_frame, icon_frame)

            # Check if scrollbar is needed
            self.after(100, self._check_projects_scroll)

        except Exception as e:
            logger.error(f"Error loading projects: {str(e)}")

    def _check_projects_scroll(self):
        """Check if projects scrollbar is needed"""
        try:
            canvas = self.projects_frame._parent_canvas
            if not canvas.winfo_exists():
                return

            # Get canvas and scrollregion sizes
            canvas_height = canvas.winfo_height()
            _, _, _, scroll_height = (
                canvas.bbox("all") if canvas.bbox("all") else (0, 0, 0, 0)
            )

            # Show/hide scrollbar based on content
            if scroll_height <= canvas_height:
                self.projects_frame._scrollbar.grid_remove()
            else:
                self.projects_frame._scrollbar.grid()

        except Exception as e:
            logger.error(f"Error checking projects scroll: {str(e)}")

    def load_project(self, project: Dict):
        """Load a project"""
        try:
            # Update current project
            self.current_project = project

            # Update UI
            self.contact_name.configure(text=project["name"])
            self.contact_status.configure(text="Projeto carregado")

            # Clear messages
            self.messages_frame.clear_messages()

            # Load project conversations
            for conversation in project["conversations"]:
                self.add_message(conversation["content"], conversation["sender"])

            # Update project button text
            self.project_button.configure(text="Editar Projeto")

        except Exception as e:
            logger.error(f"Error loading project: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível carregar o projeto.")

    def _scroll_to_bottom(self):
        """Rola para a última mensagem"""
        try:
            self.messages_frame._scroll_to_bottom()
        except Exception as e:
            logger.error(f"Erro ao rolar para o final: {str(e)}")

    def _check_scroll_position(self, event=None):
        """Verifica a posição da rolagem e mostra/oculta o botão"""
        try:
            canvas = self.messages_frame._parent_canvas
            if not canvas.winfo_exists():
                return

            # Calcula se está próximo do fim
            scroll_position = canvas.yview()
            is_near_bottom = scroll_position[1] > 0.9

            if not is_near_bottom and canvas.yview()[1] < 1.0:
                self.scroll_button.grid()
            else:
                self.scroll_button.grid_remove()
        except Exception as e:
            logger.error(f"Erro ao verificar posição de rolagem: {str(e)}")

    def delete_project(self, project: Dict):
        """Delete a project"""
        try:
            if messagebox.askyesno(
                "Confirmar exclusão",
                f"Tem certeza que deseja excluir o projeto '{project['name']}'?",
            ):
                self.project_manager.delete_project(project["id"])
                self.load_projects()

                if self.current_project and self.current_project["id"] == project["id"]:
                    self.current_project = None
                    self.start_chat()

        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível excluir o projeto.")
