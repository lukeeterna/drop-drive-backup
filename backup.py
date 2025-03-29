import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
BACKUP_FOLDER = os.getenv("BACKUP_SOURCE", "output/")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")

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
    backup_to_drive()
