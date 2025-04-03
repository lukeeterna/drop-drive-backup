# upload_agent_files.py - Carica automaticamente tutti i file di un agente/progetto su Google Drive

import os
import hashlib
from uploader_module import DriveUploader

AGENT_NAME = "saas_architect_gpt"  # 🔁 Cambia per altri agenti
LOCAL_ROOT = f"./agents/{AGENT_NAME}"
DRIVE_ROOT_NAME = "luke_backup_root"

# 📁 Struttura standard da mantenere su Drive
SUBFOLDERS = ["input", "output", "log"]
FILES_TO_UPLOAD = [
    "main.py",
    "bootstrap_drive.py",
    "uploader_module.py",
    "render.yaml",
    "README.md"
]

PARENT_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")
TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
uploader = DriveUploader(token_path=TOKEN_PATH)

# 🔁 Step 1: Assicura root e agente folder
root_id = uploader._ensure_subfolder(DRIVE_ROOT_NAME, parent_id=PARENT_FOLDER_ID)
agente_id = uploader._ensure_subfolder(AGENT_NAME, parent_id=root_id)

# 🔁 Step 2: Crea sottocartelle standard
folder_ids = {}
for folder in SUBFOLDERS:
    folder_ids[folder] = uploader._ensure_subfolder(folder, parent_id=agente_id)

# 🔁 Step 3: Carica file nella root dell'agente
for file in FILES_TO_UPLOAD:
    path = os.path.join(LOCAL_ROOT, file)
    if os.path.exists(path):
        uploaded_id = uploader.upload_file(path, parent_id=agente_id, hash_check=True)
        print(f"✅ Caricato {file} → {uploaded_id}")
    else:
        print(f"⚠️ File mancante: {file}")

# ✅ Log finale
print("\n[✅ Upload completato per agente:", AGENT_NAME, "]")
