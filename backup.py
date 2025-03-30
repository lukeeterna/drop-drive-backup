from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import os

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
BACKUP_SOURCE = os.getenv("BACKUP_SOURCE", "output")

def backup_to_drive():
    print("⏳ Avvio backup...")

    if not os.path.exists(TOKEN_FILE):
        print("❌ token.json mancante. Autentica prima su /auth/init.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("drive", "v3", credentials=creds)

    if not os.path.isdir(BACKUP_SOURCE):
        print(f"❌ Cartella {BACKUP_SOURCE} non trovata.")
        return

    for filename in os.listdir(BACKUP_SOURCE):
        filepath = os.path.join(BACKUP_SOURCE, filename)
        if os.path.isfile(filepath):
            file_metadata = {
                "name": filename,
                "parents": [GDRIVE_FOLDER_ID] if GDRIVE_FOLDER_ID else [],
            }
            media = MediaFileUpload(filepath, resumable=True)
            service.files().create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()
            print(f"✅ Backup completato: {filename}")

if __name__ == "__main__":
    backup_to_drive()
