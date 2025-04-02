import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ✅ ENV VAR
TOKEN_PATH = os.environ.get("TOKEN_FILE", "token.json")
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "")

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
service = build("drive", "v3", credentials=creds)

# ✅ CREA CARTELLA (verifica parent_id)
def create_folder(folder_name, parent_id):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    folders = results.get("files", [])

    if folders:
        print(f"📁 Cartella '{folder_name}' trovata con ID: {folders[0]['id']}")
        return folders[0]["id"]

    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }

    folder = service.files().create(body=folder_metadata, fields="id").execute()
    print(f"✅ Cartella '{folder_name}' creata con ID: {folder['id']}")
    return folder["id"]

# ✅ UPLOAD FILE
def upload_file(file_path, folder_id):
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    print(f"📤 File '{file_path}' caricato con ID: {uploaded['id']}")

# ✅ ESECUZIONE
if __name__ == "__main__":
    print(f"🔍 Cartella ROOT di backup: {GDRIVE_FOLDER_ID}")
    folder_id = create_folder("saas", GDRIVE_FOLDER_ID)

    test_file_path = "output/TEST_backup.txt"
    if os.path.exists(test_file_path):
        upload_file(test_file_path, folder_id)
    else:
        print(f"❌ File di test non trovato: {test_file_path}")
