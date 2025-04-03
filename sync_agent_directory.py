# sync_agent_directory.py

import os
import hashlib
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Config da variabili ambiente
TOKEN_FILE = os.environ.get("TOKEN_FILE", "token.json")
ROOT_AGENT_DIR = "AGENTI"
DRIVE_PARENT_ID = os.environ.get("GDRIVE_FOLDER_ID")  # es: ID della cartella BACKUP_AUTOMATICO

creds = Credentials.from_authorized_user_file(TOKEN_FILE)
drive_service = build("drive", "v3", credentials=creds)

def compute_md5(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def ensure_drive_folder(name, parent_id=None):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = drive_service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    folders = results.get("files", [])

    if folders:
        return folders[0]["id"]

    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = drive_service.files().create(body=metadata, fields="id").execute()
    return folder["id"]

def upload_file_if_needed(local_path, parent_drive_id):
    filename = os.path.basename(local_path)
    query = f"name='{filename}' and '{parent_drive_id}' in parents and trashed=false"
    files = drive_service.files().list(q=query, fields="files(id, md5Checksum)").execute().get("files", [])

    local_md5 = compute_md5(local_path)
    for file in files:
        if file.get("md5Checksum") == local_md5:
            print(f"✅ Nessun cambiamento per {filename}, skip upload")
            return

    media = MediaFileUpload(local_path)
    metadata = {"name": filename, "parents": [parent_drive_id]}
    uploaded = drive_service.files().create(body=metadata, media_body=media, fields="id").execute()
    print(f"⬆️ Uploadato {filename} → Drive ID: {uploaded['id']}")

def sync_local_dir_to_drive():
    agent_root_drive_id = ensure_drive_folder("AGENTI", DRIVE_PARENT_ID)

    for agent_name in os.listdir(ROOT_AGENT_DIR):
        agent_path = os.path.join(ROOT_AGENT_DIR, agent_name)
        if not os.path.isdir(agent_path):
            continue

        print(f"\n🔍 Sync agente: {agent_name}")
        agent_drive_id = ensure_drive_folder(agent_name, agent_root_drive_id)

        for subfolder in ["input", "output", "log"]:
            local_sub_path = os.path.join(agent_path, subfolder)
            if not os.path.exists(local_sub_path):
                continue

            drive_sub_id = ensure_drive_folder(subfolder, agent_drive_id)

            for file_name in os.listdir(local_sub_path):
                file_path = os.path.join(local_sub_path, file_name)
                if os.path.isfile(file_path):
                    upload_file_if_needed(file_path, drive_sub_id)

if __name__ == "__main__":
    sync_local_dir_to_drive()
