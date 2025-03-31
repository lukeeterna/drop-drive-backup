# LUKEBACKUP_GPT - Backup GPT Agent con upload su Google Drive (con sottocartelle GPT)

import os
import shutil
import datetime
import json
from uploader_module import DriveUploader  # 🔁 Fix circular import

# Config globale
GPT_LIST = [
    "backup_automatico",
    "output_test"
]

BACKUP_SOURCE = os.environ.get("BACKUP_SOURCE", "./output")
TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")

SOURCE_PATHS = {
    "backup_automatico": [f"{BACKUP_SOURCE}/drop-drive-backup.zip"],
    "output_test": [
        f"{BACKUP_SOURCE}/TEST_backup.txt",
        f"{BACKUP_SOURCE}/backup_finale_pro_chatgpt.txt"
    ]
}

BACKUP_ROOT = "./DRIVE_BACKUP_SIMULATION"
LOG_FILE = os.path.join(BACKUP_ROOT, "backup_log.json")
PARENT_DRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC")

# ✅ PATCH: Creo una sola root GPT se non esiste
uploader = DriveUploader(token_path=TOKEN_PATH)

if __name__ == "__main__":
    result = {
        "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "files_backed_up": [],
        "status": "success"
    }

    for gpt in GPT_LIST:
        target_folder = os.path.join(BACKUP_ROOT, gpt)
        os.makedirs(target_folder, exist_ok=True)

        for file_path in SOURCE_PATHS.get(gpt, []):
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                timestamped_name = f"{result['timestamp']}_{filename}"
                dest_path = os.path.join(target_folder, timestamped_name)
                shutil.copy2(file_path, dest_path)
                try:
                    drive_id = uploader.upload_file(
                        dest_path,
                        parent_id=PARENT_DRIVE_FOLDER_ID,
                        subfolder_name=gpt
                    )
                    result["files_backed_up"].append({"local": dest_path, "drive_id": drive_id})
                except Exception as upload_error:
                    result["files_backed_up"].append({"local": dest_path, "drive_upload": "failed", "error": str(upload_error)})
                    result["status"] = "partial_success"
            else:
                print(f"❌ File non trovato: {file_path}")
                result["status"] = "partial_success"

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(result) + "\n")

    print("[✅ BACKUP COMPLETATO + UPLOAD ORGANIZZATO SU DRIVE]")
    print(json.dumps(result, indent=2))
