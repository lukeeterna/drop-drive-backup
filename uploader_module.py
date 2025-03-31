import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_PATH = "./token.json"

class DriveUploader:
    def __init__(self, token_path=TOKEN_PATH):
        self.token_path = token_path
        self.creds = Credentials.from_authorized_user_file(self.token_path)
        self.service = build('drive', 'v3', credentials=self.creds)

    def get_or_create_folder(self, folder_name, parent_id):
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)', supportsAllDrives=True).execute()
        items = results.get('files', [])
        if items:
            return items[0]['id']

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = self.service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
        return folder.get('id')

    def upload_file(self, file_path, drive_folder_id, subfolder_name=None):
        folder_id = drive_folder_id
        if subfolder_name:
            folder_id = self.get_or_create_folder(subfolder_name, drive_folder_id)

        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
