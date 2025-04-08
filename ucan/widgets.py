import datetime
import logging
import re
import threading
import time
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Optional

import customtkinter as ctk
import markdown2  # Add this import

from .theme import ThemeManager

logger = logging.getLogger("UCAN")


class MarkdownLabel(ctk.CTkLabel):
    """Label that supports markdown formatting"""

    def __init__(self, *args, **kwargs):
        self.markdown_text = kwargs.pop("markdown_text", "")
        super().__init__(*args, **kwargs)
        self.apply_markdown()

    def apply_markdown(self):
        """Applies markdown formatting"""
        try:
            # Convert markdown to HTML
            html = markdown2.markdown(
                self.markdown_text,
                extras=["fenced-code-blocks", "tables", "break-on-newline"],
            )

            # Basic HTML to Tkinter text formatting
            formatted = html
            # Bold
            formatted = re.sub(r"<strong>(.*?)</strong>", r"**\1**", formatted)
            # Italic
            formatted = re.sub(r"<em>(.*?)</em>", r"*\1*", formatted)
            # Code
            formatted = re.sub(r"<code>(.*?)</code>", r"`\1`", formatted)
            # Remove other HTML tags
            formatted = re.sub(r"<[^>]+>", "", formatted)

            self.configure(text=formatted)
        except Exception as e:
            logger.error(f"Error applying markdown: {str(e)}")
            self.configure(text=self.markdown_text)


