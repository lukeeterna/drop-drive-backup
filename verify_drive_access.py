# verify_drive_access.py - Verifica l'accesso alla cartella Google Drive per backup

import os
from uploader_module import DriveUploader

PARENT_DRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC")
TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")

if __name__ == "__main__":
    uploader = DriveUploader(token_path=TOKEN_PATH)
    try:
        folder_name = uploader.get_folder_name(PARENT_DRIVE_FOLDER_ID)
        print(f"\U0001f50d Cartella trovata: {folder_name} (ID: {PARENT_DRIVE_FOLDER_ID})")
        print("\n\U0001f4c1 Cartelle visibili nella root del Drive:")
        root_folders = uploader.list_folders("root")
        for folder in root_folders:
            print(f" - {folder['name']} ({folder['id']})")
    except Exception as e:
        print(f"❌ Errore durante la verifica dell'accesso a Drive: {e}")
