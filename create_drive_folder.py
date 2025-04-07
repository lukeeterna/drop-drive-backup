from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# Imposta il nome della cartella da creare
FOLDER_NAME = "n8n-test"
# Lascia None per creare nella root del Drive
PARENT_FOLDER_ID = None
# Percorso al file JSON del service account
SERVICE_ACCOUNT_FILE = "service_account.json"

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Carica le credenziali dal file JSON del service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Costruisce il servizio Google Drive
service = build("drive", "v3", credentials=credentials)

def create_or_get_folder(name, parent_id=None):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    items = results.get("files", [])

    if items:
        print(f"✅ Cartella già esistente con ID: {items[0]['id']}")
        return items[0]["id"]
    else:
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            file_metadata["parents"] = [parent_id]

        file = service.files().create(body=file_metadata, fields="id").execute()
        print(f"📁 Cartella '{name}' creata con ID: {file.get('id')}")
        return file.get("id")

# Esecuzione
print(f"\U0001F50D Avvio creazione cartella '{FOLDER_NAME}' in root: ")
folder_id = create_or_get_folder(FOLDER_NAME, PARENT_FOLDER_ID)
