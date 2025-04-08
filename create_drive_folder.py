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

def create
