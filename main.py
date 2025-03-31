# LUKEBACKUP_GPT - Backup GPT Agent con upload su Google Drive (con debug e sottocartelle corrette)
# Esegue il backup di file locali e li carica nella sottocartella corrispondente in Drive

import os
import shutil
import datetime
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# Config globale
GPT_LIST = ["backup_automatico"]  # Backup test GPT
SOURCE_PATHS = {
    "backup_automatico": ["./drop-drive-backup.zip"]
}
BACKUP_ROOT = "./DRIVE_BACKUP_SIMULATION"
LOG_FILE = os.path.join(BACKUP_ROOT, "backup_log.json")
PARENT_DRIVE_FOLDER_ID = "16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC"
TOKEN_PATH = "./token.json"

def get_or_create_folder(service, folder_name, parent_id):
    print(f"🔎 CERCO cartella '{folder_name}' dentro parent ID: {parent_id}")
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)', supportsAllDrives=True).execute()
    items = results.get('files', [])
    if items:
        print(f"📁 Cartella trovata: {items[0]['name']} (ID: {items[0]['id']})")
        return items[0]['id']
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
    print(f"📂 Cartella creata: {folder_name} → ID: {folder['id']}")
    return folder.get('id')

def upload_to_drive(filepath, parent_folder_id, gpt_folder_name):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('drive', 'v3', credentials=creds)
    subfolder_id = get_or_create_folder(service, gpt_folder_name, parent_folder_id)
    filename = os.path.basename(filepath)
    file_metadata = {
        'name': filename,
        'parents': [subfolder_id]
    }
    media = MediaFileUpload(filepath, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"📤 File caricato su Drive: {filename} → ID: {file['id']}")
    return file.get('id')

def create_backup():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log = {"timestamp": timestamp, "files_backed_up": [], "status": "success"}

    for gpt in GPT_LIST:
        target_folder = os.path.join(BACKUP_ROOT, gpt)
        os.makedirs(target_folder, exist_ok=True)

        for file_path in SOURCE_PATHS.get(gpt, []):
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                dest_path = os.path.join(target_folder, f"{timestamp}_{filename}")
                shutil.copy2(file_path, dest_path)
                try:
                    drive_id = upload_to_drive(dest_path, PARENT_DRIVE_FOLDER_ID, gpt)
                    log["files_backed_up"].append({"local": dest_path, "drive_id": drive_id})
                except Exception as upload_error:
                    log["files_backed_up"].append({"local": dest_path, "drive_upload": "failed", "error": str(upload_error)})
                    log["status"] = "partial_success"
            else:
                print(f"❌ File non trovato: {file_path}")
                log["status"] = "partial_success"

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

    return log

if __name__ == "__main__":
    result = create_backup()
    print("[✅ BACKUP COMPLETATO + UPLOAD ORGANIZZATO SU DRIVE]")
    print(json.dumps(result, indent=2))
