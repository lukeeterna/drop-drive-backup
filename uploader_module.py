# uploader_module.py - Modulo gestione upload su Google Drive

import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import hashlib


class DriveUploader:
    def __init__(self, token_path="./token.json"):
        self.token_path = token_path
        self.creds = Credentials.from_authorized_user_file(self.token_path)
        self.service = build("drive", "v3", credentials=self.creds)

    def upload_file(self, file_path, parent_id=None, subfolder_name=None, hash_check=False):
        if hash_check and self._file_already_uploaded(file_path, parent_id, subfolder_name):
            print(f"\u23e9 Nessun cambiamento per: {file_path}")
            return "skipped"

        file_metadata = {"name": os.path.basename(file_path)}

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

    def _file_already_uploaded(self, file_path, parent_id, subfolder_name=None):
        filename = os.path.basename(file_path)
        query = f"name='{filename}' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        response = self.service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name, md5Checksum)"
        ).execute()

        files = response.get("files", [])
        if not files:
            return False

        local_hash = self._compute_md5(file_path)
        for f in files:
            if f.get("md5Checksum") == local_hash:
                return True
        return False

    def _compute_md5(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
