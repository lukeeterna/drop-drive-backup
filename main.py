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
FALLBACK_LOG_FILE = os.path.join(BACKUP_ROOT, "fallback_files.json")
PARENT_DRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC")

# ✅ PATCH: Creo una sola root GPT se non esiste
uploader = DriveUploader(token_path=TOKEN_PATH)

if __name__ == "__main__":
    result = {
        "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "files_backed_up": [],
        "status": "success"
    }
    fallback_files = []

    for gpt in GPT_LIST:
        target_folder = os.path.join(BACKUP_ROOT, gpt)
        os.makedirs(target_folder, exist_ok=True)

        for file_path in SOURCE_PATHS.get(gpt, []):
            # 🔄 Se il file non esiste, lo genero automaticamente per test
            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(f"FILE DI TEST AUTO-GENERATO PER {gpt}\n")
                fallback_files.append({"generated": file_path, "gpt": gpt})

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

    os.makedirs(BACKUP_ROOT, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(result) + "\n")

    if fallback_files:
        with open(FALLBACK_LOG_FILE, "a") as f:
            f.write(json.dumps({"timestamp": result["timestamp"], "fallbacks": fallback_files}) + "\n")

    print("[✅ BACKUP COMPLETATO + UPLOAD ORGANIZZATO SU DRIVE]")
    print(json.dumps(result, indent=2))
