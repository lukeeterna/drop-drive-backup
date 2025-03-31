# verify_drive_access.py

import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", None)

if not FOLDER_ID:
    raise ValueError("Variabile d'ambiente 'GDRIVE_FOLDER_ID' non impostata.")

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
drive = build('drive', 'v3', credentials=creds)

print("\n🔍 Verifica accesso cartella Drive con ID:", FOLDER_ID)

try:
    folder = drive.files().get(fileId=FOLDER_ID, fields="id, name, owners").execute()
    print("✅ Cartella trovata:", folder["name"])
    print("👤 Proprietario:", folder["owners"][0]["emailAddress"])
except Exception as e:
    print("❌ Errore: impossibile accedere alla cartella:", e)

print("\n📁 Cartelle visibili nella root del Drive:")
results = drive.files().list(
    q="'root' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
    pageSize=20,
    fields="files(id, name)"
).execute()
folders = results.get("files", [])
for f in folders:
    print(f" - {f['name']} ({f['id']})")

# Opzionale: crea nuova cartella se non trovata
CREATE_IF_MISSING = os.environ.get("CREATE_IF_MISSING", "false").lower() == "true"
if CREATE_IF_MISSING:
    print("\n🛠️ CREATING nuova cartella 'luke_backup_root' (se non esiste)...")
    new_folder_metadata = {
        'name': 'luke_backup_root',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.files().create(body=new_folder_metadata, fields="id").execute()
    print("✅ Nuova cartella creata con ID:", folder["id"])
