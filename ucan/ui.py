import logging
import os
import tkinter
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .ai_provider import AIProvider
from .database import Database
from .theme import COLORS, LAYOUT, ThemeManager
from .widgets import ScrollableMessageFrame

logger = logging.getLogger("UCAN")


class ChatApp(ctk.CTk):
    def __init__(self):
        """Inicializa a interface do usuário"""
        super().__init__()

        # Configura a janela principal
        self.title("UCAN - Chat com IA")
        self.geometry("1200x800")  # Aumentado para melhor visualização
        self.minsize(800, 600)  # Tamanho mínimo para garantir usabilidade

        # Configura o tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configura o grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Frame lateral (contatos)
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=COLORS["surface"],
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 1),  # Borda direita fina
            pady=0,
        )
        self.sidebar.grid_rowconfigure(2, weight=1)

        # Frame do logo com gradiente
        self.logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLORS["primary"],
            corner_radius=0,
            height=60,
            border_width=0,
        )
        self.logo_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=0,
            pady=(0, 1),  # Borda inferior fina
        )
        self.logo_frame.grid_propagate(False)

        # Gradiente do logo
        gradient_frame = ctk.CTkFrame(
            self.logo_frame,
            fg_color="transparent",
            height=60,
            corner_radius=0,
        )
        gradient_frame.pack(fill="both", expand=True)
        gradient_frame.pack_propagate(False)

        # Logo com efeito de gradiente
        self.logo_label = ctk.CTkLabel(
            gradient_frame,
            text="UCAN",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS["text_light"],
        )
        self.logo_label.pack(expand=True)

        # Efeito de gradiente
        self._create_gradient(gradient_frame)

        # Título da seção
        self.chat_title = ctk.CTkLabel(
            self.sidebar,
            text="Assistente",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        self.chat_title.grid(
            row=1,
            column=0,
            sticky="w",
            padx=LAYOUT["padding"]["medium"],
            pady=LAYOUT["padding"]["medium"],
        )

        # Lista de contatos com design clean
        self.contacts_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            corner_radius=0,
            fg_color=COLORS["surface"],
            border_width=0,
        )
        self.contacts_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=0,
            pady=0,
        )
        self.contacts_frame.grid_columnconfigure(0, weight=1)

        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["background"],
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
            fg_color=COLORS["surface"],
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
        contact_info.pack(fill="both", expand=True, padx=LAYOUT["padding"]["medium"])

        # Ícone do assistente
        avatar_size = 36
        self.contact_avatar = ctk.CTkFrame(
            contact_info,
            width=avatar_size,
            height=avatar_size,
            corner_radius=LAYOUT["border_radius"]["circle"],
            fg_color=COLORS["primary"],
        )
        self.contact_avatar.pack(side="left", padx=(0, LAYOUT["padding"]["medium"]))
        self.contact_avatar.pack_propagate(False)

        self.contact_avatar_label = ctk.CTkLabel(
            self.contact_avatar,
            text="🤖",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color=COLORS["text_light"],
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
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.contact_name.pack(anchor="w")

        # Status do assistente
        self.contact_status = ctk.CTkLabel(
            contact_text,
            text="Pronto para conversar",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self.contact_status.pack(anchor="w")

        # Frame de mensagens com overlay para botão de rolagem
        self.messages_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=0,
            fg_color="transparent",
        )
        self.messages_container.grid(row=1, column=0, sticky="nsew")
        self.messages_container.grid_rowconfigure(0, weight=1)
        self.messages_container.grid_columnconfigure(0, weight=1)

        # Frame de mensagens
        self.messages_frame = ScrollableMessageFrame(
            self.messages_container,
            corner_radius=0,
            fg_color=COLORS["background"],
            scrollbar_fg_color=COLORS["surface"],
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        self.messages_frame.grid(row=0, column=0, sticky="nsew")

        # Botão de rolar para baixo
        self.scroll_button = ctk.CTkButton(
            self.messages_container,
            text="↓",
            width=36,
            height=36,
            corner_radius=LAYOUT["border_radius"]["circle"],
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_light"],
            text_color=COLORS["primary"],
        )
        self.scroll_button.grid(row=0, column=0, sticky="se", padx=20, pady=20)
        self.scroll_button.configure(command=self._scroll_to_bottom)
        self.scroll_button.grid_remove()  # Inicialmente oculto

        # Frame de entrada
        self.input_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["surface"],
            corner_radius=0,
            height=60,
            border_width=0,
        )
        self.input_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=0,
            pady=(1, 0),  # Borda superior fina
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
            pady=LAYOUT["padding"]["small"],
        )

        # Botão de anexo
        self.attach_button = ctk.CTkButton(
            input_container,
            text="📎",
            width=36,
            height=36,
            corner_radius=LAYOUT["border_radius"]["circle"],
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=COLORS["surface_light"],
            text_color=COLORS["text_primary"],
        )
        self.attach_button.pack(side="left", padx=(0, LAYOUT["padding"]["small"]))
        self.attach_button.configure(command=self.show_file_dialog)

        # Frame do input com fundo
        input_background = ctk.CTkFrame(
            input_container,
            fg_color=COLORS["surface_light"],
            corner_radius=LAYOUT["border_radius"]["medium"],
        )
        input_background.pack(
            side="left", fill="x", expand=True, padx=(0, LAYOUT["padding"]["small"])
        )

        # Container para input e contador
        input_wrapper = ctk.CTkFrame(
            input_background,
            fg_color="transparent",
        )
        input_wrapper.pack(side="left", fill="both", expand=True)

        # Campo de texto
        self.message_entry = ctk.CTkTextbox(
            input_wrapper,
            height=80,
            corner_radius=LAYOUT["border_radius"]["medium"],
            fg_color="transparent",
            border_width=0,
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
        )
        self.message_entry.pack(
            side="top",
            fill="both",
            expand=True,
            padx=LAYOUT["padding"]["medium"],
        )

        # Contador de caracteres
        self.char_counter = ctk.CTkLabel(
            input_wrapper,
            text="0/2000",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_secondary"],
        )
        self.char_counter.pack(
            side="right",
            padx=LAYOUT["padding"]["medium"],
            pady=(0, 2),
        )

        # Bind para atualizar contador
        self.message_entry.bind("<KeyRelease>", self._update_char_count)

        # Botão de enviar mais elegante e integrado
        self.send_button = ctk.CTkButton(
            input_background,
            text="➤",
            width=36,
            height=36,
            corner_radius=LAYOUT["border_radius"]["circle"],
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS["primary"],
            text_color=COLORS["primary"],
            border_width=2,
            border_color=COLORS["primary"],
        )
        self.send_button.pack(side="right", padx=LAYOUT["padding"]["small"])
        self.send_button.configure(command=self.send_message)

        # Efeito de hover mais suave no botão
        self.send_button.bind("<Enter>", self._highlight_send_button)
        self.send_button.bind("<Leave>", self._restore_send_button)

        # Bind Enter para enviar
        self.message_entry.bind("<Return>", self.handle_enter)
        self.message_entry.bind(
            "<Shift-Return>", lambda e: None
        )  # Permite quebra de linha com Shift+Enter

        # Placeholder para o campo de mensagem
        self.message_entry.insert("1.0", "Digite sua mensagem...")
        self.message_entry.configure(text_color=COLORS["text_secondary"])
        self.message_entry.bind("<FocusIn>", self._clear_placeholder)
        self.message_entry.bind("<FocusOut>", self._add_placeholder)

        # Bind para mostrar/ocultar botão de rolagem
        self.messages_frame.bind("<MouseWheel>", self._check_scroll_position)

        # Inicializa banco de dados
        self.db = Database()

        # Inicializa gerenciador de temas
        self.theme_manager = ThemeManager()

        # Inicializa provedor de AI
        self.ai_provider = AIProvider()

        # Configurações de notificação
        self.notifications_enabled = True

        # Contato atual
        self.current_contact = "Assistente IA"

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

        logger.info("Aplicação inicializada com sucesso")

    def populate_contacts(self):
        """Popula a lista de contatos"""
        # Apenas a LLM como contato
        contact_frame = ctk.CTkFrame(
            self.contacts_frame,
            corner_radius=LAYOUT["border_radius"]["small"],
            fg_color="transparent",
            height=60,
        )
        contact_frame.pack(
            fill="x", padx=LAYOUT["padding"]["small"], pady=LAYOUT["padding"]["small"]
        )
        contact_frame.pack_propagate(False)

        # Container para avatar e informações
        info_container = ctk.CTkFrame(
            contact_frame,
            fg_color="transparent",
        )
        info_container.pack(fill="both", expand=True, padx=LAYOUT["padding"]["small"])

        # Avatar (círculo com ícone de IA)
        avatar_size = 36
        avatar_frame = ctk.CTkFrame(
            info_container,
            width=avatar_size,
            height=avatar_size,
            corner_radius=LAYOUT["border_radius"]["circle"],
            fg_color=COLORS["primary"],
        )
        avatar_frame.pack(side="left", padx=(0, LAYOUT["padding"]["small"]))
        avatar_frame.pack_propagate(False)

        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text="🤖",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color=COLORS["text_light"],
        )
        avatar_label.pack(expand=True)

        # Container para nome
        text_container = ctk.CTkFrame(
            info_container,
            fg_color="transparent",
        )
        text_container.pack(side="left", fill="both", expand=True)

        # Nome
        name_label = ctk.CTkLabel(
            text_container,
            text="Assistente IA",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        name_label.pack(anchor="w")

        # Descrição
        description_label = ctk.CTkLabel(
            text_container,
            text="Chat inteligente",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        description_label.pack(anchor="w")

        # Bind click com efeito hover melhorado
        callback = lambda e: self.start_chat()
        for widget in [
            contact_frame,
            info_container,
            avatar_frame,
            avatar_label,
            text_container,
            name_label,
            description_label,
        ]:
            widget.bind("<Button-1>", callback)
            widget.bind(
                "<Enter>",
                lambda e, f=contact_frame: f.configure(
                    fg_color=COLORS["surface_light"]
                ),
            )
            widget.bind(
                "<Leave>",
                lambda e, f=contact_frame: f.configure(fg_color="transparent"),
            )

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
        try:
            # Obtém a mensagem
            message = self.message_entry.get("1.0", "end-1c").strip()
            if not message:
                return

            # Adiciona ao histórico
            if not hasattr(self, "message_history"):
                self.message_history = []
            self.message_history.append(message)
            self.history_index = -1

            # Limpa o campo
            self.message_entry.delete("1.0", "end")

            # Adiciona a mensagem ao chat
            self.add_message(message, "Você")

            # Obtém resposta do bot
            response = self.ai_provider.generate_response(message)

            # Adiciona resposta do bot após um delay
            self.after(1000, lambda: self.add_message(response, "Assistente IA"))

            # Salva a mensagem no banco de dados
            self.db.save_message("Você", self.current_contact, message)
            self.db.save_message("Assistente IA", self.current_contact, response)

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível enviar a mensagem.")

    def add_message(self, message, sender):
        """Adiciona uma mensagem ao chat"""
        try:
            # Adiciona a mensagem com animação
            self.messages_frame.add_message(message, sender)

            # Atualiza o status do assistente
            if sender == "Assistente IA":
                self.contact_status.configure(text="Digitando...")
                self.after(
                    1000,
                    lambda: self.contact_status.configure(text="Pronto para conversar"),
                )

            # Rola para a última mensagem
            self.after(100, self._scroll_to_bottom)

        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem: {str(e)}")

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
            self.message_entry.insert("1.0", "Digite sua mensagem...")
            self.message_entry.configure(text_color=COLORS["text_secondary"])

    def _clear_placeholder(self, event=None):
        """Remove placeholder quando o campo recebe foco"""
        if self.message_entry.get("1.0", "end-1c") == "Digite sua mensagem...":
            self.message_entry.delete("1.0", "end")
            self.message_entry.configure(text_color=COLORS["text_primary"])

    def _highlight_send_button(self, event):
        """Destaca o botão de enviar no hover"""
        self.send_button.configure(
            text="➤",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=COLORS["primary"],
            text_color=COLORS["text_light"],
            border_color=COLORS["primary"],
        )

    def _restore_send_button(self, event):
        """Restaura o botão de enviar após o hover"""
        self.send_button.configure(
            text="➤",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent",
            text_color=COLORS["primary"],
            border_color=COLORS["primary"],
        )

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

    def _scroll_to_bottom(self):
        """Rola para a última mensagem"""
        try:
            self.messages_frame._scroll_to_bottom()
        except Exception as e:
            logger.error(f"Erro ao rolar para o final: {str(e)}")

    def _copy_message(self, text, bubble):
        """Copia uma mensagem e mostra feedback visual"""
        try:
            # Copia para o clipboard
            self.clipboard_clear()
            self.clipboard_append(text)

            # Salva a cor original
            original_color = bubble.cget("fg_color")

            # Feedback visual
            bubble.configure(fg_color=COLORS["primary"])

            # Restaura após 200ms
            self.after(200, lambda: bubble.configure(fg_color=original_color))

        except Exception as e:
            logger.error(f"Erro ao copiar mensagem: {str(e)}")
            messagebox.showerror(
                "Erro", "Não foi possível copiar a mensagem. Tente novamente."
            )

    def _update_char_count(self, event=None):
        """Atualiza o contador de caracteres"""
        try:
            if self.message_entry.get("1.0", "end-1c") == "Digite sua mensagem...":
                count = 0
            else:
                count = len(self.message_entry.get("1.0", "end-1c"))

            self.char_counter.configure(text=f"{count}/2000")

            # Muda a cor se passar do limite
            if count > 2000:
                self.char_counter.configure(text_color=COLORS["error"])
                self.send_button.configure(state="disabled")
            else:
                self.char_counter.configure(text_color=COLORS["text_secondary"])
                self.send_button.configure(state="normal")

        except Exception as e:
            logger.error(f"Erro ao atualizar contador: {str(e)}")

    def setup_input_handling(self):
        """Configura o tratamento de entrada"""
        # Bind Enter para enviar
        self.message_entry.bind("<Return>", self.handle_enter)
        self.message_entry.bind(
            "<Shift-Return>", lambda e: None
        )  # Permite quebra de linha com Shift+Enter

        # Bind Ctrl+Enter para enviar
        self.message_entry.bind("<Control-Return>", self.send_message)

        # Bind Ctrl+L para limpar chat
        self.bind("<Control-l>", lambda e: self.clear_chat())

        # Bind Ctrl+N para novo chat
        self.bind("<Control-n>", lambda e: self.new_chat())

        # Bind Ctrl+S para salvar chat
        self.bind("<Control-s>", lambda e: self.save_chat())

        # Bind Ctrl+O para abrir chat
        self.bind("<Control-o>", lambda e: self.load_chat())

        # Bind Ctrl+Q para sair
        self.bind("<Control-q>", lambda e: self.quit())

        # Bind Ctrl+F para focar no campo de mensagem
        self.bind("<Control-f>", lambda e: self.message_entry.focus())

        # Bind Ctrl+Up/Down para navegar no histórico
        self.bind("<Control-Up>", lambda e: self.navigate_history(-1))
        self.bind("<Control-Down>", lambda e: self.navigate_history(1))

        # Bind Ctrl+Backspace para limpar campo
        self.message_entry.bind("<Control-BackSpace>", lambda e: self.clear_input())

    def clear_input(self):
        """Limpa o campo de entrada"""
        self.message_entry.delete("1.0", "end")
        return "break"

    def navigate_history(self, direction):
        """Navega no histórico de mensagens"""
        if not hasattr(self, "message_history"):
            self.message_history = []
            self.history_index = -1

        if direction > 0 and self.history_index < len(self.message_history) - 1:
            self.history_index += 1
            self.message_entry.delete("1.0", "end")
            self.message_entry.insert("1.0", self.message_history[self.history_index])
        elif direction < 0 and self.history_index > 0:
            self.history_index -= 1
            self.message_entry.delete("1.0", "end")
            self.message_entry.insert("1.0", self.message_history[self.history_index])
        return "break"

    def clear_chat(self):
        """Limpa o chat"""
        self.messages_frame.clear()

    def new_chat(self):
        """Inicia um novo chat"""
        self.start_chat()

    def save_chat(self):
        """Salva o chat"""
        # Implemente a lógica para salvar o chat
        pass

    def load_chat(self):
        """Carrega um chat"""
        # Implemente a lógica para carregar um chat
        pass

    def quit(self):
        """Encerra a aplicação"""
        self.destroy()

    def _create_gradient(self, frame):
        """Cria efeito de gradiente no frame"""
        try:
            # Cria canvas para o gradiente
            canvas = tkinter.Canvas(
                frame,
                highlightthickness=0,
                bg=COLORS["primary"],
            )
            canvas.place(relwidth=1, relheight=1)
            canvas.lower()

            # Cria gradiente
            width = frame.winfo_width()
            height = frame.winfo_height()
            for i in range(height):
                # Calcula cor do gradiente
                r1, g1, b1 = frame.winfo_rgb(COLORS["primary"])
                r2, g2, b2 = frame.winfo_rgb(COLORS["primary_hover"])
                r = r1 + (r2 - r1) * i / height
                g = g1 + (g2 - g1) * i / height
                b = b1 + (b2 - b1) * i / height
                color = f'#{int(r/256):02x}{int(g/256):02x}{int(b/256):02x}'

                # Desenha linha do gradiente
                canvas.create_line(0, i, width, i, fill=color)

            # Atualiza gradiente quando a janela é redimensionada
            frame.bind('<Configure>', lambda e: self._update_gradient(canvas, frame))

        except Exception as e:
            logger.error(f"Erro ao criar gradiente: {str(e)}")

    def _update_gradient(self, canvas, frame):
        """Atualiza o gradiente quando a janela é redimensionada"""
        try:
            width = frame.winfo_width()
            height = frame.winfo_height()
            canvas.delete("all")
            for i in range(height):
                r1, g1, b1 = frame.winfo_rgb(COLORS["primary"])
                r2, g2, b2 = frame.winfo_rgb(COLORS["primary_hover"])
                r = r1 + (r2 - r1) * i / height
                g = g1 + (g2 - g1) * i / height
                b = b1 + (b2 - b1) * i / height
                color = f'#{int(r/256):02x}{int(g/256):02x}{int(b/256):02x}'
                canvas.create_line(0, i, width, i, fill=color)
        except Exception as e:
            logger.error(f"Erro ao atualizar gradiente: {str(e)}")
