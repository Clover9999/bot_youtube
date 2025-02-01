import os
import googleapiclient.discovery
import googleapiclient.errors
import google_auth_oauthlib.flow
from googleapiclient.http import MediaFileUpload

def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video(file_path):
    youtube = get_authenticated_service()
    
    video_title = os.path.splitext(os.path.basename(file_path))[0]  # Remove a extensão .mp4
    request_body = {
        "snippet": {
            "title": video_title,
            "description": "Vídeo enviado automaticamente.",
            "tags": ["Shorts", "Automação", "Python"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )
    response = request.execute()
    print(f'Vídeo {video_title} enviado com sucesso! ID: {response["id"]}')

if __name__ == "__main__":
    video_files = ["kkk mt bom.mp4", "video2.mp4", "video3.mp4"]  # Substitua pelos vídeos que deseja enviar
    for video in video_files:
        if os.path.exists(video):
            upload_video(video)
        else:
            print(f"Arquivo {video} não encontrado.")
