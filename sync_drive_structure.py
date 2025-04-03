# sync_drive_structure.py - Assicura che la struttura agenti/progetti sia corretta
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
ROOT_FOLDER_NAME = "luke_backup_root"
AGENT_STRUCTURE = ["input", "output", "log"]

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
service = build("drive", "v3", credentials=creds)

def get_or_create_folder(name, parent_id=None):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    items = results.get("files", [])

    if items:
        return items[0]["id"]

    folder_metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        folder_metadata["parents"] = [parent_id]

    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder.get("id")

def ensure_agent_structure(agent_name):
    root_id = get_or_create_folder(ROOT_FOLDER_NAME)
    agent_id = get_or_create_folder(agent_name, parent_id=root_id)
    structure = {}
    for subfolder in AGENT_STRUCTURE:
        sub_id = get_or_create_folder(subfolder, parent_id=agent_id)
        structure[subfolder] = sub_id

    return {"agent_name": agent_name, "drive_id": agent_id, "structure": structure}

if __name__ == "__main__":
    agent_name = os.environ.get("AGENT_NAME", "saas_architect_gpt")
    result = ensure_agent_structure(agent_name)

    print("[✅ Directory struttura sincronizzata su Drive]")
    print(json.dumps(result, indent=2))
