from flask import Flask, request, redirect
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import os, json

load_dotenv()

app = Flask(__name__)

CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE", "client_secret.json")
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
BACKUP_SOURCE = os.getenv("BACKUP_SOURCE", "output")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

@app.route("/")
def index():
    return "✅ Flask attivo. Visita /auth/init per autenticarti."

@app.route("/auth/init")
def auth_init():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

@app.route("/auth/callback")
def auth_callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return "✅ Autenticazione completata. Puoi ora schedulare il backup."

def backup_to_drive():
    print("⏳ Avvio backup...")
    if not os.path.exists(TOKEN_FILE):
        print("❌ token.json mancante. Autentica prima su /auth/init.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('drive', 'v3', credentials=creds)

    if not os.path.isdir(BACKUP_SOURCE):
        print(f"❌ Cartella {BACKUP_SOURCE} non trovata.")
        return

    for filename in os.listdir(BACKUP_SOURCE):
        filepath = os.path.join(BACKUP_SOURCE, filename)
        if os.path.isfile(filepath):
            file_metadata = {
                'name': filename,
                'parents': [GDRIVE_FOLDER_ID] if GDRIVE_FOLDER_ID else []
            }
            media = MediaFileUpload(filepath, resumable=True)
            service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"✅ Backup completato: {filename}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
