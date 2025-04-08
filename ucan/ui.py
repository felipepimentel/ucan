import logging
import sys
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .attachments import AttachmentManager
from .database import Database
from .llm import LLMProvider
from .projects import ProjectManager
from .theme import ThemeManager
from .widgets import MessagesContainer, ProjectPanel, ThinkingIndicator

logger = logging.getLogger("UCAN")


class ChatApp(ctk.CTk):
    """Interface principal do chat"""

    def __init__(self):
        """Inicializa a interface"""
        super().__init__()

        # Start with window withdrawn (hidden) to prevent showing rendering
        self.withdraw()

        # Initialize managers and state
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()
        self.active_tabs = []
        self.current_tab = None

        # Set language to Portuguese (pt) and don't allow changing
        self.language = "pt"

        # Configure window
        self.title("UCAN")
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Inicializa banco de dados
        self.db = Database()

        # Generate test data if database is empty
        if not self.db.get_all_projects():
            self.db.generate_test_data()

        # Inicializa gerenciador de anexos
        self.attachment_manager = AttachmentManager(self.db)

        # Projeto atual
        self.current_project = None

        # Initialize project manager
        self.project_manager = ProjectManager(self.db)

        # Create placeholder for conversations container to avoid attribute errors
        self.conversations_container = None
        self.projects_container = None

        # Inicializa provedor de AI
        self.ai_provider = LLMProvider()

        # Setup layout
        self.setup_layout()

        # Configurações de notificação
        self.notification_queue = []
        self.is_notification_showing = False

        logger.info("Aplicação inicializada com sucesso")

        # Schedule showing the window when ready (after UI is built and idle)
        self.after(500, self._show_maximized)

        # Iniciar chat com assistente
        self.after(600, lambda: self.start_chat())

        # Flag to track if suggestions have been added
        self.suggestions_added = False

        # Schedule loading of projects and conversations after UI is fully rendered
        self.after(100, self.refresh_sidebar_content)

    def refresh_sidebar_content(self):
        """Refresh sidebar content including projects and conversations"""
        try:
            # Clear and reload projects
            if hasattr(self, "projects_container") and self.projects_container:
                for widget in self.projects_container.winfo_children():
                    widget.destroy()
                self.load_projects()

            # Clear and reload conversations
            if (
                hasattr(self, "conversations_container")
                and self.conversations_container
            ):
                for widget in self.conversations_container.winfo_children():
                    widget.destroy()
                self.list_conversations()

            # Show notification about loaded content
            self.show_notification("Projetos e conversas carregados", "info")
        except Exception as e:
            logger.error(f"Error refreshing sidebar content: {str(e)}")

    def setup_layout(self):
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=self.colors["background"])
        self.main_container.pack(fill="both", expand=True)

        # Content container (sidebar + chat)
        self.content_container = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
        )
        self.content_container.pack(fill="both", expand=True, padx=16, pady=16)

        # Sidebar (wider and with better structure)
        self.setup_sidebar()

        # Chat area with better structure
        self.chat_area = ctk.CTkFrame(
            self.content_container,
            fg_color=self.colors["surface"],
            corner_radius=12,
        )
        self.chat_area.pack(fill="both", expand=True)

        # Chat header with modern look
        self.chat_header = ctk.CTkFrame(
            self.chat_area,
            fg_color=self.colors["surface_light"],
            height=72,
            corner_radius=8,  # Match the new corner radius style
        )
        self.chat_header.pack(fill="x", padx=16, pady=16)
        self.chat_header.pack_propagate(False)

        # Contact info with subtitle
        contact_container = ctk.CTkFrame(
            self.chat_header,
            fg_color="transparent",
        )
        contact_container.pack(side="left", padx=16)

        # Status indicator (green dot)
        status_indicator = ctk.CTkFrame(
            contact_container,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=self.colors["success"],
        )
        status_indicator.place(x=0, y=22)

        self.contact_info = ctk.CTkLabel(
            contact_container,
            text="UCAN Assistant",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text"],
        )
        self.contact_info.pack(anchor="w", padx=(16, 0))

        self.contact_status = ctk.CTkLabel(
            contact_container,
            text="Pronto para ajudar",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_secondary"],
        )
        self.contact_status.pack(anchor="w", padx=(16, 0))

        # Thinking indicator
        self.thinking = ThinkingIndicator(
            self.chat_header,
            fg_color="transparent",
        )
        self.thinking.pack(side="left", padx=8)

        # Messages container
        self.setup_messages_container()

        # Quick actions with button groups
        actions_frame = ctk.CTkFrame(
            self.chat_header,
            fg_color="transparent",
        )
        actions_frame.pack(side="right", padx=16)

        # Group 1: Chat actions in pill shape
        chat_actions = ctk.CTkFrame(
            actions_frame,
            fg_color=self.colors["surface"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
        )
        chat_actions.pack(side="left", padx=8)

        # New chat icon button
        new_chat_btn = ctk.CTkButton(
            chat_actions,
            text="💬",
            width=36,
            height=36,
            corner_radius=0,
            fg_color="transparent",
            hover_color=self.colors["surface_hover"],
            text_color=self.colors["text"],
            command=self.new_chat,
        )
        new_chat_btn.pack(side="left")

        # Add divider
        divider1 = ctk.CTkFrame(
            chat_actions,
            width=1,
            height=20,
            fg_color=self.colors["border"],
        )
        divider1.pack(side="left")

        # Export conversation button
        export_btn = ctk.CTkButton(
            chat_actions,
            text="📤",
            width=36,
            height=36,
            corner_radius=0,
            fg_color="transparent",
            hover_color=self.colors["surface_hover"],
            text_color=self.colors["text"],
            command=self.export_chat,
        )
        export_btn.pack(side="left")

        # Add divider
        divider2 = ctk.CTkFrame(
            chat_actions,
            width=1,
            height=20,
            fg_color=self.colors["border"],
        )
        divider2.pack(side="left")

        # Clear chat button
        clear_btn = ctk.CTkButton(
            chat_actions,
            text="🗑",
            width=36,
            height=36,
            corner_radius=0,
            fg_color="transparent",
            hover_color=self.colors["surface_hover"],
            text_color=self.colors["text"],
            command=self.clear_chat,
        )
        clear_btn.pack(side="left")

        # Tooltip for new chat
        new_chat_tooltip = ctk.CTkLabel(
            self,
            text="Nova conversa",
            fg_color=self.colors["surface"],
            corner_radius=6,
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=12),
            padx=8,
            pady=4,
        )

        # Variables to track tooltip display state
        self.tooltip_showing = False
        self.tooltip_after_id = None

        def on_chat_enter(e):
            # Cancel any existing timer
            if hasattr(self, "tooltip_after_id") and self.tooltip_after_id:
                self.after_cancel(self.tooltip_after_id)

            # Set a timer to show the tooltip after a short delay
            self.tooltip_after_id = self.after(
                300, lambda: show_tooltip(new_chat_btn, new_chat_tooltip)
            )

        def show_tooltip(button, tooltip):
            if hasattr(self, "tooltip_showing") and not self.tooltip_showing:
                self.tooltip_showing = True
                x, y = (
                    button.winfo_rootx(),
                    button.winfo_rooty() - tooltip.winfo_height() - 5,
                )
                tooltip.place(x=x, y=y)

        def on_chat_leave(e):
            # Cancel any pending tooltip display
            if hasattr(self, "tooltip_after_id") and self.tooltip_after_id:
                self.after_cancel(self.tooltip_after_id)
                self.tooltip_after_id = None

            # Hide the tooltip
            new_chat_tooltip.place_forget()
            self.tooltip_showing = False

        new_chat_btn.bind("<Enter>", on_chat_enter)
        new_chat_btn.bind("<Leave>", on_chat_leave)

        # Tooltip for export
        export_tooltip = ctk.CTkLabel(
            self,
            text="Exportar conversa",
            fg_color=self.colors["surface"],
            corner_radius=6,
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=12),
            padx=8,
            pady=4,
        )

        def on_export_enter(e):
            # Cancel any existing timer
            if hasattr(self, "tooltip_after_id") and self.tooltip_after_id:
                self.after_cancel(self.tooltip_after_id)

            # Set a timer to show the tooltip after a short delay
            self.tooltip_after_id = self.after(
                300, lambda: show_tooltip(export_btn, export_tooltip)
            )

        def on_export_leave(e):
            # Cancel any pending tooltip display
            if hasattr(self, "tooltip_after_id") and self.tooltip_after_id:
                self.after_cancel(self.tooltip_after_id)
                self.tooltip_after_id = None

            # Hide the tooltip
            export_tooltip.place_forget()
            self.tooltip_showing = False

        export_btn.bind("<Enter>", on_export_enter)
        export_btn.bind("<Leave>", on_export_leave)

        # Tooltip for clear
        clear_tooltip = ctk.CTkLabel(
            self,
            text="Limpar conversa",
            fg_color=self.colors["surface"],
            corner_radius=6,
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=12),
            padx=8,
            pady=4,
        )

        def on_clear_enter(e):
            # Cancel any existing timer
            if hasattr(self, "tooltip_after_id") and self.tooltip_after_id:
                self.after_cancel(self.tooltip_after_id)

            # Set a timer to show the tooltip after a short delay
            self.tooltip_after_id = self.after(
                300, lambda: show_tooltip(clear_btn, clear_tooltip)
            )

        def on_clear_leave(e):
            # Cancel any pending tooltip display
            if hasattr(self, "tooltip_after_id") and self.tooltip_after_id:
                self.after_cancel(self.tooltip_after_id)
                self.tooltip_after_id = None

            # Hide the tooltip
            clear_tooltip.place_forget()
            self.tooltip_showing = False

        clear_btn.bind("<Enter>", on_clear_enter)
        clear_btn.bind("<Leave>", on_clear_leave)

        # Group 2: Theme toggle
        theme_frame = ctk.CTkFrame(
            actions_frame,
            fg_color=self.colors["surface"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
        )
        theme_frame.pack(side="left", padx=8)

        # Theme toggle button
        theme_btn = ctk.CTkButton(
            theme_frame,
            text="🌙" if self.theme_manager.theme == "light" else "☀️",
            width=36,
            height=36,
            corner_radius=0,
            fg_color="transparent",
            hover_color=self.colors["surface_hover"],
            text_color=self.colors["text"],
            command=self.toggle_theme,
        )
        theme_btn.pack(side="left")

        # Tooltip for theme toggle
        theme_tooltip = ctk.CTkLabel(
            self,
            text="Alternar tema",
            fg_color=self.colors["surface"],
            corner_radius=6,
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=12),
            padx=8,
            pady=4,
        )

        def on_theme_enter(e):
            # Cancel any existing timer
            if hasattr(self, "tooltip_after_id") and self.tooltip_after_id:
                self.after_cancel(self.tooltip_after_id)

            # Set a timer to show the tooltip after a short delay
            self.tooltip_after_id = self.after(
                300, lambda: show_tooltip(theme_btn, theme_tooltip)
            )

        def on_theme_leave(e):
            # Cancel any pending tooltip display
            if hasattr(self, "tooltip_after_id") and self.tooltip_after_id:
                self.after_cancel(self.tooltip_after_id)
                self.tooltip_after_id = None

            # Hide the tooltip
            theme_tooltip.place_forget()
            self.tooltip_showing = False

        theme_btn.bind("<Enter>", on_theme_enter)
        theme_btn.bind("<Leave>", on_theme_leave)

        # Input container with modern design integrated with chat
        self.input_container = ctk.CTkFrame(
            self.chat_area,
            fg_color=self.colors["surface_light"],
            corner_radius=20,  # More rounded
            height=120,  # Increased height for better spacing
            border_width=1,
            border_color=self.colors["border"],
        )
        self.input_container.pack(fill="x", padx=24, pady=(0, 24))
        self.input_container.pack_propagate(False)

        # Simple hover effect to input container
        def on_input_enter(e):
            self.input_container.configure(border_color=self.colors["primary"])

        def on_input_leave(e):
            if not self.text_input.focus_get():
                self.input_container.configure(border_color=self.colors["border"])

        self.input_container.bind("<Enter>", on_input_enter)
        self.input_container.bind("<Leave>", on_input_leave)

        # Text area with clean styling
        text_frame = ctk.CTkFrame(
            self.input_container,
            fg_color="transparent",
        )
        text_frame.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        # Text input with modern styling
        self.text_input = ctk.CTkTextbox(
            text_frame,
            height=70,
            fg_color="transparent",
            border_width=0,
            font=ctk.CTkFont(size=15),
            text_color=self.colors["text"],
        )
        self.text_input.pack(fill="both", expand=True)

        # Add placeholder
        self.is_placeholder = True
        self.text_input.insert("1.0", "Digite sua mensagem aqui...")
        self.text_input.configure(text_color=self.colors["text_secondary"])

        # Bind events for placeholder and character count
        self.text_input.bind("<FocusIn>", self._clear_placeholder)
        self.text_input.bind("<FocusOut>", self._add_placeholder)
        self.text_input.bind("<KeyRelease>", self._update_char_count)

        # Setup keyboard shortcuts
        self.text_input.bind("<Tab>", self._handle_tab)
        self.text_input.bind("<Control-Return>", lambda e: self.send_message())

        # Add character counter
        char_count_frame = ctk.CTkFrame(
            text_frame,
            fg_color="transparent",
            width=100,
            height=20,
        )
        char_count_frame.place(relx=0.99, rely=0.95, anchor="se")

        self.char_count = ctk.CTkLabel(
            char_count_frame,
            text="0/4000",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=12),
        )
        self.char_count.pack(side="right")

        # Toolbar container for all buttons
        toolbar = ctk.CTkFrame(
            self.input_container,
            fg_color="transparent",
            height=40,
        )
        toolbar.pack(fill="x", padx=12, pady=(0, 8))

        # Left side: Action buttons
        left_actions = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        left_actions.pack(side="left")

        # Action buttons with modern look
        action_options = [
            {"icon": "📎", "tooltip": "Anexar arquivo", "command": self.attach_file},
            {
                "icon": "📋",
                "tooltip": "Usar template",
                "command": self.show_template_dialog,
            },
            {"icon": "🌐", "tooltip": "Traduzir", "command": self.translate_text},
        ]

        for option in action_options:
            btn = ctk.CTkButton(
                left_actions,
                text=option["icon"],
                width=36,
                height=36,
                corner_radius=8,
                fg_color=self.colors["surface"],
                hover_color=self.colors["surface_hover"],
                text_color=self.colors["text"],
                command=option["command"],
                border_width=1,
                border_color=self.colors["border"],
            )
            btn.pack(side="left", padx=4)

            # Create tooltip
            tooltip = ctk.CTkLabel(
                self,
                text=option["tooltip"],
                fg_color=self.colors["surface"],
                corner_radius=6,
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=12),
                padx=8,
                pady=4,
            )

            # Show/hide tooltips on hover
            def on_action_enter(e, b=btn, t=tooltip):
                x, y = b.winfo_rootx(), b.winfo_rooty() - t.winfo_height() - 5
                t.place(x=x, y=y)

            def on_action_leave(e, t=tooltip):
                t.place_forget()

            btn.bind("<Enter>", on_action_enter)
            btn.bind("<Leave>", on_action_leave)

        # Center: Format buttons
        center_actions = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        center_actions.place(relx=0.5, rely=0.5, anchor="center")

        # Format buttons
        format_options = [
            {"icon": "B", "tooltip": "Negrito", "format": "bold"},
            {"icon": "I", "tooltip": "Itálico", "format": "italic"},
            {"icon": "~", "tooltip": "Riscado", "format": "strikethrough"},
            {"icon": "`", "tooltip": "Código", "format": "code"},
            {"icon": "•", "tooltip": "Lista", "format": "list"},
            {"icon": "1.", "tooltip": "Lista numerada", "format": "numbered_list"},
            {"icon": ">", "tooltip": "Citação", "format": "quote"},
        ]

        # Create format buttons group
        format_group = ctk.CTkFrame(
            center_actions,
            fg_color=self.colors["surface"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
        )
        format_group.pack()

        for i, option in enumerate(format_options):
            btn = ctk.CTkButton(
                format_group,
                text=option["icon"],
                width=36,
                height=36,
                corner_radius=0,
                fg_color="transparent",
                hover_color=self.colors["surface_hover"],
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda fmt=option["format"]: self.format_text(fmt),
                border_width=0,
            )
            btn.pack(side="left")

            # Add separators between buttons
            if i < len(format_options) - 1:
                separator = ctk.CTkFrame(
                    format_group,
                    width=1,
                    height=20,
                    fg_color=self.colors["border"],
                )
                separator.pack(side="left")

            # Create tooltip
            tooltip = ctk.CTkLabel(
                self,
                text=option["tooltip"],
                fg_color=self.colors["surface"],
                corner_radius=6,
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=12),
                padx=8,
                pady=4,
            )

            # Show/hide tooltips on hover
            def on_format_enter(e, b=btn, t=tooltip):
                x, y = b.winfo_rootx(), b.winfo_rooty() - t.winfo_height() - 5
                t.place(x=x, y=y)

            def on_format_leave(e, t=tooltip):
                t.place_forget()

            btn.bind("<Enter>", on_format_enter)
            btn.bind("<Leave>", on_format_leave)

        # Right side: Send button
        right_actions = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        right_actions.pack(side="right")

        # Send button with improved design
        self.send_btn = ctk.CTkButton(
            right_actions,
            text="Enviar",
            width=100,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_dark"],
            text_color=self.colors["text_light"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.send_message,
        )
        # Use place instead of pack for more precise alignment
        self.send_btn.pack(side="right")

        # Send icon inside button
        self.send_icon = ctk.CTkLabel(
            self.send_btn,
            text="→",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_light"],
        )
        self.send_icon.place(relx=0.85, rely=0.5, anchor="center")

        # Character counter with better positioning - moved to avoid overlapping
        self.char_counter = ctk.CTkLabel(
            toolbar,  # Attach to toolbar instead of input_container
            text="0/4000",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"],
        )
        self.char_counter.pack(
            side="left", padx=(16, 0)
        )  # Position on left side of toolbar

        # Handle focus events with improved styling
        def on_entry_focus_in(event):
            if self.text_input.get("1.0", "end-1c") == "Digite sua mensagem...":
                self.text_input.delete("1.0", "end")
                self.text_input.configure(text_color=self.colors["text"])

            # Update border color with subtle glow effect
            self.input_container.configure(
                border_color=self.colors["primary"], border_width=2
            )

        def on_entry_focus_out(event):
            if not self.text_input.get("1.0", "end-1c").strip():
                self.text_input.insert("1.0", "Digite sua mensagem...")
                self.text_input.configure(text_color=self.colors["text_secondary"])

            # Reset border
            self.input_container.configure(
                border_color=self.colors["border"], border_width=1
            )

        self.text_input.bind("<FocusIn>", on_entry_focus_in)
        self.text_input.bind("<FocusOut>", on_entry_focus_out)

        # Initial placeholder text
        self.text_input.insert("1.0", "Digite sua mensagem...")
        self.text_input.configure(text_color=self.colors["text_secondary"])

        # Setup placeholder state
        self._placeholder_visible = True

        # Setup key bindings
        self.setup_input_handling()

        # Update character counter
        def update_counter(event=None):
            text = self.text_input.get("1.0", "end-1c")
            # Don't count placeholder text
            if text == "Digite sua mensagem...":
                count = 0
                self._placeholder_visible = True
            else:
                count = len(text)
                self._placeholder_visible = False

            # Update counter with nice formatting
            self.char_counter.configure(text=f"{count}/4000")

            # Change color based on length
            if count > 3500:
                self.char_counter.configure(text_color=self.colors["error"])
            elif count > 3000:
                self.char_counter.configure(text_color=self.colors["warning"])
            else:
                self.char_counter.configure(text_color=self.colors["text_secondary"])

            # Limit text length
            if count > 4000:
                self.text_input.delete("1.0+4000c", "end")

            # Update send button state
            if hasattr(self, "send_btn"):
                self.send_btn.configure(
                    state="normal"
                    if count > 0 and text != "Digite sua mensagem..."
                    else "disabled"
                )

        # Character counter
        self.text_input.bind("<KeyRelease>", update_counter)

        # Add hover animation for send button
        def on_send_enter(e):
            self.send_icon.configure(font=ctk.CTkFont(size=18, weight="bold"))
            self.send_btn.configure(fg_color=self.colors["primary_dark"])

        def on_send_leave(e):
            self.send_icon.configure(font=ctk.CTkFont(size=16, weight="bold"))
            self.send_btn.configure(fg_color=self.colors["primary"])

        self.send_btn.bind("<Enter>", on_send_enter)
        self.send_btn.bind("<Leave>", on_send_leave)

        # Disable button initially if no text
        self.send_btn.configure(state="disabled")

    def _update_char_count(self, event=None):
        """Update character counter"""
        try:
            count = len(self.text_input.get("1.0", "end-1c"))
            self.char_counter.configure(text=f"{count}/4000")

            # Update send button state
            self.send_btn.configure(state="normal" if count > 0 else "disabled")

        except Exception as e:
            logger.error(f"Error updating char count: {str(e)}")

    def send_message(self, event=None):
        """Send a message from the input field"""
        try:
            # Check if placeholder is visible
            if hasattr(self, "is_placeholder") and self.is_placeholder:
                return

            # Get message text
            message = self.text_input.get("1.0", "end-1c").strip()

            # Validate message
            if not message:
                return

            # Add message to UI
            self.add_message(message, "Você")

            # Save message to database if we have a current conversation
            if hasattr(self, "current_conversation") and self.current_conversation:
                conversation_id = self.current_conversation["id"]
                self.project_manager.add_message(conversation_id, message, "Você")

            # Clear input
            self.text_input.delete("1.0", "end")
            self._update_char_count()

            # Focus on input
            self.text_input.focus_set()

            # Start thinking animation
            self.thinking.start()

            # Process with AI (simulated delay)
            self.after(1500, lambda: self._process_message(message))

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            messagebox.showerror("Error", "Erro ao enviar mensagem. Tente novamente.")

    def format_text(self, format_type):
        """Format selected text in the input field"""
        # Clear placeholder if present
        if hasattr(self, "is_placeholder") and self.is_placeholder:
            self._clear_placeholder()

        try:
            # Get selected text
            selected_range = self.text_input.tag_ranges("sel")
            if selected_range:
                start_index = selected_range[0]
                end_index = selected_range[1]
                selected_text = self.text_input.get(start_index, end_index)

                # Apply formatting based on type
                formatted_text = ""
                if format_type == "bold":
                    formatted_text = f"**{selected_text}**"
                elif format_type == "italic":
                    formatted_text = f"*{selected_text}*"
                elif format_type == "strikethrough":
                    formatted_text = f"~~{selected_text}~~"
                elif format_type == "code":
                    if "\n" in selected_text:
                        formatted_text = f"```\n{selected_text}\n```"
                    else:
                        formatted_text = f"`{selected_text}`"
                elif format_type == "list":
                    lines = selected_text.split("\n")
                    formatted_lines = [f"• {line}" for line in lines]
                    formatted_text = "\n".join(formatted_lines)
                elif format_type == "numbered_list":
                    lines = selected_text.split("\n")
                    formatted_lines = [
                        f"{i + 1}. {line}" for i, line in enumerate(lines)
                    ]
                    formatted_text = "\n".join(formatted_lines)
                elif format_type == "quote":
                    lines = selected_text.split("\n")
                    formatted_lines = [f"> {line}" for line in lines]
                    formatted_text = "\n".join(formatted_lines)
                else:
                    formatted_text = selected_text

                # Replace selected text with formatted text
                self.text_input.delete(start_index, end_index)
                self.text_input.insert(start_index, formatted_text)
            else:
                # Insert formatting markers at cursor position
                cursor_position = self.text_input.index("insert")

                if format_type == "bold":
                    self.text_input.insert(cursor_position, "****")
                    self.text_input.mark_set("insert", "insert-2c")
                elif format_type == "italic":
                    self.text_input.insert(cursor_position, "**")
                    self.text_input.mark_set("insert", "insert-1c")
                elif format_type == "strikethrough":
                    self.text_input.insert(cursor_position, "~~~~")
                    self.text_input.mark_set("insert", "insert-2c")
                elif format_type == "code":
                    self.text_input.insert(cursor_position, "``")
                    self.text_input.mark_set("insert", "insert-1c")
                elif format_type == "list":
                    self.text_input.insert(cursor_position, "• ")
                elif format_type == "numbered_list":
                    self.text_input.insert(cursor_position, "1. ")
                elif format_type == "quote":
                    self.text_input.insert(cursor_position, "> ")
        except Exception as e:
            logger.error(f"Error formatting text: {str(e)}")

        # Update character count
        self._update_char_count()

        # Focus back on input
        self.text_input.focus_set()

    def attach_file(self):
        """Attach file to message"""
        # Implement file attachment logic
        pass

    def use_template(self, content: str = None, dialog=None):
        """Insert template content into the message input"""
        # If called without content, show the template dialog
        if not content:
            self.show_template_dialog()
            return

        # Close dialog if provided
        if dialog and dialog.winfo_exists():
            dialog.destroy()

        # Clear placeholder if present
        if hasattr(self, "is_placeholder") and self.is_placeholder:
            self._clear_placeholder()

        # Insert template content
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", content)

        # Update character count
        self._update_char_count()

    def new_chat(self):
        """Start new chat"""
        try:
            # Create a new conversation in the database
            conversation_id = self.project_manager.create_conversation(
                f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )

            if conversation_id:
                # Set current conversation
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
                )
                self.current_conversation = dict(cursor.fetchone())

                # Clear current project
                self.current_project = None

                # Update header
                self.contact_info.configure(text="Nova conversa")
                self.contact_status.configure(text="Iniciando...")

            # Clear messages
            if hasattr(self.messages_container, "clear_messages"):
                self.messages_container.clear_messages()

            # Clear text field
            self.text_input.delete("1.0", "end")
            self._update_char_count()

            # Initialize chat with welcome message
            self.start_chat()

        except Exception as e:
            logger.error(f"Error starting new chat: {str(e)}")
            messagebox.showerror(
                "Erro", f"Não foi possível iniciar nova conversa: {str(e)}"
            )

    def export_chat(self):
        """Export chat history"""
        # Implement export logic
        pass

    def clear_chat(self):
        """Clear all messages in chat"""
        try:
            # Ask for confirmation
            if messagebox.askyesno(
                "Limpar Chat", "Tem certeza que deseja limpar o chat?"
            ):
                # Clear messages
                self.messages_container.clear_messages()

                # Add start message
                self.start_chat()

        except Exception as e:
            logger.error(f"Error clearing chat: {str(e)}")

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        # Toggle theme using theme manager
        colors = self.theme_manager.toggle_theme()
        self.colors = colors

        # Apply new colors to all UI elements
        self._apply_theme_colors()

        # Show theme change notification
        theme_name = "Light" if self.theme_manager.theme == "light" else "Dark"
        self.show_notification(f"{theme_name} theme activated", "info")

    def show_notification(self, message, type="info", duration=3000):
        """Show a notification message"""
        # Define notification colors based on type
        colors = {
            "info": self.colors["primary"],
            "success": self.colors["success"],
            "warning": self.colors["warning"],
            "error": self.colors["error"],
        }
        bg_color = colors.get(type, self.colors["primary"])

        # Create notification frame
        notification = ctk.CTkFrame(
            self, corner_radius=8, fg_color=bg_color, width=300, height=50
        )

        # Add notification text
        notification_text = ctk.CTkLabel(
            notification,
            text=message,
            text_color=self.colors["text_light"],
            font=ctk.CTkFont(size=14),
        )
        notification_text.place(relx=0.5, rely=0.5, anchor="center")

        # Position notification at the top center of the window
        notification.place(relx=0.5, rely=0.05, anchor="n")

        # Auto-hide notification after duration
        self.after(duration, lambda: notification.destroy())

    def show_project_panel(self, project=None):
        """Show project panel"""
        try:
            panel = ProjectPanel(
                self,
                project=project,
                on_save=self.save_project,
            )
            panel.show()

        except Exception as e:
            logger.error(f"Error showing project panel: {str(e)}")

    def save_project(self, project_data):
        """Save project"""
        try:
            # Save or update project in database
            if "id" in project_data and project_data["id"]:
                # Update existing project
                success = self.project_manager.update_project(
                    project_data["id"], project_data
                )
            else:
                # Create new project
                project_id = self.project_manager.create_project(
                    project_data["name"],
                    project_data["description"],
                    project_data.get("instructions", ""),
                )
                success = project_id is not None

            if success:
                # Refresh projects list
                self.load_projects()

            return success
        except Exception as e:
            logger.error(f"Error saving project: {str(e)}")
            return False

    def start_chat(self):
        """Inicia o chat com o assistente"""
        try:
            # Limpa o chat
            if hasattr(self.messages_container, "clear_messages"):
                self.messages_container.clear_messages()
                # Reset suggestions flag when clearing messages
                self.suggestions_added = False

            # Adiciona mensagem de boas-vindas com animação
            self.after(
                500,
                lambda: self.add_message(
                    "👋 Olá! Sou o UCAN, seu assistente virtual.\n\n"
                    "Estou aqui para ajudar você com:\n"
                    "• Respostas para suas perguntas\n"
                    "• Gerenciamento de projetos\n"
                    "• Uso de templates de mensagem\n"
                    "• Análise de informações\n\n"
                    "Como posso ajudar você hoje?",
                    "Assistente",
                ),
            )

            # Add suggestions section only if not already added
            if not self.suggestions_added:
                # Explicitly add welcome suggestions after clearing
                self.messages_container._add_welcome_suggestions()
                self.suggestions_added = True

            # Foca no campo de mensagem
            self.text_input.focus()

        except Exception as e:
            logger.error(f"Erro ao iniciar chat: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível iniciar o chat.")

    def add_suggestions(self, suggestions):
        """Add suggestion buttons to the chat"""
        try:
            # Create suggestions container
            suggestions_container = ctk.CTkFrame(
                self.messages_container,
                fg_color="transparent",
            )

            # Add suggestions label
            suggestions_label = ctk.CTkLabel(
                suggestions_container,
                text="Sugestões para começar:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text_secondary"],
            )
            suggestions_label.pack(anchor="w", pady=(16, 8))

            # Create buttons container with flexbox-like layout
            buttons_container = ctk.CTkFrame(
                suggestions_container,
                fg_color="transparent",
            )
            buttons_container.pack(fill="x")

            # Create two rows for better organization
            for i in range(2):
                row_frame = ctk.CTkFrame(
                    buttons_container,
                    fg_color="transparent",
                )
                row_frame.pack(fill="x", pady=4)

                # Add two buttons per row
                for j in range(2):
                    idx = i * 2 + j
                    if idx < len(suggestions):
                        btn = ctk.CTkButton(
                            row_frame,
                            text=suggestions[idx],
                            height=36,
                            corner_radius=8,
                            fg_color=self.colors["surface"],
                            hover_color=self.colors["surface_hover"],
                            text_color=self.colors["text"],
                            border_width=1,
                            border_color=self.colors["border"],
                            command=lambda s=suggestions[idx]: self.handle_suggestion(
                                s
                            ),
                        )
                        btn.pack(
                            side="left",
                            padx=(0 if j == 0 else 8, 0),
                            fill="x",
                            expand=True,
                        )

            # Add the container to messages
            if hasattr(self.messages_container, "add_widget"):
                self.messages_container.add_widget(suggestions_container)

        except Exception as e:
            logger.error(f"Error adding suggestions: {str(e)}")

    def start_chat_with(self, name: str):
        """Start chat with a specific contact"""
        try:
            # Update current contact
            self.current_contact = name
            self.contact_name.configure(text=name)
            self.contact_status.configure(text="Pronto para conversar")

            # Clear messages
            self.messages_frame.clear_messages()

            # Add welcome message
            self.after(
                500,
                lambda: self.add_message(
                    "Olá! Sou o UCAN, seu assistente virtual. Como posso ajudar você hoje?",
                    name,
                ),
            )

            # Focus on message entry
            self.message_entry.focus()

        except Exception as e:
            logger.error(f"Error starting chat with {name}: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível iniciar o chat.")

    def add_message(self, text, sender):
        """Add a message to the conversation"""
        try:
            # Use the messages_container if it exists
            if hasattr(self, "messages_container") and hasattr(
                self.messages_container, "add_message"
            ):
                is_user = sender != "UCAN Assistant"
                self.messages_container.add_message(text, is_user=is_user)
            else:
                # Fallback implementation
                logger.warning("Messages container not available, using fallback")
                # Here we would implement a fallback method to display messages
                pass

        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            messagebox.showerror("Error", "Erro ao exibir mensagem.")

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
                border_width=1,
                border_color=self.colors["border"],
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
            self.send_btn.configure(state="disabled")

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
                self.process_attachment(file_path)

        except Exception as e:
            logger.error(f"Erro ao abrir diálogo de arquivo: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível abrir o diálogo de arquivo.")
        finally:
            # Reabilita o botão de envio
            self.send_btn.configure(state="normal")
            # Restaura o status
            self.contact_status.configure(text="Pronto para conversar")

    def setup_input_handling(self):
        """Setup input field key bindings"""
        # Handle Enter to send message
        self.text_input.bind("<Return>", self.handle_enter)
        self.text_input.bind("<KP_Enter>", self.handle_enter)

        # Ctrl+Enter for new line
        self.text_input.bind("<Control-Return>", lambda e: True)

        # Character counter
        self.text_input.bind("<KeyRelease>", self._update_char_count)

        # Up/down arrows for message history
        self.text_input.bind("<Up>", self._previous_message)
        self.text_input.bind("<Down>", self._next_message)

    def handle_enter(self, event):
        """Trata o pressionamento da tecla Enter"""
        if not event.state & 0x1:  # Shift não está pressionado
            self.send_message()
            return "break"  # Previne quebra de linha

    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _add_placeholder(self, event=None):
        """Add placeholder to text input"""
        if not self.text_input.get("1.0", "end-1c").strip():
            self.text_input.insert("1.0", "Digite sua mensagem...")
            self.text_input.configure(text_color=self.colors["text_secondary"])

    def _clear_placeholder(self, event=None):
        """Clear placeholder from text input"""
        if self.text_input.get("1.0", "end-1c") == "Digite sua mensagem...":
            self.text_input.delete("1.0", "end")
            self.text_input.configure(text_color=self.colors["text"])

    def _scroll_to_bottom(self):
        """Scroll messages to bottom"""
        try:
            if hasattr(self.messages_container, "_scroll_to_bottom"):
                self.messages_container._scroll_to_bottom()
        except Exception as e:
            logger.error(f"Error scrolling to bottom: {str(e)}")

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

    def show_template_dialog(self):
        """Show template selection dialog"""
        # This is a placeholder for the actual implementation
        messagebox.showinfo(
            "Templates", "Templates functionality will be available in a future update."
        )

    def setup_sidebar(self):
        """Creates the sidebar with projects and conversations"""
        # Sidebar container
        self.sidebar = ctk.CTkFrame(
            self.content_container,
            fg_color=self.colors["surface"],
            corner_radius=12,
            width=300,
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 16))
        self.sidebar.pack_propagate(False)

        # Sidebar header
        sidebar_header = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=72,
        )
        sidebar_header.pack(fill="x", padx=16, pady=16)

        # App logo and name
        app_title = ctk.CTkLabel(
            sidebar_header,
            text="UCAN",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["primary"],
        )
        app_title.pack(side="left")

        # Sidebar content with scrollable area
        sidebar_content = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
        )
        sidebar_content.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Search bar
        search_container = ctk.CTkFrame(
            sidebar_content,
            fg_color=self.colors["surface_light"],
            corner_radius=8,
            height=40,
        )
        search_container.pack(fill="x", padx=8, pady=8)

        search_icon = ctk.CTkLabel(
            search_container,
            text="🔍",
            width=20,
            text_color=self.colors["text_secondary"],
        )
        search_icon.pack(side="left", padx=(10, 0))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._handle_search)

        search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Search projects and chats...",
            border_width=0,
            fg_color="transparent",
            text_color=self.colors["text"],
            placeholder_text_color=self.colors["text_secondary"],
            textvariable=self.search_var,
        )
        search_entry.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Projects section (collapsible)
        self.projects_container = self._create_collapsible_section(
            sidebar_content, "Projetos", True
        )

        # Load projects - this will also add the New Project button
        self.load_projects()

        # Conversations section (collapsible)
        self.conversations_container = self._create_collapsible_section(
            sidebar_content, "Conversas", True
        )

        # Load conversations - this will also add the New Chat button
        self.list_conversations()

        # Settings section (collapsible)
        self.settings_container = self._create_collapsible_section(
            sidebar_content, "Settings", False
        )

        # Dark/Light theme toggle
        theme_btn = ctk.CTkButton(
            self.settings_container,
            text="🌓 Theme",
            fg_color=self.colors["surface_light"],
            text_color=self.colors["text"],
            hover_color=self.colors["surface_hover"],
            corner_radius=8,
            height=40,
            command=self.toggle_theme,
        )
        theme_btn.pack(fill="x", padx=8, pady=4)

        # User profile button
        profile_btn = ctk.CTkButton(
            self.settings_container,
            text="👤 Profile",
            fg_color=self.colors["surface_light"],
            text_color=self.colors["text"],
            hover_color=self.colors["surface_hover"],
            corner_radius=8,
            height=40,
            command=self.show_profile,
        )
        profile_btn.pack(fill="x", padx=8, pady=4)

        # Keyboard shortcuts button
        shortcuts_btn = ctk.CTkButton(
            self.settings_container,
            text="⌨️ Shortcuts",
            fg_color=self.colors["surface_light"],
            text_color=self.colors["text"],
            hover_color=self.colors["surface_hover"],
            corner_radius=8,
            height=40,
            command=self.show_shortcuts,
        )
        shortcuts_btn.pack(fill="x", padx=8, pady=4)

    def _add_new_project_button(self):
        """Add new project button to the projects container"""
        # Add "New Project" button at the top of the projects section
        new_project_container = ctk.CTkFrame(
            self.projects_container,
            fg_color=self.colors["surface_light"],
            corner_radius=8,
            height=50,
        )
        new_project_container.pack(fill="x", padx=8, pady=(0, 8))

        new_project_button = ctk.CTkButton(
            new_project_container,
            text="+ Novo Projeto",
            font=ctk.CTkFont(size=14),
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_dark"],
            text_color=self.colors["text_light"],
            command=lambda: self.show_project_panel(),
        )
        new_project_button.pack(fill="x", padx=8, pady=7)

    def _add_new_chat_button(self):
        """Add new chat button to the conversations container"""
        # Add "New Chat" button at the top of the conversations section
        new_chat_container = ctk.CTkFrame(
            self.conversations_container,
            fg_color=self.colors["surface_light"],
            corner_radius=8,
            height=50,
        )
        new_chat_container.pack(fill="x", padx=8, pady=(0, 8))

        new_chat_button = ctk.CTkButton(
            new_chat_container,
            text="+ Nova Conversa",
            font=ctk.CTkFont(size=14),
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_dark"],
            text_color=self.colors["text_light"],
            command=self.new_chat,
        )
        new_chat_button.pack(fill="x", padx=8, pady=7)

    def _create_collapsible_section(self, parent, title, expanded=True):
        """Creates a collapsible section for the sidebar"""
        # Section container
        section = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        section.pack(fill="x", pady=4)

        # Header with toggle
        header = ctk.CTkFrame(
            section,
            fg_color="transparent",
        )
        header.pack(fill="x")

        # Toggle icon
        toggle_icon = "▼" if expanded else "▶"
        toggle_btn = ctk.CTkButton(
            header,
            text=toggle_icon,
            width=20,
            fg_color="transparent",
            hover_color=self.colors["surface_hover"],
            text_color=self.colors["text"],
            corner_radius=4,
        )
        toggle_btn.pack(side="left", padx=(8, 0))

        # Section title
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"],
        )
        title_label.pack(side="left", padx=8)

        # Content container (hidden when collapsed)
        content = ctk.CTkFrame(
            section,
            fg_color="transparent",
        )
        if expanded:
            content.pack(fill="x", pady=(8, 0))

        # Configure toggle button
        def toggle_section():
            nonlocal expanded
            expanded = not expanded
            toggle_btn.configure(text="▼" if expanded else "▶")
            if expanded:
                content.pack(fill="x", pady=(8, 0))
            else:
                content.pack_forget()

        toggle_btn.configure(command=toggle_section)

        return content

    def _handle_search(self, *args):
        """Filter projects and conversations based on search query"""
        query = self.search_var.get().lower()

        # Clear and reload projects/conversations based on search
        for widget in self.projects_container.winfo_children():
            widget.destroy()

        for widget in self.conversations_container.winfo_children():
            widget.destroy()

        # Reload with filter
        self.load_projects(search_query=query)
        self.list_conversations(search_query=query)

    def change_language(self, lang):
        """Change the application language"""
        if lang == "English":
            self.language = "en"
        elif lang == "Português":
            self.language = "pt"
        elif lang == "Español":
            self.language = "es"

        # Update UI text elements based on language
        self._update_ui_language()

    def _update_ui_language(self):
        """Update UI text based on selected language"""
        lang_texts = {
            "en": {
                "projects": "Projects",
                "conversations": "Conversations",
                "settings": "Settings",
                "search_placeholder": "Search projects and chats...",
                "ready_to_help": "Ready to help",
                "new_project": "Create new project?",
                "export_chat": "Export conversation?",
                "templates": "What are templates?",
                "attachments": "How to use attachments?",
            },
            "pt": {
                "projects": "Projetos",
                "conversations": "Conversas",
                "settings": "Configurações",
                "search_placeholder": "Buscar projetos e conversas...",
                "ready_to_help": "Pronto para ajudar",
                "new_project": "Como criar um novo projeto?",
                "export_chat": "Como exportar uma conversa?",
                "templates": "O que são templates?",
                "attachments": "Como usar anexos?",
            },
            "es": {
                "projects": "Proyectos",
                "conversations": "Conversaciones",
                "settings": "Configuración",
                "search_placeholder": "Buscar proyectos y conversaciones...",
                "ready_to_help": "Listo para ayudar",
                "new_project": "¿Cómo crear un nuevo proyecto?",
                "export_chat": "¿Cómo exportar una conversación?",
                "templates": "¿Qué son las plantillas?",
                "attachments": "¿Cómo usar archivos adjuntos?",
            },
        }

        texts = lang_texts.get(self.language, lang_texts["en"])

        # Update section titles
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and hasattr(widget, "title_label"):
                if (
                    widget.title_label.cget("text") == "Projetos"
                    or widget.title_label.cget("text") == "Projects"
                    or widget.title_label.cget("text") == "Proyectos"
                ):
                    widget.title_label.configure(text=texts["projects"])
                elif (
                    widget.title_label.cget("text") == "Conversas"
                    or widget.title_label.cget("text") == "Conversations"
                    or widget.title_label.cget("text") == "Conversaciones"
                ):
                    widget.title_label.configure(text=texts["conversations"])
                elif (
                    widget.title_label.cget("text") == "Configurações"
                    or widget.title_label.cget("text") == "Settings"
                    or widget.title_label.cget("text") == "Configuración"
                ):
                    widget.title_label.configure(text=texts["settings"])

        # Update other UI elements
        self.contact_status.configure(text=texts["ready_to_help"])

        # Update suggestion buttons if they exist
        self._update_suggestion_buttons(texts)

    def _update_suggestion_buttons(self, texts):
        """Update text in suggestion buttons"""
        if hasattr(self, "suggestion_buttons") and self.suggestion_buttons:
            for btn in self.suggestion_buttons:
                current_text = btn.cget("text")
                if (
                    "criar um novo projeto" in current_text
                    or "create new project" in current_text
                    or "crear un nuevo proyecto" in current_text
                ):
                    btn.configure(text=texts["new_project"])
                elif (
                    "exportar uma conversa" in current_text
                    or "export conversation" in current_text
                    or "exportar una conversación" in current_text
                ):
                    btn.configure(text=texts["export_chat"])
                elif (
                    "são templates" in current_text
                    or "are templates" in current_text
                    or "son las plantillas" in current_text
                ):
                    btn.configure(text=texts["templates"])
                elif (
                    "usar anexos" in current_text
                    or "use attachments" in current_text
                    or "usar archivos adjuntos" in current_text
                ):
                    btn.configure(text=texts["attachments"])

    def show_profile(self):
        """Show user profile settings"""
        # Placeholder for future implementation
        messagebox.showinfo(
            "Profile", "Profile settings will be available in a future update."
        )

    def show_shortcuts(self):
        """Show keyboard shortcuts help"""
        shortcuts = {
            "Ctrl+Enter": "Send message",
            "Ctrl+N": "New chat",
            "Ctrl+E": "Export chat",
            "Ctrl+L": "Clear chat",
            "Ctrl+T": "Toggle theme",
            "↑/↓": "Navigate message history",
            "Ctrl+F": "Focus search",
            "Esc": "Cancel current operation",
        }

        shortcuts_text = "Keyboard Shortcuts:\n\n"
        for key, action in shortcuts.items():
            shortcuts_text += f"{key}: {action}\n"

        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)

    def load_projects(self, search_query=None):
        """Load projects into the sidebar"""
        try:
            # Clear existing projects
            if self.projects_container and hasattr(
                self.projects_container, "winfo_children"
            ):
                for widget in self.projects_container.winfo_children():
                    widget.destroy()

            # Add the "New Project" button back first
            self._add_new_project_button()

            # If containers are not initialized yet, exit gracefully
            if not self.projects_container or not self.conversations_container:
                logger.warning("Containers not initialized yet, skipping load_projects")
                return

            # Load projects
            projects = self.project_manager.list_projects()

            if not projects:
                # Show empty state
                empty_label = ctk.CTkLabel(
                    self.projects_container,
                    text="Nenhum projeto encontrado",
                    text_color=self.colors["text_secondary"],
                    font=ctk.CTkFont(size=13),  # Larger font
                )
                empty_label.pack(pady=20)
            else:
                # Add project items
                for project in projects:
                    project_frame = ctk.CTkFrame(
                        self.projects_container,
                        fg_color=self.colors["surface_light"],
                        corner_radius=8,
                        height=70,  # Taller frames
                    )
                    project_frame.pack(fill="x", padx=8, pady=6)  # More spacing

                    # Project name
                    name_label = ctk.CTkLabel(
                        project_frame,
                        text=project["name"],
                        font=ctk.CTkFont(size=15, weight="bold"),  # Larger font
                        text_color=self.colors["text"],
                    )
                    name_label.pack(anchor="w", padx=14, pady=(10, 4))  # Better padding

                    # Project description (truncated)
                    desc = project["description"]
                    if len(desc) > 35:  # Allow slightly longer descriptions
                        desc = desc[:32] + "..."

                    desc_label = ctk.CTkLabel(
                        project_frame,
                        text=desc,
                        font=ctk.CTkFont(size=13),  # Larger font
                        text_color=self.colors["text_secondary"],
                    )
                    desc_label.pack(anchor="w", padx=14, pady=(0, 10))  # Better padding

                    # Add hover effect
                    def on_enter(e, frame=project_frame):
                        frame.configure(fg_color=self.colors["surface_hover"])

                    def on_leave(e, frame=project_frame):
                        frame.configure(fg_color=self.colors["surface_light"])

                    project_frame.bind("<Enter>", on_enter)
                    project_frame.bind("<Leave>", on_leave)

                    # Add click event - Open project conversations instead of panel
                    project_frame.bind(
                        "<Button-1>", lambda e, p=project: self.open_project(p)
                    )

                    # Add settings button for project editing
                    settings_btn = ctk.CTkButton(
                        project_frame,
                        text="⚙️",
                        width=30,
                        height=30,
                        corner_radius=8,
                        fg_color="transparent",
                        hover_color=self.colors["surface_hover"],
                        text_color=self.colors["text_secondary"],
                        command=lambda p=project: self.show_project_panel(p),
                    )
                    settings_btn.place(relx=0.95, rely=0.5, anchor="e")

            # Load conversations
            conversations = self.list_conversations()

            if not conversations:
                # Show empty state
                empty_label = ctk.CTkLabel(
                    self.conversations_container,
                    text="Nenhuma conversa encontrada",
                    text_color=self.colors["text_secondary"],
                    font=ctk.CTkFont(size=13),  # Larger font
                )
                empty_label.pack(pady=20)
            else:
                # Add conversation items
                for conversation in conversations:
                    # Skip project-related conversations in the main conversations list
                    if conversation.get("project_id"):
                        continue

                    conv_frame = ctk.CTkFrame(
                        self.conversations_container,
                        fg_color=self.colors["surface_light"],
                        corner_radius=8,
                        height=70,  # Taller frames
                    )
                    conv_frame.pack(fill="x", padx=8, pady=6)  # More spacing

                    # Conversation title
                    title_label = ctk.CTkLabel(
                        conv_frame,
                        text=conversation["title"],
                        font=ctk.CTkFont(size=15, weight="bold"),  # Larger font
                        text_color=self.colors["text"],
                    )
                    title_label.pack(
                        anchor="w", padx=14, pady=(10, 4)
                    )  # Better padding

                    # Preview (if available)
                    if "preview" in conversation and conversation["preview"]:
                        preview = conversation["preview"]
                        if len(preview) > 35:  # Allow slightly longer previews
                            preview = preview[:32] + "..."

                        preview_label = ctk.CTkLabel(
                            conv_frame,
                            text=preview,
                            font=ctk.CTkFont(size=13),  # Larger font
                            text_color=self.colors["text_secondary"],
                        )
                        preview_label.pack(
                            anchor="w", padx=14, pady=(0, 10)
                        )  # Better padding

                    # Add hover effect
                    def on_enter(e, frame=conv_frame):
                        frame.configure(fg_color=self.colors["surface_hover"])

                    def on_leave(e, frame=conv_frame):
                        frame.configure(fg_color=self.colors["surface_light"])

                    conv_frame.bind("<Enter>", on_enter)
                    conv_frame.bind("<Leave>", on_leave)

                    # Add click event to open conversation
                    conv_frame.bind(
                        "<Button-1>",
                        lambda e, c=conversation: self.start_chat_with(c),
                    )

        except Exception as e:
            logger.error(f"Error loading projects: {str(e)}")
            # Show error message in sidebar if it exists
            if self.projects_container and hasattr(
                self.projects_container, "winfo_children"
            ):
                error_label = ctk.CTkLabel(
                    self.projects_container,
                    text="Erro ao carregar projetos",
                    text_color=self.colors["error"],
                )
                error_label.pack(pady=20)

    def list_conversations(self, search_query=None):
        """List all conversations"""
        try:
            # Clear existing conversations first
            if self.conversations_container and hasattr(
                self.conversations_container, "winfo_children"
            ):
                for widget in self.conversations_container.winfo_children():
                    widget.destroy()

            # Add the "New Chat" button back first
            self._add_new_chat_button()

            # First check if the conversations table exists
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"
            )
            if not cursor.fetchone():
                # Create conversations table if it doesn't exist
                self.db.conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        unread BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create messages table if needed
                self.db.conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER,
                        conversation_id INTEGER,
                        sender TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                    )
                """)

                self.db.conn.commit()
                return []

            # Check if messages table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
            )
            if not cursor.fetchone():
                # Create messages table
                self.db.conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER,
                        conversation_id INTEGER,
                        sender TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                    )
                """)
                self.db.conn.commit()

                # Return just conversations without message count
                cursor.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
                return [dict(row) for row in cursor.fetchall()]

            # Check if conversation_id column exists in messages table
            cursor.execute("PRAGMA table_info(messages)")
            columns = [column[1] for column in cursor.fetchall()]
            if "conversation_id" not in columns:
                # Add the column if it doesn't exist
                cursor.execute(
                    "ALTER TABLE messages ADD COLUMN conversation_id INTEGER REFERENCES conversations(id)"
                )
                self.db.conn.commit()

                # Return just conversations without messages since there wouldn't be any linked
                cursor.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
                return [dict(row) for row in cursor.fetchall()]

            # Get conversations with message count
            cursor.execute("""
                SELECT c.*, COUNT(m.id) as message_count 
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
            """)

            conversations = []
            for row in cursor.fetchall():
                conversation = dict(row)

                # Get last message for preview
                preview_cursor = self.db.conn.cursor()
                preview_cursor.execute(
                    """
                    SELECT content FROM messages 
                    WHERE conversation_id = ? 
                    ORDER BY created_at DESC LIMIT 1
                """,
                    (conversation["id"],),
                )

                last_message = preview_cursor.fetchone()
                if last_message:
                    preview = last_message[0]
                    conversation["preview"] = preview[:100] + (
                        "..." if len(preview) > 100 else ""
                    )

                conversations.append(conversation)

            return conversations
        except Exception as e:
            logger.error(f"Error listing conversations: {str(e)}")
            return []

    def handle_suggestion(self, suggestion):
        """Handle a quick suggestion click"""
        try:
            if suggestion and isinstance(suggestion, str):
                # Clear placeholder if visible
                if self._placeholder_visible:
                    self.text_input.delete("1.0", "end")
                    self.text_input.configure(text_color=self.colors["text"])
                    self._placeholder_visible = False

                # Set the suggestion as input text
                self.text_input.delete("1.0", "end")
                self.text_input.insert("1.0", suggestion)

                # Update counter and button state
                text = self.text_input.get("1.0", "end-1c")
                count = len(text)
                self.char_counter.configure(text=f"{count}/4000")
                self.send_btn.configure(state="normal")

                # Give focus to the input field
                self.text_input.focus_set()
        except Exception as e:
            logger.error(f"Error handling suggestion: {str(e)}")

    def setup_messages_container(self):
        """Setup messages container"""
        try:
            # Messages container (scrollable)
            self.messages_container = MessagesContainer(
                self.chat_area,
                fg_color=self.colors["background"],
                corner_radius=12,
                colors=self.colors,
                copy_callback=self.copy_message,
            )
            self.messages_container.pack(
                fill="both", expand=True, padx=16, pady=(8, 16)
            )

        except Exception as e:
            logger.error(f"Error setting up messages container: {str(e)}")

    def open_project(self, project):
        """Open project and show its conversations"""
        try:
            # Set current project
            self.current_project = project

            # Update header to show project context
            self.contact_info.configure(text=f"Projeto: {project['name']}")
            self.contact_status.configure(text="Carregando conversas do projeto...")

            # Clear messages
            if hasattr(self.messages_container, "clear_messages"):
                self.messages_container.clear_messages()

            # Get project conversations
            conversations = self.list_project_conversations(project["id"])

            # Clear the main area to add project conversations
            self.messages_container.clear_widgets()

            # Create project header
            project_header = ctk.CTkFrame(
                self.messages_container,
                fg_color=self.colors["surface_light"],
                corner_radius=8,
            )

            project_name = ctk.CTkLabel(
                project_header,
                text=project["name"],
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=self.colors["primary"],
            )
            project_name.pack(anchor="w", padx=16, pady=(16, 4))

            project_desc = ctk.CTkLabel(
                project_header,
                text=project["description"],
                font=ctk.CTkFont(size=14),
                text_color=self.colors["text"],
                wraplength=800,
                justify="left",
            )
            project_desc.pack(anchor="w", padx=16, pady=(0, 16))

            # Action buttons
            action_frame = ctk.CTkFrame(
                project_header,
                fg_color="transparent",
            )
            action_frame.pack(fill="x", padx=16, pady=(0, 16))

            # Upload file button
            upload_btn = ctk.CTkButton(
                action_frame,
                text="Enviar Arquivo",
                width=140,
                height=36,
                corner_radius=8,
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_dark"],
                text_color=self.colors["text_light"],
                command=lambda: self.upload_file_to_project(project["id"]),
            )
            upload_btn.pack(side="left", padx=(0, 8))

            # New conversation button
            new_convo_btn = ctk.CTkButton(
                action_frame,
                text="Nova Conversa",
                width=140,
                height=36,
                corner_radius=8,
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_dark"],
                text_color=self.colors["text_light"],
                command=lambda: self.start_new_project_conversation(project),
            )
            new_convo_btn.pack(side="left", padx=4)

            # Add project header to container
            self.messages_container.add_widget(project_header)

            if conversations:
                # Create conversations container
                convos_container = ctk.CTkFrame(
                    self.messages_container,
                    fg_color="transparent",
                )

                # Add title for conversations
                convos_title = ctk.CTkLabel(
                    convos_container,
                    text="Conversas do Projeto",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors["text"],
                )
                convos_title.pack(anchor="w", padx=16, pady=(16, 8))

                # Create grid for conversations
                conversations_grid = ctk.CTkFrame(
                    convos_container,
                    fg_color="transparent",
                )
                conversations_grid.pack(fill="x", padx=16, pady=8)

                # Add conversations in a grid layout
                for i, conversation in enumerate(conversations):
                    conv_frame = ctk.CTkFrame(
                        conversations_grid,
                        fg_color=self.colors["surface_light"],
                        corner_radius=8,
                        border_width=1,
                        border_color=self.colors["border"],
                    )
                    conv_frame.pack(fill="x", pady=8)

                    title = conversation.get("title", "Conversa sem título")
                    date = conversation.get("updated_at", "")

                    # Format date if present
                    date_text = ""
                    if date:
                        try:
                            from datetime import datetime

                            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                            date_text = dt.strftime("%d/%m/%Y %H:%M")
                        except:
                            date_text = date

                    # Title with date
                    header_frame = ctk.CTkFrame(
                        conv_frame,
                        fg_color="transparent",
                    )
                    header_frame.pack(fill="x", padx=12, pady=(12, 0))

                    title_label = ctk.CTkLabel(
                        header_frame,
                        text=title,
                        font=ctk.CTkFont(size=15, weight="bold"),
                        text_color=self.colors["text"],
                    )
                    title_label.pack(side="left")

                    if date_text:
                        date_label = ctk.CTkLabel(
                            header_frame,
                            text=date_text,
                            font=ctk.CTkFont(size=12),
                            text_color=self.colors["text_secondary"],
                        )
                        date_label.pack(side="right")

                    # Preview
                    if "preview" in conversation and conversation["preview"]:
                        preview = conversation["preview"]
                        preview_label = ctk.CTkLabel(
                            conv_frame,
                            text=preview,
                            wraplength=700,
                            justify="left",
                            font=ctk.CTkFont(size=13),
                            text_color=self.colors["text_secondary"],
                        )
                        preview_label.pack(anchor="w", padx=12, pady=(4, 12), fill="x")

                    # Add hover effect
                    def on_enter(e, frame=conv_frame):
                        frame.configure(fg_color=self.colors["surface_hover"])

                    def on_leave(e, frame=conv_frame):
                        frame.configure(fg_color=self.colors["surface_light"])

                    conv_frame.bind("<Enter>", on_enter)
                    conv_frame.bind("<Leave>", on_leave)

                    # Add click event
                    conv_frame.bind(
                        "<Button-1>",
                        lambda e,
                        c=conversation,
                        p=project: self.start_project_conversation(p, c),
                    )

                # Add conversations container to main area
                self.messages_container.add_widget(convos_container)
            else:
                # Create empty state
                empty_container = ctk.CTkFrame(
                    self.messages_container,
                    fg_color="transparent",
                )

                empty_label = ctk.CTkLabel(
                    empty_container,
                    text="Nenhuma conversa encontrada neste projeto",
                    font=ctk.CTkFont(size=15),
                    text_color=self.colors["text_secondary"],
                )
                empty_label.pack(pady=32)

                start_btn = ctk.CTkButton(
                    empty_container,
                    text="Iniciar Nova Conversa",
                    width=200,
                    height=40,
                    corner_radius=8,
                    fg_color=self.colors["primary"],
                    hover_color=self.colors["primary_dark"],
                    text_color=self.colors["text_light"],
                    command=lambda: self.start_new_project_conversation(project),
                )
                start_btn.pack(pady=8)

                self.messages_container.add_widget(empty_container)

            # Show project files if any
            files = self.list_project_files(project["id"])
            if files:
                # Create files container
                files_container = ctk.CTkFrame(
                    self.messages_container,
                    fg_color="transparent",
                )

                # Add title for files
                files_title = ctk.CTkLabel(
                    files_container,
                    text="Arquivos do Projeto",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors["text"],
                )
                files_title.pack(anchor="w", padx=16, pady=(24, 8))

                # Create files grid
                files_grid = ctk.CTkFrame(
                    files_container,
                    fg_color="transparent",
                )
                files_grid.pack(fill="x", padx=16, pady=8)

                # Add files
                for file in files:
                    file_frame = ctk.CTkFrame(
                        files_grid,
                        fg_color=self.colors["surface_light"],
                        corner_radius=8,
                        border_width=1,
                        border_color=self.colors["border"],
                    )
                    file_frame.pack(fill="x", pady=4)

                    file_type_icon = "📄"  # Default icon
                    filename = file.get("filename", "")
                    file_size = file.get("size", "")

                    if filename.endswith((".pdf", ".PDF")):
                        file_type_icon = "📕"
                    elif filename.endswith((".docx", ".doc", ".txt")):
                        file_type_icon = "📝"
                    elif filename.endswith((".jpg", ".jpeg", ".png", ".gif")):
                        file_type_icon = "🖼️"
                    elif filename.endswith((".mp3", ".wav", ".ogg")):
                        file_type_icon = "🎵"
                    elif filename.endswith((".mp4", ".mov", ".avi")):
                        file_type_icon = "🎬"

                    # File info
                    file_row = ctk.CTkFrame(
                        file_frame,
                        fg_color="transparent",
                    )
                    file_row.pack(fill="x", padx=12, pady=12)

                    icon_label = ctk.CTkLabel(
                        file_row,
                        text=file_type_icon,
                        font=ctk.CTkFont(size=18),
                    )
                    icon_label.pack(side="left", padx=(0, 8))

                    name_label = ctk.CTkLabel(
                        file_row,
                        text=filename,
                        font=ctk.CTkFont(size=14),
                        text_color=self.colors["text"],
                    )
                    name_label.pack(side="left")

                    if file_size:
                        # Format size
                        size_text = file_size
                        try:
                            size = int(file_size)
                            if size < 1024:
                                size_text = f"{size} B"
                            elif size < 1024 * 1024:
                                size_text = f"{size // 1024} KB"
                            else:
                                size_text = f"{size // (1024 * 1024):.1f} MB"
                        except:
                            pass

                        size_label = ctk.CTkLabel(
                            file_row,
                            text=size_text,
                            font=ctk.CTkFont(size=12),
                            text_color=self.colors["text_secondary"],
                        )
                        size_label.pack(side="right")

                    # Add hover effect
                    def on_file_enter(e, frame=file_frame):
                        frame.configure(fg_color=self.colors["surface_hover"])

                    def on_file_leave(e, frame=file_frame):
                        frame.configure(fg_color=self.colors["surface_light"])

                    file_frame.bind("<Enter>", on_file_enter)
                    file_frame.bind("<Leave>", on_file_leave)

                    # Add click event to view file
                    file_frame.bind(
                        "<Button-1>", lambda e, f=file: self.view_project_file(f)
                    )

                # Add files container to main area
                self.messages_container.add_widget(files_container)

            # Update status
            self.contact_status.configure(
                text=f"Base de conhecimento com {len(files) if files else 0} arquivos"
            )

            # Disable text input initially
            self.text_input.configure(state="disabled")
            self.send_btn.configure(state="disabled")

        except Exception as e:
            logger.error(f"Error opening project: {str(e)}")
            messagebox.showerror("Erro", f"Não foi possível abrir o projeto: {str(e)}")

    def list_project_conversations(self, project_id):
        """List conversations for a specific project"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                SELECT c.*, COUNT(m.id) as message_count 
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                WHERE c.project_id = ?
                GROUP BY c.id
                ORDER BY c.updated_at DESC
            """,
                (project_id,),
            )

            conversations = []
            for row in cursor.fetchall():
                conversation = dict(row)

                # Get last message for preview
                preview_cursor = self.db.conn.cursor()
                preview_cursor.execute(
                    """
                    SELECT content FROM messages 
                    WHERE conversation_id = ? 
                    ORDER BY created_at DESC LIMIT 1
                """,
                    (conversation["id"],),
                )

                last_message = preview_cursor.fetchone()
                if last_message:
                    preview = last_message[0]
                    conversation["preview"] = preview[:100] + (
                        "..." if len(preview) > 100 else ""
                    )

                conversations.append(conversation)

            return conversations

        except Exception as e:
            logger.error(f"Error listing project conversations: {str(e)}")
            return []

    def list_project_files(self, project_id):
        """List files for a specific project"""
        try:
            cursor = self.db.conn.cursor()

            # Check if project_files table exists
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
                self.db.conn.commit()
                return []

            # Get files
            cursor.execute(
                """
                SELECT * FROM project_files
                WHERE project_id = ?
                ORDER BY created_at DESC
            """,
                (project_id,),
            )

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error listing project files: {str(e)}")
            return []

    def upload_file_to_project(self, project_id):
        """Upload a file to a project"""
        try:
            # Show file dialog
            file_path = filedialog.askopenfilename(
                title="Selecione um arquivo para o projeto",
                filetypes=[
                    ("Todos os arquivos", "*.*"),
                    ("Arquivos de texto", "*.txt"),
                    ("Arquivos PDF", "*.pdf"),
                    ("Documentos", "*.docx;*.doc"),
                    ("Imagens", "*.jpg;*.jpeg;*.png"),
                ],
            )

            if not file_path:
                return

            # Get file info
            import os

            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            # Copy file to application directory
            import shutil

            app_dir = os.path.join(os.path.expanduser("~"), ".ucan", "files")
            os.makedirs(app_dir, exist_ok=True)

            # Create unique filename
            import uuid

            unique_id = str(uuid.uuid4())
            new_filename = f"{unique_id}_{filename}"
            new_filepath = os.path.join(app_dir, new_filename)

            # Copy file
            shutil.copy2(file_path, new_filepath)

            # Save to database
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO project_files (project_id, filename, filepath, size)
                VALUES (?, ?, ?, ?)
            """,
                (project_id, filename, new_filepath, file_size),
            )

            self.db.conn.commit()

            # Refresh project view
            if self.current_project and self.current_project.get("id") == project_id:
                self.open_project(self.current_project)

            # Show success message
            messagebox.showinfo(
                "Sucesso", f"Arquivo '{filename}' adicionado ao projeto."
            )

        except Exception as e:
            logger.error(f"Error uploading file to project: {str(e)}")
            messagebox.showerror(
                "Erro", f"Não foi possível fazer upload do arquivo: {str(e)}"
            )

    def view_project_file(self, file):
        """View a project file"""
        try:
            import os
            import platform
            import subprocess

            filepath = file.get("filepath", "")

            if not os.path.exists(filepath):
                messagebox.showerror("Erro", "Arquivo não encontrado.")
                return

            # Open file with default application
            if platform.system() == "Windows":
                os.startfile(filepath)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", filepath])
            else:  # Linux
                subprocess.run(["xdg-open", filepath])

        except Exception as e:
            logger.error(f"Error viewing file: {str(e)}")
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {str(e)}")

    def start_new_project_conversation(self, project):
        """Start a new conversation in a project"""
        try:
            # Create new conversation
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversations (title, project_id, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
                (f"Conversa {project['name']}", project["id"]),
            )

            self.db.conn.commit()
            conversation_id = cursor.lastrowid

            # Get the conversation
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            )
            conversation = dict(cursor.fetchone())

            # Start the conversation
            self.start_project_conversation(project, conversation)

        except Exception as e:
            logger.error(f"Error starting new project conversation: {str(e)}")
            messagebox.showerror(
                "Erro", f"Não foi possível iniciar nova conversa: {str(e)}"
            )

    def start_project_conversation(self, project, conversation):
        """Start a conversation in a project context"""
        try:
            # Update current project and conversation
            self.current_project = project
            self.current_conversation = conversation

            # Update header
            self.contact_info.configure(
                text=f"Projeto: {project['name']} - {conversation.get('title', 'Conversa')}"
            )
            self.contact_status.configure(text="Carregando conversa...")

            # Clear messages
            if hasattr(self.messages_container, "clear_messages"):
                self.messages_container.clear_messages()

            # Load messages for this conversation
            messages = self.load_conversation_messages(conversation["id"])

            if not messages:
                # Add system message about context
                self.add_message(
                    f"👋 Iniciando conversa no contexto do projeto '{project['name']}'.\n\n"
                    f"Este projeto contém {len(self.list_project_files(project['id']))} arquivos na base de conhecimento.",
                    "Sistema",
                )
            else:
                # Add all messages
                for message in messages:
                    self.add_message(message["content"], message["sender"])

            # Enable text input
            self.text_input.configure(state="normal")
            if self._placeholder_visible:
                self.text_input.delete("1.0", "end")
                self.text_input.insert("1.0", "Digite sua mensagem...")
                self.text_input.configure(text_color=self.colors["text_secondary"])

            # Update status
            self.contact_status.configure(text="Conversa ativa")

            # Focus on input
            self.text_input.focus_set()

        except Exception as e:
            logger.error(f"Error starting project conversation: {str(e)}")
            messagebox.showerror(
                "Erro", f"Não foi possível iniciar a conversa: {str(e)}"
            )

    def load_conversation_messages(self, conversation_id):
        """Load messages for a conversation"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
            """,
                (conversation_id,),
            )

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error loading conversation messages: {str(e)}")
            return []

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        # General application shortcuts
        self.bind("<Control-n>", lambda e: self.new_chat())
        self.bind("<Control-e>", lambda e: self.export_chat())
        self.bind("<Control-l>", lambda e: self.clear_chat())
        self.bind("<Control-t>", lambda e: self.toggle_theme())

        # Search focus
        self.bind("<Control-f>", lambda e: self._focus_search())

        # Escape to cancel current operation
        self.bind("<Escape>", lambda e: self._handle_escape())

        # Only bind message input shortcuts if the text_input exists
        if hasattr(self, "text_input") and self.text_input is not None:
            # Message history navigation with arrow keys (when input has focus)
            self.text_input.bind("<Up>", self._previous_message)
            self.text_input.bind("<Down>", self._next_message)

            # Submit message with Ctrl+Enter
            self.text_input.bind("<Control-Return>", lambda e: self.send_message())

            # Tab key behavior
            self.text_input.bind("<Tab>", self._handle_tab)
        else:
            logger.warning(
                "Text input not yet initialized, skipping input-specific shortcuts"
            )

        # Project shortcuts
        self.bind("<Control-p>", lambda e: self.show_project_panel())

        # Templates shortcuts
        self.bind("<Control-r>", lambda e: self.show_template_dialog())

        # Toggle high contrast
        self.bind("<Control-h>", lambda e: self._toggle_high_contrast())

        logger.info("Keyboard shortcuts initialized")

    def _focus_search(self, event=None):
        """Focus the search input"""
        if hasattr(self, "search_var"):
            # Find the search entry widget and focus it
            for widget in self.sidebar.winfo_children():
                if isinstance(widget, ctk.CTkScrollableFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkFrame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ctk.CTkEntry):
                                    grandchild.focus_set()
                                    return

    def _handle_escape(self, event=None):
        """Handle escape key press"""
        # If editing a message, cancel the edit
        if hasattr(self, "current_edit_frame") and self.current_edit_frame:
            self._cancel_edit()
            return

        # If a dialog is open, close it
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel) and widget.winfo_viewable():
                widget.destroy()
                return

        # Unfocus the current widget
        self.focus_set()

    def _toggle_high_contrast(self, event=None):
        """Toggle high contrast mode"""
        colors = self.theme_manager.toggle_contrast()
        self.colors = colors
        self._apply_theme_colors()

        # Show a notification
        contrast_mode = (
            "High Contrast" if self.theme_manager.high_contrast else "Normal Contrast"
        )
        self.show_notification(f"{contrast_mode} mode activated", "info")

    def _apply_theme_colors(self):
        """Apply theme colors to all widgets"""
        # This method will be called when theme changes
        # We should update colors of all widgets in the UI

        # Update main container
        self.main_container.configure(fg_color=self.colors["background"])

        # Update sidebar
        self.sidebar.configure(fg_color=self.colors["surface"])

        # Update chat area
        self.chat_area.configure(fg_color=self.colors["surface"])
        self.chat_header.configure(fg_color=self.colors["surface_light"])

        # Update chat contact info
        self.contact_info.configure(text_color=self.colors["text"])
        self.contact_status.configure(text_color=self.colors["text_secondary"])

        # Update message area background color
        if hasattr(self, "messages_container"):
            self.messages_container.configure(fg_color=self.colors["surface"])

        # Update input area
        if hasattr(self, "input_frame"):
            self.input_frame.configure(fg_color=self.colors["surface_light"])

        if hasattr(self, "text_input"):
            self.text_input.configure(
                fg_color=self.colors["surface"],
                border_color=self.colors["border"],
                text_color=self.colors["text"],
            )

        # Update buttons
        if hasattr(self, "send_button"):
            self.send_button.configure(
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_dark"],
                text_color=self.colors["text_light"],
            )

        # Update suggestions area
        if hasattr(self, "suggestions_frame"):
            self.suggestions_frame.configure(fg_color=self.colors["surface_light"])

        # Update other UI elements as needed
        self.refresh_ui()

    def refresh_ui(self):
        """Refresh UI components after theme change"""
        # This method will be called to refresh the UI after theme changes
        # Only reload if the containers are initialized
        if self.projects_container and self.conversations_container:
            # Reload projects and conversations with updated colors
            self.load_projects()
            self.list_conversations()

        # Force UI to update
        self.update_idletasks()

    def set_workspace(self, workspace_path):
        """Set the workspace directory"""
        # This would be implemented to set a workspace directory
        # for project files and configurations
        logger.info(f"Setting workspace to {workspace_path}")
        # Here you would update any necessary paths or configurations
        # based on the workspace
        self.show_notification(f"Workspace set to {workspace_path}", "info")

    def translate_text(self):
        """Translate the input text to another language"""
        # Get current text
        if hasattr(self, "is_placeholder") and self.is_placeholder:
            messagebox.showinfo("Tradução", "Digite um texto para traduzir primeiro.")
            return

        text = self.text_input.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("Tradução", "Digite um texto para traduzir primeiro.")
            return

        # Create language selection dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Traduzir Texto")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Create dialog content
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Dialog title
        title_label = ctk.CTkLabel(
            content_frame,
            text="Traduzir para qual idioma?",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"],
        )
        title_label.pack(pady=(0, 20))

        # Language selection
        languages = [
            "English (Inglês)",
            "Español (Espanhol)",
            "Français (Francês)",
            "Deutsch (Alemão)",
            "Italiano (Italiano)",
            "日本語 (Japonês)",
            "한국어 (Coreano)",
            "中文 (Chinês)",
        ]

        language_var = ctk.StringVar(value=languages[0])

        for lang in languages:
            lang_btn = ctk.CTkRadioButton(
                content_frame,
                text=lang,
                variable=language_var,
                value=lang,
                text_color=self.colors["text"],
                fg_color=self.colors["primary"],
            )
            lang_btn.pack(anchor="w", pady=5)

        # Button frame
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color=self.colors["surface_light"],
            text_color=self.colors["text"],
            hover_color=self.colors["surface_hover"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
            command=dialog.destroy,
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        # Translate button
        def do_translate():
            selected_lang = language_var.get().split(" ")[0]
            # Here we would call LLM to translate
            # For now, let's just simulate translation
            translated_text = f"[Texto traduzido para {selected_lang}]: {text}"

            # Close dialog
            dialog.destroy()

            # Add message with original text
            self.add_message(text, "Você")

            # Clear input
            self.text_input.delete("1.0", "end")
            self._update_char_count()

            # Start "thinking" animation
            self.thinking.start()

            # Simulate translation delay
            self.after(1500, lambda: self._finish_translation(translated_text))

        translate_btn = ctk.CTkButton(
            button_frame,
            text="Traduzir",
            fg_color=self.colors["primary"],
            text_color=self.colors["text_light"],
            hover_color=self.colors["primary_dark"],
            corner_radius=8,
            command=do_translate,
        )
        translate_btn.pack(side="right")

    def _finish_translation(self, translated_text):
        """Complete the translation process and show result"""
        # Stop thinking animation
        self.thinking.stop()

        # Add translated message
        self.add_message(translated_text, "UCAN Assistant")

    def _update_char_count(self, event=None):
        """Update character count in the input field"""
        if hasattr(self, "is_placeholder") and self.is_placeholder:
            count = 0
        else:
            count = len(self.text_input.get("1.0", "end-1c"))

        max_chars = 4000

        # Update counter
        if hasattr(self, "char_count"):
            self.char_count.configure(text=f"{count}/{max_chars}")

            # Change color if approaching limit
            if count > max_chars:
                self.char_count.configure(text_color=self.colors["error"])
            elif count > max_chars * 0.8:
                self.char_count.configure(text_color=self.colors["warning"])
            else:
                self.char_count.configure(text_color=self.colors["text_secondary"])

        # Show warning if over limit
        if count > max_chars:
            self.char_count.configure(text_color=self.colors["error"])

    def _add_placeholder(self, event=None):
        """Add placeholder text to the input field if empty"""
        if self.text_input.get("1.0", "end-1c").strip() == "":
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", "Digite sua mensagem aqui...")
            self.text_input.configure(text_color=self.colors["text_secondary"])
            self.is_placeholder = True
            self._update_char_count()

    def _clear_placeholder(self, event=None):
        """Clear placeholder text when input is focused"""
        if hasattr(self, "is_placeholder") and self.is_placeholder:
            self.text_input.delete("1.0", "end")
            self.text_input.configure(text_color=self.colors["text"])
            self.is_placeholder = False
            self._update_char_count()

    def _handle_tab(self, event):
        """Handle tab key in text input - insert spaces instead of changing focus"""
        # Insert 4 spaces instead of changing focus
        self.text_input.insert("insert", "    ")

        # Prevent default behavior (focus change)
        return "break"

    def _process_message(self, message):
        """Process message with AI and show response"""
        try:
            # Simulate AI processing
            response = "I received your message: " + message

            # You would typically call an LLM here:
            # if hasattr(self, "ai_provider") and hasattr(self.ai_provider, "get_response"):
            #     response = self.ai_provider.get_response(message)

            # Stop thinking animation
            self.thinking.stop()

            # Add AI response to UI
            self.add_message(response, "Assistente")

            # Save assistant's response to database if we have a current conversation
            if hasattr(self, "current_conversation") and self.current_conversation:
                conversation_id = self.current_conversation["id"]
                self.project_manager.add_message(
                    conversation_id, response, "Assistente"
                )

                # Update conversation modified time
                self.db.update_conversation(
                    conversation_id, {"updated_at": datetime.now()}
                )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.thinking.stop()
            messagebox.showerror(
                "Error", "Erro ao processar mensagem. Tente novamente."
            )

    def center_button_in_container(self, container, button):
        """Properly center a button in a flex container"""
        # Configure the container for proper centering
        container.configure(
            fg_color="transparent", width=50, height=50, corner_radius=0
        )

        # Configure the button for proper centering
        button.configure(
            width=40,
            height=40,
            corner_radius=20,  # Use half of width/height for circular button
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_dark"],
            text_color=self.colors["text_light"],
        )

        # Use place to precisely position the button in the center
        button.place(relx=0.5, rely=0.5, anchor="center")

    def _show_maximized(self):
        """Show the window maximized after everything is loaded"""
        try:
            # Center the window first
            self.center_window()

            # Maximize window in a platform-independent way
            self.update_idletasks()  # Make sure window dimensions are updated

            # Get screen dimensions
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            # Try to maximize using the appropriate method based on platform
            if sys.platform == "win32":
                self.state("zoomed")  # Windows
            elif sys.platform == "darwin":
                # MacOS doesn't have a true maximize, so we'll make it large
                self.geometry(f"{screen_width}x{screen_height}")
            else:
                # Linux and other platforms
                self.attributes("-zoomed", True)

            # Finally show the window
            self.deiconify()

            # Force focus
            self.focus_force()

            logger.info("Window shown maximized")
        except Exception as e:
            # If maximizing fails, at least show the window
            logger.error(f"Error maximizing window: {str(e)}")
            self.deiconify()
