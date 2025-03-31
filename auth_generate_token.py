from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',  # Assicurati che sia nella stessa cartella
    scopes=SCOPES
)
creds = flow.run_local_server(port=0)

with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("✅ Nuovo token.json generato con accesso completo a Google Drive.")
