# verify_drive_access.py - Verifica accesso e cartella backup su Drive
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "")

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
service = build("drive", "v3", credentials=creds)

try:
    folder = service.files().get(fileId=FOLDER_ID, fields="name, owners").execute()
    print(f"✅ Cartella trovata: {folder['name']}")
    print(f"👤 Proprietario: {folder['owners'][0]['emailAddress']}")

    print("📁 Cartelle visibili nella root del Drive:")
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false",
        spaces="drive",
        fields="files(id, name)"
    ).execute()
    for file in results.get("files", []):
        print(f" - {file['name']} ({file['id']})")

except Exception as e:
    print(f"❌ Errore durante la verifica della cartella Drive: {e}")

