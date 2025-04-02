# uploader_module.py - Modulo di upload su Google Drive con controllo hash

import os
import json
import hashlib
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class DriveUploader:
    def __init__(self, token_path="./token.json"):
        self.token_path = token_path
        self.creds = Credentials.from_authorized_user_file(self.token_path)
        self.service = build("drive", "v3", credentials=self.creds)

    def upload_file(self, file_path, parent_id=None, subfolder_name=None, hash_check=False):
        file_metadata = {"name": os.path.basename(file_path)}

        if subfolder_name:
            subfolder_id = self._ensure_subfolder(subfolder_name, parent_id)
            file_metadata["parents"] = [subfolder_id]
        elif parent_id:
            file_metadata["parents"] = [parent_id]

        # Calcolo hash locale del file da caricare
        local_hash = self._compute_sha256(file_path)

        if hash_check:
            existing_files = self._list_files_in_folder(file_metadata["parents"][0], file_metadata["name"])
            for f in existing_files:
                if "md5Checksum" in f and f["md5Checksum"] == local_hash:
                    print(f"⚠️ Skip upload: file già presente con stesso hash → {file_metadata['name']}")
                    return f["id"]

        media = MediaFileUpload(file_path, resumable=True)
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

    def _list_files_in_folder(self, folder_id, filename):
        query = f"'{folder_id}' in parents and name = '{filename}' and trashed = false"
        results = self.service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name, md5Checksum)"
        ).execute()
        return results.get("files", [])

    def _compute_sha256(self, filename):
        h = hashlib.sha256()
        with open(filename, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
