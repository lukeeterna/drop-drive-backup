# verify_drive_access.py - Verifica se la cartella su Drive è accessibile

import os
import json
from uploader_module import DriveUploader
from bootstrap_drive import DRIVE_LOG_FILE

uploader = DriveUploader()

def verify_drive_access():
    if not os.path.exists(DRIVE_LOG_FILE):
        print("❌ File di log non trovato. Esegui prima il bootstrap.")
        return

    with open(DRIVE_LOG_FILE) as f:
        log_data = json.load(f)

    if not log_data:
        print("⚠️ File di log vuoto. Nessuna cartella trovata.")
        return

    print("📝 Log Drive trovato. Contenuto:")
    print(json.dumps(log_data, indent=2))

    for folder_name, folder_id in log_data.items():
        print(f"🔍 Verifica accesso cartella Drive con ID: {folder_id}")
        try:
            metadata = uploader.service.files().get(fileId=folder_id, fields="name, owners").execute()
            print(f"✅ Cartella trovata: {metadata['name']}")
            print(f"👤 Proprietario: {metadata['owners'][0]['emailAddress']}")
        except Exception as e:
            print(f"❌ Errore nell'accesso alla cartella {folder_name} ({folder_id}): {e}")

if __name__ == "__main__":
    verify_drive_access()
