from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json', SCOPES)

# Questo funziona da terminale headless!
creds = flow.run_console()

with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("✅ TOKEN GENERATO E SALVATO con successo.")
