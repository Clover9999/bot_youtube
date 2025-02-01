import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import sys

# Definindo o caminho dos arquivos dependendo de ser executável ou não
if getattr(sys, 'frozen', False):
    # Caso esteja em um executável
    client_secret_path = os.path.join(sys._MEIPASS, 'client_secrets.json')
    token_file_path = os.path.join(sys._MEIPASS, 'token.json')
else:
    # Caso esteja rodando no ambiente de desenvolvimento
    client_secret_path = 'client_secrets.json'
    token_file_path = 'token.json'

# Verifique se o arquivo 'client_secrets.json' existe
if not os.path.exists(client_secret_path):
    messagebox.showerror("Erro", "Arquivo 'client_secrets.json' não encontrado!")
    sys.exit()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Criar janela principal
ctk.set_appearance_mode("dark")  # Modo escuro
ctk.set_default_color_theme("blue")  # Tema azul
root = ctk.CTk()
root.title("Bot de Upload para YouTube")
root.geometry("500x400")

# Criar Frame principal
frame = ctk.CTkFrame(root)
frame.pack(pady=10, padx=10, fill="both", expand=True)

# Lista de arquivos
file_listbox = ctk.CTkTextbox(frame, height=150, wrap="none")
file_listbox.pack(pady=10, padx=10, fill="both", expand=True)

def get_authenticated_service():
    creds = None
    if os.path.exists(token_file_path):
        creds = Credentials.from_authorized_user_file(token_file_path, SCOPES)
    
    if not creds or not creds.valid:
        try:
            # Usando run_local_server() para autenticação via navegador
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)  # Usando run_local_server() para gerar o link de autenticação

            with open(token_file_path, "w") as token:
                token.write(creds.to_json())

        except Exception as e:
            # Captura a exceção e exibe mais detalhes
            print(f"Erro ao autenticar: {e}")
            messagebox.showerror("Erro de autenticação", f"Ocorreu um erro ao autenticar o usuário: {e}")
            return None

    return build("youtube", "v3", credentials=creds)

def integrate_auth():
    """Refaz manualmente a autenticação do usuário"""
    try:
        os.remove(token_file_path)  # Deleta o token para forçar nova autenticação
    except FileNotFoundError:
        pass
    messagebox.showinfo("Integração", "Faça login na sua conta do Google para integrar novamente.")
    get_authenticated_service()
    messagebox.showinfo("Sucesso", "Integração concluída com sucesso!")

def upload_video(video_path):
    youtube = get_authenticated_service()
    request_body = {
        "snippet": {
            "title": os.path.splitext(os.path.basename(video_path))[0],  # Remove a extensão .mp4
            "description": "Vídeo enviado via bot",
            "tags": ["bot", "upload", "YouTube"],
            "categoryId": "22"
        },
        "status": {"privacyStatus": "public"}
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    request.execute()

    # Atualiza a lista de arquivos enviados
    file_listbox.insert("end", f"✔ Enviado: {os.path.basename(video_path)}\n")
    file_listbox.yview("end")  # Rolagem automática para o final

    messagebox.showinfo("Sucesso", f"Vídeo '{video_path}' enviado com sucesso!")

def select_video():
    file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if file_path:
        file_listbox.insert("end", f"⏳ Enviando: {os.path.basename(file_path)}...\n")
        file_listbox.yview("end")
        root.update_idletasks()  # Atualiza a interface durante o upload
        upload_video(file_path)

# Criar botões
upload_button = ctk.CTkButton(frame, text="Selecionar Vídeo", command=select_video)
upload_button.pack(pady=5, padx=10, fill="x")

integrate_button = ctk.CTkButton(frame, text="Integrar", command=integrate_auth, fg_color="orange")
integrate_button.pack(pady=5, padx=10, fill="x")

# Iniciar o loop da interface
root.mainloop()
