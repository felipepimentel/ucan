import logging
import os
import threading
from tkinter import filedialog, messagebox
from typing import Dict

import customtkinter as ctk

from .attachments import AttachmentManager
from .database import Database
from .llm import LLMProvider
from .projects import ProjectManager
from .theme import LAYOUT, ThemeManager
from .widgets import ProjectPanel, ScrollableMessageFrame, ThinkingIndicator

logger = logging.getLogger("UCAN")


class ChatApp(ctk.CTk):
    """Interface principal do chat"""

    def __init__(self):
        """Inicializa a interface"""
        super().__init__()

        # Configurações da janela
        self.title("UCAN - Chat com IA")
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Tema escuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Inicializa gerenciador de tema
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()

        # Cores
        self.colors = {
            "primary": "#7aa2f7",
            "primary_hover": "#3d59a1",
            "secondary": "#bb9af7",
            "surface": "#1a1b26",
            "surface_light": "#24283b",
            "background": "#16161e",  # Darker background
            "text": "#c0caf5",
            "text_secondary": "#565f89",
            "text_light": "#ffffff",
            "border": "#29394f",
            "error": "#f7768e",
        }

        # Inicializa banco de dados
        self.db = Database()

        # Generate test data if database is empty
        if not self.db.get_all_projects():
            self.db.generate_test_data()

        # Inicializa provedor de AI
        self.ai_provider = LLMProvider()

        # Configurações de notificação
        self.notification_queue = []
        self.is_notification_showing = False

        # Inicializa gerenciador de anexos
        self.attachment_manager = AttachmentManager(self.db)

        # Projeto atual
        self.current_project = None

        # Initialize project manager
        self.project_manager = ProjectManager(self.db)

        # Layout principal
        self.setup_layout()

        # Configura atalhos
        self.setup_input_handling()

        # Load projects
        self.load_projects()

        logger.info("Aplicação inicializada com sucesso")

        # Iniciar chat com assistente
        self.after(500, lambda: self.start_chat())

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
            message_frame.configure(
                fg_color=self.colors["surface_light"]
                if sender == "Você"
                else self.colors["surface"],
                corner_radius=LAYOUT["border_radius"]["medium"],
            )

            # Botões de ação
            actions_frame = message_frame.winfo_children()[1]  # actions_frame
            actions_frame.configure(fg_color="transparent")

            copy_btn = ctk.CTkButton(
                actions_frame,
                text="📋",
                width=24,
                height=24,
                fg_color="transparent",
                hover_color=self.colors["surface"],
                command=lambda: self.copy_message(message),
            )
            copy_btn.grid(row=0, column=0, padx=2)

            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️",
                width=24,
                height=24,
                fg_color="transparent",
                hover_color=self.colors["surface"],
                command=lambda: self.edit_message(message_frame),
            )
            edit_btn.grid(row=0, column=1, padx=2)

            delete_btn = ctk.CTkButton(
                actions_frame,
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

            def show_actions(event=None):
                """Mostra os botões de ação"""
                for btn in [copy_btn, edit_btn, delete_btn]:
                    btn.grid()

            def hide_actions(event=None):
                """Esconde os botões de ação"""
                # Verifica se o mouse ainda está sobre a mensagem ou os botões
                mouse_x = message_frame.winfo_pointerx() - message_frame.winfo_rootx()
                mouse_y = message_frame.winfo_pointery() - message_frame.winfo_rooty()

                if not (
                    0 <= mouse_x <= message_frame.winfo_width()
                    and 0 <= mouse_y <= message_frame.winfo_height()
                ):
                    for btn in [copy_btn, edit_btn, delete_btn]:
                        btn.grid_remove()

            # Bind eventos de hover na mensagem e nos botões
            message_frame.bind("<Enter>", show_actions)
            message_frame.bind("<Leave>", hide_actions)

            for btn in [copy_btn, edit_btn, delete_btn]:
                btn.bind("<Enter>", show_actions)

            # Rola para a última mensagem
            self.messages_frame._scroll_to_bottom()

            # Check scrollbar visibility after adding message
            self.check_messages_scroll()

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
                self.process_attachment(file_path)

        except Exception as e:
            logger.error(f"Erro ao abrir diálogo de arquivo: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível abrir o diálogo de arquivo.")
        finally:
            # Reabilita o botão de envio
            self.send_button.configure(state="normal")
            # Restaura o status
            self.contact_status.configure(text="Pronto para conversar")

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
        self.bind("<Control-Down>", self._next_message)

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
            self.message_entry.insert("1.0", "Digite sua mensagem...")
            self.message_entry.configure(text_color=self.colors["text_secondary"])

    def _clear_placeholder(self, event=None):
        """Remove placeholder quando o campo recebe foco"""
        if self.message_entry.get("1.0", "end-1c").strip() == "Digite sua mensagem...":
            self.message_entry.delete("1.0", "end")
            self.message_entry.configure(text_color=self.colors["text"])

    def _update_char_count(self, event=None):
        """Atualiza o contador de caracteres"""
        try:
            if (
                self.message_entry.get("1.0", "end-1c").strip()
                == "Digite sua mensagem..."
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
                    f.write("<html><body><div class='chat'>\n")
                    for msg in self.messages_frame.messages:
                        sender = msg[1].cget("text").split("\n")[0]
                        content = "\n".join(msg[1].cget("text").split("\n")[1:])
                        f.write(f"<div class='message {sender.lower()}'>\n")
                        f.write(f"<strong>{sender}</strong><br>\n")
                        f.write(f"{content}\n</div>\n")
                    f.write("</div></body></html>")
                else:
                    for msg in self.messages_frame.messages:
                        sender = msg[1].cget("text").split("\n")[0]
                        content = "\n".join(msg[1].cget("text").split("\n")[1:])
                        f.write(f"{sender}:\n{content}\n\n")

            messagebox.showinfo("Sucesso", "Chat exportado com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao exportar chat: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível exportar o chat.")

    def toggle_theme(self):
        """Alterna o tema da aplicação"""
        ctk.set_appearance_mode(
            "dark" if ctk.get_appearance_mode() == "light" else "light"
        )
        self.theme_manager.apply_theme()

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
                self.scroll_button.pack(side="bottom", anchor="se", padx=10, pady=10)
            else:
                self.scroll_button.pack_forget()
        except Exception as e:
            logger.error(f"Erro ao verificar posição de rolagem: {str(e)}")

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

    def show_project_dialog(self, project: Dict = None):
        """Show project creation/edit panel"""
        if not hasattr(self, "project_panel"):
            self.project_panel = ProjectPanel(
                self, project=project, on_save=self._handle_project_save
            )
        else:
            # Update panel if already exists
            self.project_panel.project = project
            if project:
                self.project_panel.project_id = project["id"]
                self.project_panel.name_entry.delete(0, "end")
                self.project_panel.name_entry.insert(0, project["name"])
                self.project_panel.desc_text.delete("1.0", "end")
                self.project_panel.desc_text.insert("1.0", project["description"])
                self.project_panel.inst_text.delete("1.0", "end")
                self.project_panel.inst_text.insert(
                    "1.0", project.get("instructions", "")
                )
            else:
                self.project_panel.project_id = None
                self.project_panel.name_entry.delete(0, "end")
                self.project_panel.desc_text.delete("1.0", "end")
                self.project_panel.inst_text.delete("1.0", "end")

        self.project_panel.show()

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
        """Load projects into the projects frame"""
        try:
            # Clear existing projects
            for widget in self.projects_frame.winfo_children():
                widget.destroy()

            # Load projects from database
            projects = self.project_manager.list_projects()

            for project in projects:
                project_frame = ctk.CTkFrame(
                    self.projects_frame,
                    fg_color=self.colors["background"],
                    corner_radius=LAYOUT["border_radius"]["medium"],
                )
                project_frame.pack(fill="x", pady=4, padx=2)

                # Project name and icon container
                header_frame = ctk.CTkFrame(
                    project_frame,
                    fg_color="transparent",
                )
                header_frame.pack(fill="x", padx=8, pady=(8, 4))

                # Project icon
                icon_frame = ctk.CTkFrame(
                    header_frame,
                    width=24,
                    height=24,
                    corner_radius=LAYOUT["border_radius"]["circle"],
                    fg_color=self.colors["surface_light"],
                )
                icon_frame.pack(side="left", padx=(0, 8))
                icon_frame.pack_propagate(False)

                icon_label = ctk.CTkLabel(
                    icon_frame,
                    text="📋",
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors["text"],
                )
                icon_label.pack(expand=True)

                # Project name
                name_label = ctk.CTkLabel(
                    header_frame,
                    text=project["name"],
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=self.colors["text"],
                    anchor="w",
                )
                name_label.pack(side="left", fill="x", expand=True)

                # Project description preview
                preview = (
                    project["description"][:80] + "..."
                    if len(project["description"]) > 80
                    else project["description"]
                )
                desc_label = ctk.CTkLabel(
                    project_frame,
                    text=preview,
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors["text_secondary"],
                    wraplength=220,
                    justify="left",
                )
                desc_label.pack(anchor="w", padx=8, pady=(0, 8))

                # Project actions
                actions_frame = ctk.CTkFrame(
                    project_frame,
                    fg_color="transparent",
                )
                actions_frame.pack(fill="x", padx=8, pady=(0, 8))

                # Edit button
                edit_btn = ctk.CTkButton(
                    actions_frame,
                    text="✏️",
                    width=24,
                    height=24,
                    fg_color="transparent",
                    hover_color=self.colors["surface"],
                    command=lambda p=project: self.show_project_dialog(p),
                )
                edit_btn.pack(side="right", padx=2)

                # Delete button
                delete_btn = ctk.CTkButton(
                    actions_frame,
                    text="🗑️",
                    width=24,
                    height=24,
                    fg_color="transparent",
                    hover_color=self.colors["surface"],
                    command=lambda p=project: self.delete_project(p),
                )
                delete_btn.pack(side="right", padx=2)

                # Select button
                select_btn = ctk.CTkButton(
                    actions_frame,
                    text="✓",
                    width=24,
                    height=24,
                    fg_color="transparent",
                    hover_color=self.colors["surface"],
                    command=lambda p=project: self.select_project(p),
                )
                select_btn.pack(side="right", padx=2)

                # Hide action buttons initially
                for btn in [edit_btn, delete_btn, select_btn]:
                    btn.pack_forget()

                def show_actions(event=None):
                    """Show action buttons"""
                    for btn in [edit_btn, delete_btn, select_btn]:
                        btn.pack(side="right", padx=2)

                def hide_actions(event=None):
                    """Hide action buttons"""
                    # Check if mouse is still over project frame or buttons
                    mouse_x = (
                        project_frame.winfo_pointerx() - project_frame.winfo_rootx()
                    )
                    mouse_y = (
                        project_frame.winfo_pointery() - project_frame.winfo_rooty()
                    )

                    if not (
                        0 <= mouse_x <= project_frame.winfo_width()
                        and 0 <= mouse_y <= project_frame.winfo_height()
                    ):
                        for btn in [edit_btn, delete_btn, select_btn]:
                            btn.pack_forget()

                # Hover effect for project card
                def on_enter(e):
                    project_frame.configure(fg_color=self.colors["surface_light"])
                    show_actions()

                def on_leave(e):
                    project_frame.configure(fg_color=self.colors["background"])
                    hide_actions()

                # Bind hover events
                project_frame.bind("<Enter>", on_enter)
                project_frame.bind("<Leave>", on_leave)

                for btn in [edit_btn, delete_btn, select_btn]:
                    btn.bind("<Enter>", show_actions)

        except Exception as e:
            logger.error(f"Error loading projects: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível carregar os projetos.")

    def delete_project(self, project: Dict):
        """Delete a project"""
        try:
            if messagebox.askyesno(
                "Confirmar exclusão",
                "Tem certeza que deseja excluir este projeto?",
            ):
                self.project_manager.delete_project(project["id"])
                self.load_projects()

                # Clear current project if it was deleted
                if self.current_project and self.current_project["id"] == project["id"]:
                    self.current_project = None
                    self.contact_name.configure(text="Assistente IA")
                    self.contact_status.configure(text="Pronto para conversar")

        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível excluir o projeto.")

    def select_project(self, project: Dict):
        """Select a project"""
        try:
            self.current_project = project
            self.contact_name.configure(text=project["name"])
            self.contact_status.configure(text=project["description"])
            self.messages_frame.clear_messages()

            # Load project conversations
            conversations = self.project_manager.get_conversations(project["id"])
            for conv in conversations:
                self.add_message(conv["content"], conv["sender"])

        except Exception as e:
            logger.error(f"Error selecting project: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível selecionar o projeto.")

    def process_attachment(self, file_path: str):
        """Process an attachment"""
        try:
            # Process file
            file_info = self.attachment_manager.process_file(file_path)

            # Show attachment preview
            self.attachment_frame.pack(fill="x", pady=5)
            self.attachment_preview.configure(text=f"📎 {os.path.basename(file_path)}")

            # Store current attachment
            self.current_attachment = file_info

        except Exception as e:
            logger.error(f"Error processing attachment: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível processar o anexo.")

    def remove_attachment(self):
        """Remove current attachment"""
        try:
            # Hide attachment frame
            self.attachment_frame.pack_forget()

            # Clear current attachment
            self.current_attachment = None

        except Exception as e:
            logger.error(f"Error removing attachment: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível remover o anexo.")

    def check_messages_scroll(self, event=None):
        """Check if scrollbar is needed"""
        try:
            canvas = self.messages_frame._parent_canvas
            if not canvas.winfo_exists():
                return

            # Get canvas dimensions
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            # Get content dimensions
            content_width = canvas.bbox("all")[2] if canvas.bbox("all") else 0
            content_height = canvas.bbox("all")[3] if canvas.bbox("all") else 0

            # Show/hide scrollbar based on content size
            if content_height > canvas_height:
                self.messages_frame._scrollbar.pack(side="right", fill="y")
            else:
                self.messages_frame._scrollbar.pack_forget()

        except Exception as e:
            logger.error(f"Error checking messages scroll: {str(e)}")

    def setup_layout(self):
        """Setup the main layout"""
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors["surface"],
            corner_radius=0,
            border_width=1,
            border_color=self.colors["border"],
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.sidebar.configure(width=280)  # Slightly narrower

        # Configure sidebar grid
        self.sidebar.grid_rowconfigure(4, weight=1)  # Projects frame expands
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Frame do logo com gradiente
        self.logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.colors["primary"],
            corner_radius=0,
            height=52,  # Slightly shorter
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
            height=40,  # Adjusted height
        )
        logo_container.pack(expand=True, fill="both", padx=LAYOUT["padding"]["medium"])
        logo_container.pack_propagate(False)

        # Logo content container
        logo_content = ctk.CTkFrame(
            logo_container,
            fg_color="transparent",
            height=32,
        )
        logo_content.place(relx=0.5, rely=0.5, anchor="center")

        # Logo icon
        logo_icon = ctk.CTkLabel(
            logo_content,
            text="🤖",
            font=ctk.CTkFont(family="Segoe UI", size=20),  # Slightly smaller
            text_color=self.colors["text_light"],
            height=32,
        )
        logo_icon.pack(side="left", padx=(0, 6))  # Reduced padding

        # Logo text
        self.logo_label = ctk.CTkLabel(
            logo_content,
            text="UCAN",
            font=ctk.CTkFont(
                family="Segoe UI", size=20, weight="bold"
            ),  # Slightly smaller
            text_color=self.colors["text_light"],
            height=32,
        )
        self.logo_label.pack(side="left")

        # Container para título e botão de nova conversa
        chat_header = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=36,  # Adjusted height
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
            font=ctk.CTkFont(
                family="Segoe UI", size=14, weight="bold"
            ),  # Slightly smaller
            text_color=self.colors["text"],
        )
        self.chat_title.pack(side="left")

        # Botão de nova conversa
        new_chat_btn = ctk.CTkButton(
            chat_header,
            text="＋",
            width=28,
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["surface_light"],
            hover_color=self.colors["primary"],
            text_color=self.colors["text"],
            command=self.start_chat,
        )
        new_chat_btn.pack(side="right")

        # Frame do contato
        contact_frame = ctk.CTkFrame(
            self.sidebar,
            corner_radius=LAYOUT["border_radius"]["medium"],
            fg_color=self.colors["surface_light"],
            height=64,  # Slightly shorter
        )
        contact_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=LAYOUT["padding"]["medium"],
            pady=(0, LAYOUT["padding"]["small"]),
        )
        contact_frame.grid_propagate(False)

        # Container para avatar e informações
        info_container = ctk.CTkFrame(
            contact_frame,
            fg_color="transparent",
        )
        info_container.pack(
            fill="both",
            expand=True,
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["small"],
        )

        # Avatar
        avatar_size = 36  # Slightly smaller
        avatar_frame = ctk.CTkFrame(
            info_container,
            width=avatar_size,
            height=avatar_size,
            corner_radius=LAYOUT["border_radius"]["circle"],
            fg_color=self.colors["primary"],
        )
        avatar_frame.pack(side="left", padx=(0, LAYOUT["padding"]["medium"]))
        avatar_frame.pack_propagate(False)

        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text="🤖",
            font=ctk.CTkFont(family="Segoe UI", size=18),  # Adjusted size
            text_color=self.colors["text_light"],
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
            text="Assistente IA",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        name_label.pack(anchor="w")

        # Descrição
        description_label = ctk.CTkLabel(
            text_container,
            text="Chat principal",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.colors["text_secondary"],
            anchor="w",
        )
        description_label.pack(anchor="w")

        # Efeito hover no contato
        def create_hover_effect(frame):
            def on_enter(e):
                frame.configure(fg_color=self.colors["surface"])

            def on_leave(e):
                frame.configure(fg_color=self.colors["surface_light"])

            frame.bind("<Enter>", on_enter)
            frame.bind("<Leave>", on_leave)

        create_hover_effect(contact_frame)

        # Bind para iniciar chat
        contact_frame.bind(
            "<Button-1>",
            lambda e: self.start_chat_with("Assistente IA"),
        )

        # Container para título e botão de novo projeto
        projects_header = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=36,  # Adjusted height
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
            text="＋",
            width=28,
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(size=14, weight="bold"),
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
            scrollbar_fg_color=self.colors["surface_light"],
            scrollbar_button_color=self.colors["primary"],
            scrollbar_button_hover_color=self.colors["primary_hover"],
        )
        self.projects_frame.grid(
            row=4,
            column=0,
            sticky="nsew",
            padx=LAYOUT["padding"]["medium"],
            pady=0,
        )

        # Configure projects scrollbar
        self.projects_frame._scrollbar.configure(
            width=8,  # Thinner scrollbar
            corner_radius=4,
        )

        # Main content
        self.content = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors["background"],
        )
        self.content.pack(side="right", fill="both", expand=True)

        # Top bar
        self.top_bar = ctk.CTkFrame(
            self.content,
            fg_color=self.colors["background"],
            corner_radius=0,
            height=60,
        )
        self.top_bar.pack(fill="x", pady=0)
        self.top_bar.pack_propagate(False)

        # Contact info
        self.contact_name = ctk.CTkLabel(
            self.top_bar,
            text="Assistente IA",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.colors["text"],
        )
        self.contact_name.pack(side="left", padx=LAYOUT["padding"]["medium"])

        self.contact_status = ctk.CTkLabel(
            self.top_bar,
            text="Pronto para conversar",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors["text_secondary"],
        )
        self.contact_status.pack(side="left", padx=LAYOUT["padding"]["small"])

        # Thinking indicator
        self.thinking_indicator = ThinkingIndicator(
            self.top_bar,
            fg_color="transparent",
        )

        # Messages frame
        self.messages_frame = ScrollableMessageFrame(
            self.content,
            fg_color=self.colors["background"],
        )
        self.messages_frame.pack(
            fill="both",
            expand=True,
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["medium"],
        )

        # Input frame
        self.input_frame = ctk.CTkFrame(
            self.content,
            fg_color=self.colors["background"],
        )
        self.input_frame.pack(
            fill="x",
            padx=LAYOUT["padding"]["medium"],
            pady=(0, LAYOUT["padding"]["medium"]),
        )

        # Message entry
        self.message_entry = ctk.CTkTextbox(
            self.input_frame,
            height=60,
            fg_color=self.colors["surface_light"],
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["text"],
            corner_radius=LAYOUT["border_radius"]["medium"],
        )
        self.message_entry.pack(fill="x", pady=(0, LAYOUT["padding"]["small"]))
        self.message_entry.bind("<Return>", self.handle_enter)
        self.message_entry.bind("<FocusIn>", self._clear_placeholder)
        self.message_entry.bind("<FocusOut>", self._add_placeholder)
        self.message_entry.bind("<Key>", self._update_char_count)

        # Attachment frame
        self.attachment_frame = ctk.CTkFrame(
            self.input_frame,
            fg_color=self.colors["surface"],
            corner_radius=LAYOUT["border_radius"]["small"],
            height=40,
        )
        self.attachment_frame.pack_forget()

        # Attachment preview
        self.attachment_preview = ctk.CTkLabel(
            self.attachment_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors["text"],
        )
        self.attachment_preview.pack(side="left", padx=LAYOUT["padding"]["small"])

        # Remove attachment button
        remove_btn = ctk.CTkButton(
            self.attachment_frame,
            text="×",
            width=24,
            height=24,
            fg_color="transparent",
            hover_color=self.colors["surface_light"],
            command=self.remove_attachment,
        )
        remove_btn.pack(side="right", padx=LAYOUT["padding"]["small"])

        # Input actions
        actions_frame = ctk.CTkFrame(
            self.input_frame,
            fg_color="transparent",
        )
        actions_frame.pack(fill="x")

        # Character counter
        self.char_counter = ctk.CTkLabel(
            actions_frame,
            text="0",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors["text_secondary"],
        )
        self.char_counter.pack(side="left", padx=LAYOUT["padding"]["small"])

        # Send button
        self.send_button = ctk.CTkButton(
            actions_frame,
            text="Enviar",
            width=80,
            height=32,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self.send_message,
            state="disabled",
            corner_radius=LAYOUT["border_radius"]["medium"],
        )
        self.send_button.pack(side="right", padx=LAYOUT["padding"]["small"])

        # Add placeholder
        self._add_placeholder()

        # Scroll button
        self.scroll_button = ctk.CTkButton(
            self.content,
            text="↓",
            width=32,
            height=32,
            corner_radius=16,
            fg_color=self.colors["surface"],
            hover_color=self.colors["primary"],
            command=self._scroll_to_bottom,
        )
        self.scroll_button.pack(side="bottom", anchor="se", padx=10, pady=10)
        self.scroll_button.pack_forget()

        # Bind scroll events
        self.messages_frame._parent_canvas.bind(
            "<Configure>", self._check_scroll_position
        )
        self.messages_frame._parent_canvas.bind(
            "<MouseWheel>", self._check_scroll_position
        )
        self.messages_frame._parent_canvas.bind(
            "<Button-4>", self._check_scroll_position
        )
        self.messages_frame._parent_canvas.bind(
            "<Button-5>", self._check_scroll_position
        )

        # Center window
        self.center_window()
