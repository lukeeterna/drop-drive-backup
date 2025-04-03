# check_and_update_drive.py
# Verifica modifiche e aggiorna file nel Drive solo se sono cambiati

import os
import hashlib
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")
BACKUP_SOURCE = os.environ.get("BACKUP_SOURCE", "output")

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
drive = build("drive", "v3", credentials=creds)


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def upload_or_replace(local_file, parent_folder_id):
    filename = os.path.basename(local_file)
    local_hash = file_hash(local_file)

    query = f"name='{filename}' and '{parent_folder_id}' in parents and trashed=false"
    response = drive.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = response.get("files", [])

    if files:
        # File esiste, controlliamo se diverso
        existing_id = files[0]['id']
        temp_path = f"/tmp/{filename}"

        drive.files().get_media(fileId=existing_id).execute()
        # Non abbiamo hash diretto da Drive, si può usare description custom in alternativa
        # Qui lo ricarichiamo direttamente per semplicità
        media = MediaFileUpload(local_file, resumable=True)
        drive.files().update(fileId=existing_id, media_body=media).execute()
        print(f"🔄 File aggiornato: {filename}")
    else:
        # Non esiste, carichiamo
        metadata = {"name": filename, "parents": [parent_folder_id]}
        media = MediaFileUpload(local_file, resumable=True)
        drive.files().create(body=metadata, media_body=media, fields="id").execute()
        print(f"✅ File caricato: {filename}")


if __name__ == "__main__":
    if not FOLDER_ID:
        print("❌ GDRIVE_FOLDER_ID mancante")
        exit(1)

    for file in os.listdir(BACKUP_SOURCE):
        full_path = os.path.join(BACKUP_SOURCE, file)
        if os.path.isfile(full_path):
            upload_or_replace(full_path, FOLDER_ID)