class ScrollableMessageFrame(ctk.CTkScrollableFrame):
    """Frame for displaying messages with scrolling"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.messages = []
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

        # Add start of conversation indicator with better visibility
        self.start_indicator = ctk.CTkFrame(
            self,
            fg_color=self.colors["surface_light"],
            corner_radius=8,
            height=40,
        )
        self.start_indicator.pack(fill="x", pady=20)

        start_line = ctk.CTkFrame(
            self.start_indicator,
            fg_color=self.colors["border"],
            height=2,  # Thicker line
        )
        start_line.pack(side="left", fill="x", expand=True, padx=10)

        start_label = ctk.CTkLabel(
            self.start_indicator,
            text="Início da Conversa",
            font=ctk.CTkFont(size=13, weight="bold"),  # Bolder text
            text_color=self.colors["text"],  # Better contrast
        )
        start_label.pack(side="left", padx=10)

        end_line = ctk.CTkFrame(
            self.start_indicator,
            fg_color=self.colors["border"],
            height=2,  # Thicker line
        )
        end_line.pack(side="left", fill="x", expand=True, padx=10)

        # Add quick suggestions frame
        self.suggestions_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=100,
        )
        self.suggestions_frame.pack(fill="x", pady=10)

        # Add suggestions label
        suggestions_label = ctk.CTkLabel(
            self.suggestions_frame,
            text="Perguntas rápidas:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_secondary"],
        )
        suggestions_label.pack(anchor="w", padx=16)

        # Suggestions container
        self.suggestions_container = ctk.CTkFrame(
            self.suggestions_frame,
            fg_color="transparent",
        )
        self.suggestions_container.pack(fill="x", padx=8, pady=8)

    def add_suggestions(self, suggestions, on_select=None):
        """Add quick suggestion buttons"""
        try:
            # Clear existing suggestions
            for widget in self.suggestions_container.winfo_children():
                widget.destroy()

            # Create flex layout frame
            flex_container = ctk.CTkFrame(
                self.suggestions_container,
                fg_color="transparent",
            )
            flex_container.pack(fill="x", padx=4, pady=4)

            # Track current row and column
            row = 0
            col = 0
            max_cols = 2  # Show 2 buttons per row for better layout

            # Create suggestion buttons in a grid layout
            for suggestion in suggestions:
                suggestion_btn = ctk.CTkButton(
                    flex_container,
                    text=suggestion,
                    font=ctk.CTkFont(size=13),
                    fg_color=self.colors["surface_light"],
                    text_color=self.colors["text"],
                    hover_color=self.colors["surface_hover"],
                    height=36,
                    width=220,  # Fixed width for alignment
                    corner_radius=12,
                    anchor="center",
                    command=lambda s=suggestion: self._handle_suggestion_click(
                        s, on_select
                    ),
                )
                suggestion_btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")

                # Add hover effect
                def on_enter(e, b=suggestion_btn):
                    b.configure(fg_color=self.colors["surface_hover"])

                def on_leave(e, b=suggestion_btn):
                    b.configure(fg_color=self.colors["surface_light"])

                suggestion_btn.bind("<Enter>", on_enter)
                suggestion_btn.bind("<Leave>", on_leave)

                # Update grid position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        except Exception as e:
            logging.error(f"Error adding suggestions: {str(e)}")

    def _handle_suggestion_click(self, suggestion, callback=None):
        """Handle suggestion button click"""
        try:
            if callback and callable(callback):
                callback(suggestion)
        except Exception as e:
            logging.error(f"Error handling suggestion click: {str(e)}")

    def add_message(self, message: str, is_user: bool = False):
        """Add a message to the frame with animation effect"""
        try:
            # Create message container with spacing
            message_container = ctk.CTkFrame(
                self,
                fg_color="transparent",
                height=0,  # Start with height 0 for animation
            )
            message_container.pack(fill="x", pady=12, padx=16)  # Increased spacing

            # Message row with avatar and bubble
            message_row = ctk.CTkFrame(
                message_container,
                fg_color="transparent",
            )
            message_row.pack(fill="x")

            # Avatar frame - circular avatar
            avatar_size = 42  # Slightly larger avatar
            avatar_frame = ctk.CTkFrame(
                message_row,
                width=avatar_size,
                height=avatar_size,
                corner_radius=avatar_size // 2,  # Make it circular
                fg_color=self.colors["primary"]
                if is_user
                else self.colors["surface_light"],
            )
            avatar_frame.pack(
                side="right" if is_user else "left", padx=10
            )  # Increased padding
            avatar_frame.pack_propagate(False)

            # Avatar icon or text
            avatar_text = ctk.CTkLabel(
                avatar_frame,
                text="👤" if is_user else "🤖",
                font=ctk.CTkFont(size=16),
                text_color=self.colors["text_light"]
                if is_user
                else self.colors["text"],
            )
            avatar_text.pack(expand=True)

            # Create message bubble with modern styling
            bubble_container = ctk.CTkFrame(
                message_row,
                fg_color="transparent",
                width=450,  # More space for readability
            )
            bubble_container.pack(
                side="right" if is_user else "left", fill="x", expand=True
            )

            # Time and sender info
            info_frame = ctk.CTkFrame(
                bubble_container,
                fg_color="transparent",
                height=24,  # Slightly taller
            )
            info_frame.pack(fill="x", pady=(0, 4))

            # Add sender name
            sender_text = "Você" if is_user else "Assistente"
            sender_label = ctk.CTkLabel(
                info_frame,
                text=sender_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["text"],
                anchor="w" if not is_user else "e",
            )
            sender_label.pack(
                side="left" if not is_user else "right", padx=8
            )  # More padding

            # Add timestamp
            current_time = datetime.datetime.now().strftime("%H:%M")
            time_label = ctk.CTkLabel(
                info_frame,
                text=current_time,
                font=ctk.CTkFont(size=10),
                text_color=self.colors["text_secondary"],
                anchor="w" if not is_user else "e",
            )
            time_label.pack(
                side="left" if not is_user else "right", padx=8
            )  # More padding

            # Create bubble with shadow effect
            bubble = ctk.CTkFrame(
                bubble_container,
                fg_color=self.colors["primary"]
                if is_user
                else self.colors["surface_light"],
                corner_radius=16,
                border_width=0,
            )

            # Position the bubble first
            bubble.pack(
                side="right" if is_user else "left",
                fill="x",
                expand=True,
                padx=(50 if is_user else 0, 0 if is_user else 50),  # Better positioning
            )

            # For non-user messages, add a subtle border instead of shadow
            if not is_user:
                bubble.configure(
                    border_width=1,
                    border_color=self.colors["border"],
                )

            # Add text with proper padding and markdown support
            text_label = ctk.CTkLabel(
                bubble,
                text=message,
                wraplength=450,  # Wider text for better readability
                justify="left",
                font=ctk.CTkFont(size=14),
                text_color=self.colors["text_light"]
                if is_user
                else self.colors["text"],
                anchor="w",
            )
            text_label.pack(padx=20, pady=16, fill="both", expand=True)  # More padding

            # Add message to list
            self.messages.append((message_container, text_label, bubble, is_user))

            # Add action buttons container
            actions_frame = ctk.CTkFrame(
                bubble_container,
                fg_color="transparent",
                height=24,
            )
            actions_frame.pack(fill="x", pady=(4, 0))

            # Action buttons with modern styling
            actions = [
                ("📋", lambda: self.copy_message(message), "Copiar"),
                ("✏️", lambda: self.edit_message(message_container), "Editar"),
                ("🗑️", lambda: self.delete_message(message_container), "Excluir"),
            ]

            action_container = ctk.CTkFrame(
                actions_frame,
                fg_color="transparent",
            )
            action_container.pack(side="right" if is_user else "left")

            # Add hover-reveal action buttons
            for icon, cmd, tooltip in actions:
                btn = ctk.CTkButton(
                    action_container,
                    text=icon,
                    width=28,
                    height=28,
                    corner_radius=14,
                    fg_color="transparent",
                    hover_color=self.colors["surface"],
                    text_color=self.colors["text_secondary"],
                    font=ctk.CTkFont(size=12),
                    command=cmd,
                )
                btn.pack(side="left", padx=2)

                # Add tooltip
                tooltip_label = ctk.CTkLabel(
                    self.master.master,  # Position relative to main window
                    text=tooltip,
                    fg_color=self.colors["surface"],
                    corner_radius=6,
                    text_color=self.colors["text"],
                    font=ctk.CTkFont(size=11),
                    padx=8,
                    pady=4,
                )

                # Show/hide tooltip on hover
                def on_enter(e, b=btn, t=tooltip_label):
                    # Calculate position
                    x = b.winfo_rootx() + b.winfo_width() // 2 - t.winfo_width() // 2
                    y = b.winfo_rooty() - t.winfo_height() - 8
                    t.place(x=x, y=y)

                def on_leave(e, t=tooltip_label):
                    t.place_forget()

                btn.bind("<Enter>", on_enter)
                btn.bind("<Leave>", on_leave)

            # Initially hide action buttons
            action_container.pack_forget()

            # Show/hide action buttons on hover
            def show_actions(e):
                action_container.pack(side="right" if is_user else "left")

            def hide_actions(e):
                action_container.pack_forget()

            bubble.bind("<Enter>", show_actions)
            bubble.bind("<Leave>", hide_actions)

            # Animate message appearance
            def animate_message():
                # Get required height
                message_container.update_idletasks()
                required_height = message_container.winfo_reqheight()

                # Start hidden
                message_container.configure(height=0)
                message_container.pack_propagate(False)

                # Animation steps
                steps = 10
                for i in range(1, steps + 1):
                    height = int(required_height * (i / steps))
                    message_container.configure(height=height)
                    self.update_idletasks()
                    time.sleep(0.01)  # Short delay

                # Final state
                message_container.configure(height=required_height)
                message_container.pack_propagate(True)

                # Scroll to show new message
                self._scroll_to_bottom()

            # Run animation in a separate thread to avoid freezing UI
            animation_thread = threading.Thread(target=animate_message)
            animation_thread.daemon = True
            animation_thread.start()

            # Scroll to bottom
            self._scroll_to_bottom()

        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")

    def clear_messages(self):
        """Clear all messages"""
        try:
            # Remove message frames but keep start indicator and suggestions
            for message in self.messages:
                if isinstance(message, list) and message:
                    message[0].destroy()
                elif hasattr(message, "destroy"):
                    message.destroy()
            self.messages = []
        except Exception as e:
            logging.error(f"Error clearing messages: {str(e)}")

    def copy_message(self, message):
        """Copy message text to clipboard"""
        try:
            self.clipboard_clear()
            self.clipboard_append(message)

            # Show a toast notification
            toast = ctk.CTkFrame(
                self,
                fg_color=self.colors["primary"],
                corner_radius=8,
                width=200,
                height=40,
            )
            toast.place(relx=0.5, rely=0.9, anchor="center")

            toast_label = ctk.CTkLabel(
                toast,
                text="Mensagem copiada!",
                font=ctk.CTkFont(size=13),
                text_color=self.colors["text_light"],
            )
            toast_label.pack(expand=True)

            # Animate the toast
            def fade_out():
                for i in range(10, 0, -1):
                    toast.configure(
                        fg_color=(
                            self.colors["primary"][0],
                            self.colors["primary"][1],
                            i / 10,
                        )
                    )
                    self.update_idletasks()
                    time.sleep(0.05)
                toast.destroy()

            # Hide toast after 2 seconds
            self.after(2000, fade_out)

        except Exception as e:
            logger.error(f"Error copying message: {str(e)}")

    def edit_message(self, message_container):
        """Edit a message"""
        # Will be implemented in the UI class
        pass

    def delete_message(self, message_container):
        """Delete a message"""
        try:
            # Find the message in the list
            for i, message in enumerate(self.messages):
                if message[0] == message_container:
                    # Remove from list
                    self.messages.pop(i)

                    # Animate removal
                    def animate_removal():
                        # Get current height
                        message_container.update_idletasks()
                        current_height = message_container.winfo_height()

                        # Animation steps
                        steps = 10
                        for i in range(steps, 0, -1):
                            height = int(current_height * (i / steps))
                            message_container.configure(height=height)
                            self.update_idletasks()
                            time.sleep(0.01)  # Short delay

                        # Final state
                        message_container.destroy()

                    # Run animation in a separate thread
                    animation_thread = threading.Thread(target=animate_removal)
                    animation_thread.daemon = True
                    animation_thread.start()

                    break
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the message frame"""
        try:
            # Get scrollable region to scroll to bottom
            self.update_idletasks()
            self._parent_canvas.yview_moveto(1.0)
        except Exception as e:
            logger.error(f"Error scrolling: {str(e)}")

    def _get_message_text(self, message_idx: int) -> str:
        """Get the text of a message by index"""
        try:
            if 0 <= message_idx < len(self.messages):
                return self.messages[message_idx][1].cget("text")
            return ""
        except Exception as e:
            logger.error(f"Error getting message text: {str(e)}")
            return ""

    def refresh_theme(self):
        """Update colors when theme changes"""
        try:
            # Update theme manager
            self.theme_manager = ThemeManager()
            self.colors = self.theme_manager.get_colors()

            # Update start indicator
            self.start_indicator.configure(fg_color=self.colors["surface_light"])

            # Update start line and end line
            for child in self.start_indicator.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    child.configure(fg_color=self.colors["border"])
                elif isinstance(child, ctk.CTkLabel):
                    child.configure(text_color=self.colors["text"])

            # Update suggestions frame
            for child in self.suggestions_frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text_color=self.colors["text_secondary"])

            # Update suggestion buttons in grid
            for child in self.suggestions_frame.winfo_children():
                if isinstance(child, ctk.CTkFrame):  # This is the grid container
                    for button in child.winfo_children():
                        if isinstance(button, ctk.CTkButton):
                            button.configure(
                                fg_color=self.colors["surface_light"],
                                hover_color=self.colors["surface_hover"],
                                text_color=self.colors["text"],
                            )

            # Update message bubbles
            for msg_container, text_label, bubble, is_user in self.messages:
                bubble.configure(
                    fg_color=self.colors["primary"]
                    if is_user
                    else self.colors["surface_light"]
                )
                text_label.configure(
                    text_color=self.colors["text_light"]
                    if is_user
                    else self.colors["text"]
                )

        except Exception as e:
            logger.error(f"Error refreshing theme: {str(e)}")


