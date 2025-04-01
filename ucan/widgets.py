import datetime
import logging
import re
from typing import Callable, Dict, Optional

import customtkinter as ctk
import markdown2  # Add this import
import messagebox

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
    """Indicador animado de 'pensando'"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

        # Dots
        self.dots = []
        for i in range(3):
            dot = ctk.CTkLabel(
                self,
                text="•",
                font=ctk.CTkFont(size=24),
                text_color=self.colors["text_secondary"],
                width=10,
            )
            dot.pack(side="left", padx=2)
            self.dots.append(dot)

        self.current_dot = 0
        self.animation_running = False

    def start(self):
        """Inicia a animação"""
        self.animation_running = True
        self._animate()

    def stop(self):
        """Para a animação"""
        self.animation_running = False
        for dot in self.dots:
            dot.configure(text_color=self.colors["text_secondary"])

    def _animate(self):
        """Anima os pontos"""
        if not self.animation_running:
            return

        for i, dot in enumerate(self.dots):
            if i == self.current_dot:
                dot.configure(text_color=self.colors["primary"])
            else:
                dot.configure(text_color=self.colors["text_secondary"])

        self.current_dot = (self.current_dot + 1) % 3
        self.after(300, self._animate)


class ProjectDialog(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        project: Optional[Dict] = None,
        on_save: Optional[Callable[[Dict], None]] = None,
    ):
        super().__init__(parent)
        self.project = project
        self.on_save = on_save
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

        # Configure window
        self.title("Novo Projeto" if not project else "Editar Projeto")
        self.geometry("600x700")
        self.resizable(False, False)

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Project name
        name_label = ctk.CTkLabel(
            main_frame,
            text="Nome do Projeto",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text"],
        )
        name_label.pack(anchor="w", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            main_frame,
            fg_color=self.colors["surface"],
            text_color=self.colors["text"],
            border_color=self.colors["border"],
        )
        self.name_entry.pack(fill="x", pady=(0, 15))
        if project:
            self.name_entry.insert(0, project["name"])

        # Project description
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Descrição",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text"],
        )
        desc_label.pack(anchor="w", pady=(0, 5))

        self.desc_text = ctk.CTkTextbox(
            main_frame,
            height=100,
            fg_color=self.colors["surface"],
            text_color=self.colors["text"],
            border_color=self.colors["border"],
        )
        self.desc_text.pack(fill="x", pady=(0, 15))
        if project:
            self.desc_text.insert("1.0", project["description"])

        # Project instructions
        instructions_label = ctk.CTkLabel(
            main_frame,
            text="Instruções para o Assistente",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text"],
        )
        instructions_label.pack(anchor="w", pady=(0, 5))

        self.instructions_text = ctk.CTkTextbox(
            main_frame,
            height=200,
            fg_color=self.colors["surface"],
            text_color=self.colors["text"],
            border_color=self.colors["border"],
        )
        self.instructions_text.pack(fill="x", pady=(0, 15))
        if project:
            self.instructions_text.insert("1.0", project["instructions"])

        # Model settings
        settings_label = ctk.CTkLabel(
            main_frame,
            text="Configurações do Modelo",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text"],
        )
        settings_label.pack(anchor="w", pady=(0, 5))

        settings_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(0, 15))

        # Model selection
        model_label = ctk.CTkLabel(
            settings_frame,
            text="Modelo:",
            text_color=self.colors["text"],
        )
        model_label.pack(side="left", padx=(0, 10))

        self.model_var = ctk.StringVar(
            value=project["settings"]["model"] if project else "gpt-4"
        )
        model_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["gpt-4", "gpt-3.5-turbo"],
            variable=self.model_var,
            fg_color=self.colors["primary"],
            text_color=self.colors["text_light"],
            button_color=self.colors["primary_hover"],
            button_hover_color=self.colors["secondary"],
        )
        model_menu.pack(side="left", padx=(0, 20))

        # Temperature
        temp_label = ctk.CTkLabel(
            settings_frame,
            text="Temperatura:",
            text_color=self.colors["text"],
        )
        temp_label.pack(side="left", padx=(0, 10))

        self.temp_var = ctk.DoubleVar(
            value=project["settings"]["temperature"] if project else 0.7
        )
        temp_slider = ctk.CTkSlider(
            settings_frame,
            from_=0,
            to=1,
            variable=self.temp_var,
            fg_color=self.colors["surface"],
            progress_color=self.colors["primary"],
            button_color=self.colors["primary"],
            button_hover_color=self.colors["primary_hover"],
        )
        temp_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        temp_value = ctk.CTkLabel(
            settings_frame,
            textvariable=self.temp_var,
            text_color=self.colors["text"],
        )
        temp_value.pack(side="left")

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color=self.colors["surface"],
            text_color=self.colors["text"],
            hover_color=self.colors["surface_light"],
        )
        cancel_button.pack(side="right", padx=(10, 0))

        save_button = ctk.CTkButton(
            button_frame,
            text="Salvar",
            command=self._save_project,
            fg_color=self.colors["primary"],
            text_color=self.colors["text_light"],
            hover_color=self.colors["primary_hover"],
        )
        save_button.pack(side="right")

    def _save_project(self):
        """Save project settings"""
        try:
            project_data = {
                "name": self.name_entry.get().strip(),
                "description": self.desc_text.get("1.0", "end-1c").strip(),
                "instructions": self.instructions_text.get("1.0", "end-1c").strip(),
                "settings": {
                    "model": self.model_var.get(),
                    "temperature": self.temp_var.get(),
                    "max_tokens": 2000,
                },
            }

            if self.project:
                project_data["id"] = self.project["id"]
                project_data["created_at"] = self.project["created_at"]
                project_data["updated_at"] = datetime.datetime.now().isoformat()
                project_data["conversations"] = self.project["conversations"]
                project_data["files"] = self.project["files"]

            if self.on_save:
                self.on_save(project_data)

            self.destroy()

        except Exception as e:
            logger.error(f"Error saving project: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível salvar o projeto.")
