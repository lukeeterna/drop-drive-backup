# gdrive_initializer.py
# 📁 Creazione directory e file su Drive solo se non esistono, o se aggiornati

import os
import json
import hashlib
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔐 Carica credenziali dal file token.json o variabili env
TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
service = build("drive", "v3", credentials=creds)

# 🔁 Util per hashing dei contenuti

def file_hash(filepath):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

# 🔧 Crea o ottiene ID di una cartella

def get_or_create_folder(name, parent_id):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    folders = results.get("files", [])
    if folders:
        return folders[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]

# ⬆️ Carica o aggiorna file

def upload_or_update(file_path, parent_id):
    file_name = os.path.basename(file_path)
    query = f"name='{file_name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, md5Checksum)").execute()
    existing_files = results.get("files", [])

    media = MediaFileUpload(file_path)
    local_hash = file_hash(file_path)

    if existing_files:
        remote_file = existing_files[0]
        if remote_file.get("md5Checksum") != local_hash:
            service.files().update(fileId=remote_file["id"], media_body=media).execute()
            print(f"🔁 Aggiornato: {file_name}")
        else:
            print(f"✅ Già aggiornato: {file_name}")
    else:
        service.files().create(body={"name": file_name, "parents": [parent_id]}, media_body=media).execute()
        print(f"🆕 Creato: {file_name}")

# 🧠 STRUTTURA BASE DA CREARE
AGENT_ROOT = "AGENTI"
AGENT_NAME = "saas_architect_gpt"
SUBFOLDERS = ["input", "output", "log"]
DUMMY_FILE = "init.txt"

# ✅ CREAZIONE STRUTTURA
agent_root_id = get_or_create_folder(AGENT_ROOT, GDRIVE_FOLDER_ID)
agente_folder_id = get_or_create_folder(AGENT_NAME, agent_root_id)

for folder in SUBFOLDERS:
    subfolder_id = get_or_create_folder(folder, agente_folder_id)

    # 📄 Crea dummy file
    local_dummy = f"./temp/{folder}_{DUMMY_FILE}"
    os.makedirs("./temp", exist_ok=True)
    with open(local_dummy, "w") as f:
        f.write(f"Questo è un file dummy in {folder}.")

    upload_or_update(local_dummy, subfolder_id)
