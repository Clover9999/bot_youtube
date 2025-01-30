import os
import time
import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Configurações da API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secrets.json"
TOKEN_FILE = "token.pickle"  # Usando pickle ao invés de JSON

# Obtém autenticação OAuth 2.0
def get_authenticated_service():
    creds = None

    # Verifica se o token existe para evitar login repetitivo
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "rb") as token_file:
                creds = pickle.load(token_file)
        except (pickle.PickleError, EOFError):
            print("⚠️ Arquivo token.pickle corrompido. Deletando e gerando um novo...")
            os.remove(TOKEN_FILE)  # Exclui o arquivo corrompido

    # Se não tiver credenciais ou o arquivo estiver corrompido, pede novo login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Tenta atualizar as credenciais expiradas
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Salva o token com pickle para reutilização
        with open(TOKEN_FILE, "wb") as token_file:
            pickle.dump(creds, token_file)

    return build("youtube", "v3", credentials=creds)

# Upload de vídeo
def upload_video(video_path, title, description, tags):
    youtube = get_authenticated_service()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {"privacyStatus": "public"},
    }

    try:
        with open(video_path, "rb") as video_file:
            request = youtube.videos().insert(
                part="snippet,status",
                body=request_body,
                media_body=video_path
            )
            response = request.execute()

            if isinstance(response, dict) and "id" in response:
                print(f"✅ Vídeo enviado com sucesso! ID: {response['id']}")
            else:
                print("⚠️ Resposta inesperada da API:", response)
    except HttpError as e:
        print(f"❌ Erro ao enviar o vídeo: {e}")

# Upload em massa
def upload_multiple_videos(video_folder):
    for file in os.listdir(video_folder):
        if file.endswith(".mp4"):
            video_path = os.path.join(video_folder, file)
            title = f"Meu Short: {file}"
            description = "Este é um vídeo curto enviado automaticamente."
            tags = ["shorts", "automação", "YouTubeBot"]

            print(f"📤 Enviando: {video_path}")
            upload_video(video_path, title, description, tags)
            time.sleep(10)  # Pausa para evitar limite de API

# 🚀 Executa o bot
if __name__ == "__main__":
    video_folder = "meus_shorts"  # Pasta com os vídeos
    upload_multiple_videos(video_folder)
