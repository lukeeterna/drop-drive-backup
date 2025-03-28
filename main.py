import os
import json
from flask import Flask, request, redirect
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Permette l'autenticazione OAuth su HTTP (ambiente locale/test)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()
app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE", "client_secret.json")
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
BACKUP_FOLDER = os.getenv("BACKUP_SOURCE", "output/")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")

@app.route("/auth/init")
def auth_init():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=os.getenv("REDIRECT_URI")
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

@app.route("/auth/callback")
def auth_callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=os.getenv("REDIRECT_URI")
    )
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

    return "✅ Autenticazione completata. Puoi ora schedulare il backup."

def backup_to_drive():
    if not os.path.exists(TOKEN_FILE):
        print("❌ token.json mancante. Autentica prima su /auth/init.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('drive', 'v3', credentials=creds)

    uploaded = []
    for filename in os.listdir(BACKUP_FOLDER):
        file_path = os.path.join(BACKUP_FOLDER, filename)
        if not os.path.isfile(file_path):
            continue
        file_metadata = {'name': filename}
        if GDRIVE_FOLDER_ID:
            file_metadata['parents'] = [GDRIVE_FOLDER_ID]
        media = MediaFileUpload(file_path)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        uploaded.append(filename)
        print(f"✅ Backup caricato: {filename}")

    if not uploaded:
        print("ℹ️ Nessun file da caricare.")

if __name__ == "__main__":
    app.run(port=8000)
