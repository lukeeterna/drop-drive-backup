import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Variabili ambiente (se non già caricate)
TOKEN_PATH = os.environ.get("TOKEN_FILE", "token.json")
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC")

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
service = build("drive", "v3", credentials=creds)

# 1️⃣ Crea cartella "saas" dentro la root di backup
def create_folder(folder_name, parent_id):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    folders = results.get("files", [])

    if folders:
        return folders[0]["id"]

    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    print(f"✅ Cartella '{folder_name}' creata con ID: {folder['id']}")
    return folder["id"]

# 2️⃣ Carica un file test nella cartella
def upload_file(file_path, folder_id):
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path)
    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ File caricato su Drive con ID: {uploaded['id']}")

# Esecuzione
if __name__ == "__main__":
    saas_folder_id = create_folder("saas", GDRIVE_FOLDER_ID)

    # ✅ Crea file se non esiste
    test_file_path = "test_saas_file.txt"
    with open(test_file_path, "w") as f:
        f.write("📄 Questo è un test di upload nella cartella saas.")

    upload_file(test_file_path, saas_folder_id)
