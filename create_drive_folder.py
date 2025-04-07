# create_drive_folder.py - Script universale per creare cartelle su Google Drive

import os
import sys
from google.oauth2 import service_account


TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
PARENT_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "")
FOLDER_NAME = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DRIVE_SUBFOLDER", "default_folder")
FILES_TO_UPLOAD = sys.argv[2:]  # opzionale

creds = service_account.Credentials.from_service_account_file(
    'service_account.json', scopes=SCOPES
)

service = build("drive", "v3", credentials=creds)

def create_or_get_folder(name, parent_id):
    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and name='{name}' and '{parent_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    folders = results.get("files", [])
    if folders:
        print(f"📁 Cartella già esistente: {name} → ID: {folders[0]['id']}")
        return folders[0]['id']

    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    print(f"✅ Cartella creata: {name} → ID: {folder['id']}")
    return folder['id']

def upload_files(folder_id, file_paths):
    for path in file_paths:
        if os.path.exists(path):
            file_metadata = {"name": os.path.basename(path), "parents": [folder_id]}
            media = MediaFileUpload(path)
            uploaded = service.files().create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()
            print(f"📄 File caricato: {path} → ID: {uploaded['id']}")
        else:
            print(f"⚠️ File non trovato: {path}")

if __name__ == "__main__":
    print(f"🔍 Avvio creazione cartella '{FOLDER_NAME}' in root: {PARENT_FOLDER_ID}")
    folder_id = create_or_get_folder(FOLDER_NAME, PARENT_FOLDER_ID)
    if FILES_TO_UPLOAD:
        upload_files(folder_id, FILES_TO_UPLOAD)
