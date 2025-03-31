from datetime import datetime

import customtkinter as ctk

# Configuração do CustomTkinter
ctk.set_appearance_mode("System")  # Modos: "System" (padrão), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (padrão), "green", "dark-blue"

# Lista de contatos de exemplo
CONTACTS = [
    {"name": "João", "status": "online"},
    {"name": "Maria", "status": "offline"},
    {"name": "Pedro", "status": "online"},
    {"name": "Ana", "status": "offline"},
    {"name": "Carlos", "status": "online"},
]


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configurações")
        self.geometry("400x300")
        self.resizable(False, False)

        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tema
        self.theme_label = ctk.CTkLabel(self.main_frame, text="Tema:")
        self.theme_label.pack(anchor="w", pady=(10, 5))

        self.theme_var = ctk.StringVar(value="System")
        self.theme_menu = ctk.CTkOptionMenu(
            self.main_frame,
            values=["System", "Dark", "Light"],
            variable=self.theme_var,
            command=self.change_theme,
        )
        self.theme_menu.pack(fill="x", pady=(0, 10))

        # Notificações
        self.notifications_var = ctk.BooleanVar(value=True)
        self.notifications_check = ctk.CTkCheckBox(
            self.main_frame, text="Ativar notificações", variable=self.notifications_var
        )
        self.notifications_check.pack(anchor="w", pady=10)

        # Som
        self.sound_var = ctk.BooleanVar(value=True)
        self.sound_check = ctk.CTkCheckBox(
            self.main_frame, text="Ativar som", variable=self.sound_var
        )
        self.sound_check.pack(anchor="w", pady=10)

        # Botão de salvar
        self.save_button = ctk.CTkButton(
            self.main_frame, text="Salvar", command=self.save_settings
        )
        self.save_button.pack(pady=20)

    def change_theme(self, theme):
        ctk.set_appearance_mode(theme)

    def save_settings(self):
        # TODO: Salvar configurações
        self.destroy()


class ChatApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("UCAN Chat")
        self.window.geometry("800x600")

        # Configurar grid
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Criar frames principais
        self.setup_sidebar()
        self.setup_main_area()

        # Centralizar janela
        self.center_window()

    def setup_sidebar(self):
        # Frame da barra lateral
        self.sidebar = ctk.CTkFrame(self.window, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Avatar e nome do usuário
        self.avatar_label = ctk.CTkLabel(self.sidebar, text="", width=80, height=80)
        self.avatar_label.grid(row=0, column=0, padx=10, pady=10)

        self.username_label = ctk.CTkLabel(self.sidebar, text="Usuário")
        self.username_label.grid(row=1, column=0, padx=10, pady=5)

        # Lista de contatos
        self.contacts_frame = ctk.CTkFrame(self.sidebar)
        self.contacts_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # Título da lista de contatos
        self.contacts_title = ctk.CTkLabel(self.contacts_frame, text="Contatos")
        self.contacts_title.pack(pady=5)

        # Lista de contatos
        self.contacts_list = ctk.CTkScrollableFrame(self.contacts_frame)
        self.contacts_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Adicionar contatos
        self.populate_contacts()

        # Botão de configurações
        self.settings_button = ctk.CTkButton(
            self.sidebar, text="Configurações", command=self.open_settings
        )
        self.settings_button.grid(row=3, column=0, padx=10, pady=10)

    def populate_contacts(self):
        for contact in CONTACTS:
            contact_frame = ctk.CTkFrame(self.contacts_list)
            contact_frame.pack(fill="x", padx=5, pady=2)

            # Status
            status_color = "green" if contact["status"] == "online" else "gray"
            status_label = ctk.CTkLabel(
                contact_frame, text="●", text_color=status_color, width=10
            )
            status_label.pack(side="left", padx=5)

            # Nome
            name_label = ctk.CTkLabel(contact_frame, text=contact["name"], anchor="w")
            name_label.pack(side="left", fill="x", expand=True, padx=5)

            # Botão de chat
            chat_button = ctk.CTkButton(
                contact_frame,
                text="Chat",
                width=60,
                command=lambda c=contact: self.start_chat(c),
            )
            chat_button.pack(side="right", padx=5)

    def start_chat(self, contact):
        # Limpar mensagens anteriores
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        # Atualizar título
        self.window.title(f"UCAN Chat - {contact['name']}")

        # Adicionar mensagem de boas-vindas
        self.add_message(f"Chat iniciado com {contact['name']}", is_user=False)

    def setup_main_area(self):
        # Frame principal
        self.main_area = ctk.CTkFrame(self.window)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Área de mensagens
        self.messages_frame = ctk.CTkScrollableFrame(self.main_area)
        self.messages_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Área de input
        self.input_frame = ctk.CTkFrame(self.main_area)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        self.message_input = ctk.CTkTextbox(self.input_frame, height=40)
        self.message_input.grid(row=0, column=0, sticky="ew", padx=5)

        self.send_button = ctk.CTkButton(
            self.input_frame, text="Enviar", width=100, command=self.send_message
        )
        self.send_button.grid(row=0, column=1, padx=5)

        # Configurar grid
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Bind Enter para enviar mensagem
        self.message_input.bind("<Return>", lambda e: self.send_message())

    def send_message(self):
        message = self.message_input.get("1.0", "end-1c").strip()
        if message:
            self.add_message(message, is_user=True)
            self.message_input.delete("1.0", "end")

            # Simular resposta do bot
            self.window.after(
                1000, lambda: self.add_message("Olá! Como posso ajudar?", is_user=False)
            )

    def add_message(self, text, is_user=True):
        # Frame da mensagem
        message_frame = ctk.CTkFrame(self.messages_frame)
        message_frame.grid(sticky="ew", padx=5, pady=5)

        # Avatar
        avatar_label = ctk.CTkLabel(
            message_frame, text="U" if is_user else "B", width=30, height=30
        )
        avatar_label.grid(row=0, column=0 if is_user else 2, padx=5)

        # Texto da mensagem
        message_label = ctk.CTkLabel(message_frame, text=text, wraplength=400)
        message_label.grid(row=0, column=1, padx=5)

        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        timestamp_label = ctk.CTkLabel(message_frame, text=timestamp, font=("", 10))
        timestamp_label.grid(row=1, column=1, padx=5)

    def open_settings(self):
        settings_window = SettingsWindow(self.window)
        settings_window.grab_set()  # Tornar janela modal

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def run(self):
        self.window.mainloop()


def main():
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
