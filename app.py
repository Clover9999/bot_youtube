import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secrets.json"

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
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def integrate_auth():
    """Refaz manualmente a autenticação do usuário"""
    try:
        os.remove(TOKEN_FILE)  # Deleta o token para forçar nova autenticação
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
