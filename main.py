from flask import Flask, request, redirect
import os
import pathlib
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime

app = Flask(__name__)

BASE_DIR = pathlib.Path(__file__).parent.resolve()

CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE", "client_secret.json")
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
BACKUP_SOURCE = os.getenv("BACKUP_SOURCE", "output")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


@app.route("/")
def home():
    return "✅ Flask attivo - Drop Drive Auth pronto"


@app.route("/auth/init")
def auth_init():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
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
    creds_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }

    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

    return "✅ Autenticazione completata. Puoi ora schedulare il backup."


def backup_to_drive():
    print("⏳ Avvio backup...")

    if not os.path.exists(TOKEN_FILE):
        print("❌ token.json mancante. Autentica prima su /auth/init.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("drive", "v3", credentials=creds)

    for filename in os.listdir(BACKUP_SOURCE):
        filepath = os.path.join(BACKUP_SOURCE, filename)

        if os.path.isfile(filepath):
            file_metadata = {
                "name": f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')} - {filename}",
                "parents": [GDRIVE_FOLDER_ID] if GDRIVE_FOLDER_ID else []
            }

            media = MediaFileUpload(filepath, resumable=True)
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

            print(f"✅ Backup caricato: {filename} (ID: {uploaded_file.get('id')})")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
