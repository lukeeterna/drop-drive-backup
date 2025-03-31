# LUKEBACKUP_GPT - Backup GPT Agent con upload su Google Drive (con sottocartelle GPT)

import os
import shutil
import datetime
import json
from drive_uploader import DriveUploader

# Config globale
GPT_LIST = [
    "backup_automatico",
    "output_test"
]

SOURCE_PATHS = {
    "backup_automatico": ["./output/drop-drive-backup.zip"],
    "output_test": [
        "./output/TEST_backup.txt",
        "./output/backup_finale_pro_chatgpt.txt"
    ]
}

BACKUP_ROOT = "./DRIVE_BACKUP_SIMULATION"
LOG_FILE = os.path.join(BACKUP_ROOT, "backup_log.json")
PARENT_DRIVE_FOLDER_ID = "16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC"

uploader = DriveUploader()

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
                    drive_id = uploader.upload_file(dest_path, PARENT_DRIVE_FOLDER_ID, subfolder_name=gpt)
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
