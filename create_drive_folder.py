from google.oauth2 import service_account
from googleapiclient.discovery import build
import sys

# === CONFIGURAZIONE ===
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = '16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC'  # CARTELLA PRINCIPALE

# === INPUT DA TERMINALE ===
if len(sys.argv) != 2:
    print("❌ Uso: python3 create_drive_folder.py <nome_cartella>")
    sys.exit(1)
FOLDER_NAME = sys.argv[1]

# === AUTENTICAZIONE ===
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('drive', 'v3', credentials=creds)

def create_or_get_folder(name, parent_id):
    print(f"🔍 Avvio creazione cartella '{name}' in '{parent_id}'")
    query = (
        f"mimeType='application/vnd.google-apps.folder' and "
        f"name='{name}' and '{parent_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    folders = results.get('files', [])

    if folders:
        print(f"✅ Cartella '{name}' trovata. ID: {folders[0]['id']}")
        return folders[0]['id']

    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    print(f"✅ Cartella '{name}' creata. ID: {folder.get('id')}")
    return folder.get('id')

# === ESECUZIONE ===
folder_id = create_or_get_folder(FOLDER_NAME, PARENT_FOLDER_ID)
