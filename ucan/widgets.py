import datetime
import logging
import re
from tkinter import messagebox
from typing import Callable, Dict, Optional

import customtkinter as ctk
import markdown2  # Add this import

from .theme import LAYOUT, ThemeManager

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
    """Frame com scroll para mensagens"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

    def add_message(self, message: str, sender: str) -> ctk.CTkFrame:
        """Adiciona uma mensagem ao frame"""
        # Frame da mensagem
        message_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["surface"] if sender == "Você" else "transparent",
            corner_radius=LAYOUT["border_radius"]["medium"],
        )
        message_frame.grid(
            row=len(self.messages),
            column=0,
            sticky="ew",
            padx=LAYOUT["padding"]["medium"],
            pady=(0, LAYOUT["padding"]["small"]),
        )
        self.grid_columnconfigure(0, weight=1)

        # Container interno para conteúdo e ações
        content_frame = ctk.CTkFrame(
            message_frame,
            fg_color="transparent",
        )
        content_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT["padding"]["small"],
            pady=LAYOUT["padding"]["small"],
        )
        message_frame.grid_columnconfigure(0, weight=1)

        # Container para ações
        actions_frame = ctk.CTkFrame(
            message_frame,
            fg_color="transparent",
            height=24,
        )
        actions_frame.grid(
            row=0,
            column=1,
            sticky="e",
            padx=5,
            pady=5,
        )

        # Texto da mensagem
        message_label = ctk.CTkLabel(
            content_frame,
            text=f"{sender}\n{message}",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.colors["text"],
            justify="left",
            anchor="w",
            wraplength=600,
        )
        message_label.grid(row=0, column=0, sticky="w")

        # Adiciona à lista de mensagens
        self.messages.append((message_frame, message_label))

        # Retorna o frame da mensagem para adicionar ações
        return message_frame

    def clear_messages(self):
        """Limpa todas as mensagens"""
        for frame, _ in self.messages:
            frame.destroy()
        self.messages = []

    def _scroll_to_bottom(self):
        """Rola para a última mensagem"""
        try:
            canvas = self._parent_canvas
            canvas.update_idletasks()
            canvas.yview_moveto(1.0)
        except Exception as e:
            logger.error(f"Erro ao rolar para o final: {str(e)}")


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
        self.grab_set()

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

            # Show window
            self.deiconify()
            self.focus_force()

        except Exception as e:
            logger.error(f"Error showing project panel: {str(e)}")
            messagebox.showerror(
                "Erro", "Não foi possível mostrar o painel do projeto."
            )
