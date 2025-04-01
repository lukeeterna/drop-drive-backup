import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload  # ✅ FIX IMPORT


class DriveUploader:
    def __init__(self, token_path="./token.json"):
        self.token_path = token_path
        self.creds = Credentials.from_authorized_user_file(self.token_path)
        self.service = build("drive", "v3", credentials=self.creds)

    def upload_file(self, file_path, parent_id=None, subfolder_name=None):
        file_metadata = {"name": os.path.basename(file_path)}

        # ⬇️ Se c'è una subfolder, la creo se non esiste
        if subfolder_name:
            subfolder_id = self._ensure_subfolder(subfolder_name, parent_id)
            file_metadata["parents"] = [subfolder_id]
        elif parent_id:
            file_metadata["parents"] = [parent_id]

        media = MediaFileUpload(file_path)
        uploaded = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
        return uploaded.get("id")

    def _ensure_subfolder(self, name, parent_id=None):
        query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name)"
        ).execute()
        items = results.get("files", [])

        if items:
            return items[0]["id"]

        folder_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            folder_metadata["parents"] = [parent_id]

        folder = self.service.files().create(
            body=folder_metadata,
            fields="id"
        ).execute()
        return folder.get("id")
