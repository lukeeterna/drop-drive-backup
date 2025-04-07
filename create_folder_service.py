# ✅ CONFIGURAZIONE AUTOMATICA BACKUP CON SERVICE ACCOUNT GOOGLE DRIVE

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 📁 CONFIG
SERVICE_ACCOUNT_FILE = "service_account.json"
BACKUP_FOLDER_NAME = "n8n-test"
BACKUP_SOURCE_FOLDER = "/root/drop-drive-backup/output"
SCOPES = ['https://www.googleapis.com/auth/drive']

def init_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

def upload_files(service, folder_id, local_folder):
    for filename in os.listdir(local_folder):
        local_path = os.path.join(local_folder, filename)
        if os.path.isfile(local_path):
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            media = MediaFileUpload(local_path, resumable=True)
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"✅ Uploaded: {filename} → ID {uploaded_file['id']}")

if __name__ == "__main__":
    from googleapiclient.http import MediaFileUpload
    print("🔧 Avvio backup su Google Drive...")
    service = init_service()
    folder_id = get_or_create_folder(service, BACKUP_FOLDER_NAME)
    upload_files(service, folder_id, BACKUP_SOURCE_FOLDER)
    print("✅ Backup completato!")