class LoadingScreen(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("UCAN")
        self.geometry("300x200")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Loading text
        self.loading_label = ctk.CTkLabel(
            self,
            text="Carregando UCAN...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"],
        )
        self.loading_label.pack(pady=(40, 20))

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            self,
            fg_color=self.colors["surface"],
            progress_color=self.colors["primary"],
        )
        self.progress.pack(pady=20, padx=40, fill="x")
        self.progress.set(0)

        # Status text
        self.status_label = ctk.CTkLabel(
            self,
            text="Inicializando...",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"],
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


class ThinkingIndicator(ctk.CTkFrame):
    """Animated thinking indicator"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

        # Create dots
        self.dots = []
        for i in range(3):
            dot = ctk.CTkLabel(
                self,
                text="•",
                font=ctk.CTkFont(size=16),
                text_color=self.colors["text_secondary"],
                width=10,
            )
            dot.grid(row=0, column=i, padx=1)
            self.dots.append(dot)

        self.is_animating = False

    def start(self):
        """Start animation"""
        self.is_animating = True
        self._animate()

    def stop(self):
        """Stop animation"""
        self.is_animating = False

    def _animate(self):
        """Animate dots"""
        if not self.is_animating:
            return

        # Reset all dots
        for dot in self.dots:
            dot.configure(text_color=self.colors["text_secondary"])

        # Get current time
        now = datetime.datetime.now()
        dot_index = (now.microsecond // 333333) % 3

        # Highlight current dot
        self.dots[dot_index].configure(text_color=self.colors["primary"])

        # Schedule next animation frame
        self.after(100, self._animate)


class ProjectPanel(ctk.CTkToplevel):
    """Panel for creating/editing projects"""

    def __init__(
        self,
        parent,
        project: Optional[Dict] = None,
        on_save: Optional[Callable[[Dict], None]] = None,
    ):
        super().__init__(parent)
        self.title("Projeto")
        self.geometry("400x500")
        self.resizable(False, False)
        self.transient(parent)

        # Delay grab_set to ensure window is ready
        self.after(100, self._setup_grab)

        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

        # Store project data
        self.project = project
        self.project_id = project["id"] if project else None
        self.on_save = on_save

        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = (parent.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Project name
        name_label = ctk.CTkLabel(
            self,
            text="Nome do projeto:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        name_label.pack(anchor="w", padx=20, pady=(20, 5))

        self.name_entry = ctk.CTkEntry(
            self,
            placeholder_text="Digite o nome do projeto",
            width=360,
        )
        self.name_entry.pack(padx=20, pady=(0, 20))

        # Project description
        desc_label = ctk.CTkLabel(
            self,
            text="Descrição:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        desc_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.desc_text = ctk.CTkTextbox(
            self,
            width=360,
            height=100,
        )
        self.desc_text.pack(padx=20, pady=(0, 20))

        # Project instructions
        inst_label = ctk.CTkLabel(
            self,
            text="Instruções:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        inst_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.inst_text = ctk.CTkTextbox(
            self,
            width=360,
            height=150,
        )
        self.inst_text.pack(padx=20, pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=100,
            fg_color=self.colors["surface"],
            hover_color=self.colors["surface_light"],
            command=self.destroy,
        )
        cancel_btn.pack(side="left")

        # Save button
        save_btn = ctk.CTkButton(
            button_frame,
            text="Salvar",
            width=100,
            command=self._save_project,
        )
        save_btn.pack(side="right")

        # Load project data if editing
        if project:
            self.name_entry.insert(0, project["name"])
            self.desc_text.insert("1.0", project["description"])
            self.inst_text.insert("1.0", project.get("instructions", ""))

    def _setup_grab(self):
        """Setup grab after window is ready"""
        try:
            self.grab_set()
        except Exception as e:
            logger.error(f"Error grabbing focus: {str(e)}")

    def _save_project(self):
        """Save project data"""
        try:
            name = self.name_entry.get().strip()
            description = self.desc_text.get("1.0", "end-1c").strip()
            instructions = self.inst_text.get("1.0", "end-1c").strip()

            if not name:
                messagebox.showerror("Erro", "O nome do projeto é obrigatório.")
                return

            if not description:
                messagebox.showerror("Erro", "A descrição do projeto é obrigatória.")
                return

            project_data = {
                "name": name,
                "description": description,
                "instructions": instructions,
            }

            if self.project_id:
                project_data["id"] = self.project_id

            if self.on_save:
                self.on_save(project_data)

            self.destroy()

        except Exception as e:
            logger.error(f"Error saving project: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível salvar o projeto.")

    def show(self):
        """Show the panel"""
        try:
            # Center the window
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
            x = (self.master.winfo_screenwidth() // 2) - (width // 2)
            y = (self.master.winfo_screenheight() // 2) - (height // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")

            # Make sure we're showing
            self.deiconify()

            # Set focus after a short delay to ensure window is ready
            self.after(200, self._set_focus)

        except Exception as e:
            logger.error(f"Error showing project panel: {str(e)}")
            messagebox.showerror(
                "Erro", "Não foi possível mostrar o painel do projeto."
            )

    def _set_focus(self):
        """Set focus after window is ready"""
        try:
            self.focus_force()

            # Make sure the entry gets focus
            if hasattr(self, "name_entry"):
                self.name_entry.focus_set()
        except Exception as e:
            logger.error(f"Error setting focus: {str(e)}")


class MessagesContainer(ctk.CTkScrollableFrame):
    """Improved container for chat messages"""

    def __init__(self, master, copy_callback=None, **kwargs):
        """Initialize messages container"""
        self.colors = kwargs.pop("colors", None)
        super().__init__(master, **kwargs)

        # Set callbacks
        self.copy_callback = copy_callback

        # Initialize message list
        self.messages = []

        # Flag to track if welcome suggestions have been added
        self.welcome_suggestions_added = False

    def _add_welcome_suggestions(self):
        """Add welcome suggestions chips"""
        # Don't add welcome suggestions if already added
        if self.welcome_suggestions_added:
            return

        # Mark suggestions as added
        self.welcome_suggestions_added = True

        # Suggestions container
        suggestions_frame = ctk.CTkFrame(self, fg_color="transparent", height=100)
        suggestions_frame.pack(fill="x", pady=(20, 30))

        # Suggestions title
        suggestions_title = ctk.CTkLabel(
            suggestions_frame,
            text="Sugestões para começar:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text_secondary"],
        )
        suggestions_title.pack(anchor="w", pady=(0, 10))

        # Suggestions row 1
        row1 = ctk.CTkFrame(suggestions_frame, fg_color="transparent")
        row1.pack(fill="x", pady=4)

        # Suggestions row 2
        row2 = ctk.CTkFrame(suggestions_frame, fg_color="transparent")
        row2.pack(fill="x", pady=4)

        # Suggestions list
        suggestions = [
            "Como criar um novo projeto?",
            "Como exportar uma conversa?",
            "O que são templates?",
            "Como usar anexos?",
        ]

        # Create suggestion chips
        for i, suggestion in enumerate(suggestions):
            row = row1 if i < 2 else row2

            chip = ctk.CTkButton(
                row,
                text=suggestion,
                font=ctk.CTkFont(size=13),
                height=32,
                corner_radius=16,
                fg_color=self.colors["surface"],
                hover_color=self.colors["surface_hover"],
                text_color=self.colors["text"],
                border_width=1,
                border_color=self.colors["border"],
                command=lambda s=suggestion: self._handle_suggestion(s),
            )
            chip.pack(side="left", padx=(0, 8))

    def _handle_suggestion(self, suggestion):
        """Handle suggestion click"""
        # Find parent App instance
        parent = self.winfo_toplevel()

        # Send suggestion as message
        if hasattr(parent, "text_input") and hasattr(parent, "send_message"):
            parent.text_input.delete("1.0", "end")
            parent.text_input.insert("1.0", suggestion)
            parent.send_message()

    def add_message(self, content, is_user=False, with_animation=True):
        """Add message to container"""
        try:
            # Message frame
            message_frame = ctk.CTkFrame(
                self,
                fg_color=self.colors["surface"]
                if not is_user
                else self.colors["primary"],
                corner_radius=16,
            )

            # Create with 0 width for animation
            if with_animation:
                message_frame.pack(fill="x", pady=8, padx=(24, 24 if is_user else 64))
                message_frame.update()  # Force update to get width
                original_width = message_frame.winfo_width()
                message_frame.pack_forget()
                message_frame.configure(width=0)

            # Position based on sender
            if is_user:
                message_frame.pack(fill="x", pady=8, anchor="e", padx=(64, 24))
            else:
                message_frame.pack(fill="x", pady=8, anchor="w", padx=(24, 64))

            # Message content
            message_content = ctk.CTkLabel(
                message_frame,
                text=content,
                font=ctk.CTkFont(size=14),
                wraplength=600,  # Limit width for better readability
                justify="left",
                anchor="w",
                text_color=self.colors["text_light"]
                if is_user
                else self.colors["text"],
                pady=12,
                padx=16,
            )
            message_content.pack(fill="both", expand=True)

            # Add to messages list
            self.messages.append({
                "frame": message_frame,
                "content": content,
                "is_user": is_user,
            })

            # Animate message appearance
            if with_animation:
                self._animate_message(message_frame, original_width)

            # Add option menu for user messages
            if is_user:
                self._add_message_options(message_frame, content)

            # Scroll to the new message
            self._scroll_to_bottom()

            return message_frame

        except Exception as e:
            import logging

            logging.getLogger("UCAN").error(f"Error adding message: {str(e)}")
            return None

    def _animate_message(self, frame, target_width, duration=15):
        """Animate message appearance with improved animation"""
        try:
            # Get current width
            current_width = frame.winfo_width()

            # Calculate steps
            step_size = (target_width - current_width) / duration

            # Also add fade-in effect by adjusting opacity
            for widget in frame.winfo_children():
                if hasattr(widget, "configure") and hasattr(widget, "cget"):
                    current_fg = widget.cget("fg_color")
                    if isinstance(current_fg, tuple) and len(current_fg) == 2:
                        r, g, b = self._hex_to_rgb(current_fg[1])
                        widget.configure(
                            fg_color=(current_fg[0], f"#{r:02x}{g:02x}{b:02x}20")
                        )

            def animate_step(step):
                if step < duration:
                    # Calculate new width
                    new_width = int(current_width + (step_size * step))
                    frame.configure(width=new_width)

                    # Gradually increase opacity
                    opacity = min(1.0, step / duration * 1.2)  # Slightly faster fade-in

                    # Update opacity of all child widgets
                    for widget in frame.winfo_children():
                        if hasattr(widget, "configure") and hasattr(widget, "cget"):
                            current_fg = widget.cget("fg_color")
                            if isinstance(current_fg, tuple) and len(current_fg) == 2:
                                r, g, b = self._hex_to_rgb(current_fg[1])
                                alpha = int(opacity * 255)
                                widget.configure(
                                    fg_color=(
                                        current_fg[0],
                                        f"#{r:02x}{g:02x}{b:02x}{alpha:02x}",
                                    )
                                )

                    # Schedule next step
                    frame.after(10, lambda: animate_step(step + 1))
                else:
                    # Final state - restore full opacity
                    for widget in frame.winfo_children():
                        if hasattr(widget, "configure") and hasattr(widget, "cget"):
                            current_fg = widget.cget("fg_color")
                            if isinstance(current_fg, tuple) and len(current_fg) == 2:
                                r, g, b = self._hex_to_rgb(current_fg[1])
                                widget.configure(
                                    fg_color=(current_fg[0], f"#{r:02x}{g:02x}{b:02x}")
                                )

                    frame.configure(width=target_width)
                    frame.pack_propagate(True)  # Allow resizing again

            # Start animation
            animate_step(1)

        except Exception as e:
            import logging

            logging.getLogger("UCAN").error(f"Error animating message: {str(e)}")

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values"""
        # Remove # if present
        hex_color = hex_color.lstrip("#")

        # Convert to RGB
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def _add_message_options(self, message_frame, content):
        """Add options menu to message"""
        try:
            # Menu button
            options_btn = ctk.CTkButton(
                message_frame,
                text="•••",
                width=24,
                height=24,
                corner_radius=12,
                fg_color="transparent",
                hover_color=self.colors["primary_dark"],
                text_color=self.colors["text_light"],
                font=ctk.CTkFont(size=10),
                command=lambda: self._show_message_menu(message_frame, content),
            )
            options_btn.place(relx=1.0, rely=0, x=-8, y=8)

        except Exception as e:
            import logging

            logging.getLogger("UCAN").error(f"Error adding message options: {str(e)}")

    def _show_message_menu(self, message_frame, content):
        """Show message options menu"""
        try:
            # Create popup menu
            menu = tk.Menu(
                self,
                tearoff=0,
                bg=self.colors["surface"],
                fg=self.colors["text"],
                activebackground=self.colors["surface_hover"],
            )

            # Add menu items
            menu.add_command(
                label="Copiar", command=lambda: self._copy_message(content)
            )
            menu.add_command(
                label="Editar", command=lambda: self._edit_message(message_frame)
            )
            menu.add_separator()
            menu.add_command(
                label="Deletar", command=lambda: self._delete_message(message_frame)
            )

            # Show menu at button position
            try:
                menu.tk_popup(
                    message_frame.winfo_rootx() + message_frame.winfo_width() - 10,
                    message_frame.winfo_rooty() + 20,
                )
            finally:
                menu.grab_release()

        except Exception as e:
            import logging

            logging.getLogger("UCAN").error(f"Error showing message menu: {str(e)}")

    def _copy_message(self, content):
        """Copy message content"""
        if self.copy_callback:
            self.copy_callback(content)

    def _edit_message(self, message_frame):
        """Edit message"""
        try:
            # Message content is the first label in the frame
            for widget in message_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    content = widget.cget("text")

                    # Create edit box
                    edit_box = ctk.CTkTextbox(
                        message_frame,
                        fg_color=self.colors["primary_dark"],
                        border_width=0,
                        text_color=self.colors["text_light"],
                        font=ctk.CTkFont(size=14),
                        height=100,
                    )
                    edit_box.pack(fill="both", expand=True, padx=12, pady=12)
                    edit_box.insert("1.0", content)
                    edit_box.focus()

                    # Hide original content
                    widget.pack_forget()

                    # Add buttons
                    btn_frame = ctk.CTkFrame(
                        message_frame,
                        fg_color="transparent",
                    )
                    btn_frame.pack(fill="x", padx=12, pady=(0, 8))

                    def save_edit():
                        new_content = edit_box.get("1.0", "end-1c")
                        widget.configure(text=new_content)

                        # Restore UI
                        edit_box.destroy()
                        btn_frame.destroy()
                        widget.pack(fill="both", expand=True)

                        # Update in messages list
                        for msg in self.messages:
                            if msg["frame"] == message_frame:
                                msg["content"] = new_content
                                break

                    def cancel_edit():
                        # Restore UI
                        edit_box.destroy()
                        btn_frame.destroy()
                        widget.pack(fill="both", expand=True)

                    # Save button
                    save_btn = ctk.CTkButton(
                        btn_frame,
                        text="Salvar",
                        font=ctk.CTkFont(size=12),
                        width=80,
                        height=28,
                        corner_radius=14,
                        fg_color=self.colors["surface_light"],
                        hover_color=self.colors["surface_hover"],
                        text_color=self.colors["text"],
                        command=save_edit,
                    )
                    save_btn.pack(side="right", padx=4)

                    # Cancel button
                    cancel_btn = ctk.CTkButton(
                        btn_frame,
                        text="Cancelar",
                        font=ctk.CTkFont(size=12),
                        width=80,
                        height=28,
                        corner_radius=14,
                        fg_color=self.colors["surface_light"],
                        hover_color=self.colors["surface_hover"],
                        text_color=self.colors["text"],
                        command=cancel_edit,
                    )
                    cancel_btn.pack(side="right", padx=4)

                    break

        except Exception as e:
            import logging

            logging.getLogger("UCAN").error(f"Error editing message: {str(e)}")

    def _delete_message(self, message_frame):
        """Delete message"""
        # Ask for confirmation using root window
        root = self.winfo_toplevel()
        result = messagebox.askyesno(
            "Confirmar", "Deseja realmente excluir esta mensagem?"
        )

        if result:
            # Remove from messages list
            self.messages = [
                msg for msg in self.messages if msg["frame"] != message_frame
            ]
            # Remove from UI
            message_frame.destroy()

    def clear_messages(self):
        """Clear all messages from container"""
        try:
            for message in self.messages:
                if "frame" in message and message["frame"].winfo_exists():
                    message["frame"].destroy()

            self.messages = []

            # Reset welcome suggestions flag
            self.welcome_suggestions_added = False

            # Clear any other widgets
            for widget in self.winfo_children():
                widget.destroy()

        except Exception as e:
            import logging

            logging.getLogger("UCAN").error(f"Error clearing messages: {str(e)}")

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the messages"""
        try:
            self.update_idletasks()
            self._parent_canvas.yview_moveto(1.0)
        except Exception as e:
            import logging

            logging.getLogger("UCAN").error(f"Error scrolling: {str(e)}")

    def refresh_theme(self):
        """Refresh message theme"""
        try:
            # Update each message color
            for msg in self.messages:
                is_user = msg.get("is_user", False)
                frame = msg.get("frame")

                if frame and frame.winfo_exists():
                    # Update frame color
                    frame.configure(
                        fg_color=self.colors["primary"]
                        if is_user
                        else self.colors["surface"]
                    )

                    # Update text color in child labels
                    for child in frame.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            child.configure(
                                text_color=self.colors["text_light"]
                                if is_user
                                else self.colors["text"]
                            )
        except Exception as e:
            import logging

            logging.getLogger("UCAN").error(f"Error refreshing theme: {str(e)}")
