from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/drive']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret_507763039316-kgao2efo9usupk3gi1a4ahs60h5qm0ck.apps.googleusercontent.com.json', SCOPES)

creds = flow.run_local_server(port=0)

with open('token.pickle', 'wb') as token:
    pickle.dump(creds, token)

service = build('drive', 'v3', credentials=creds)
results = service.files().list(pageSize=10).execute()
items = results.get('files', [])

if not items:
    print('Nessun file trovato.')
else:
    print('File trovati:')
    for item in items:
        print(f"{item['name']} ({item['id']})")
