# verify_drive_access.py - Verifica accesso cartella su Drive e stampa struttura

import os
import json
from uploader_module import DriveUploader

TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
PARENT_DRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "")

uploader = DriveUploader(token_path=TOKEN_PATH)

if __name__ == "__main__":
    print(f"\U0001f50d Verifica accesso cartella Drive con ID: {PARENT_DRIVE_FOLDER_ID}")
    
    try:
        folder_info = uploader.service.files().get(fileId=PARENT_DRIVE_FOLDER_ID, fields="name, owners").execute()
        print(f"✅ Cartella trovata: {folder_info['name']}")
        print(f"\U0001f464 Proprietario: {folder_info['owners'][0]['emailAddress']}")

        print("\U0001f4c1 Cartelle visibili nella root del Drive:")
        results = uploader.service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents",
            spaces="drive",
            fields="files(id, name)"
        ).execute()

        for item in results.get("files", []):
            print(f" - {item['name']} ({item['id']})")

    except Exception as e:
        print(f"❌ Errore durante la verifica: {str(e)}")
