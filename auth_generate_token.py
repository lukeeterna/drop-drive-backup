from google_auth_oauthlib.flow import InstalledAppFlow

# Definisci lo scope per l'accesso a Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Inizializza il flow
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)

# Usa il terminale invece del browser per autenticarti
creds = flow.run_console()

# Salva il token
with open('token.json', 'w') as token_file:
    token_file.write(creds.to_json())

print("✅ Token generato e salvato correttamente in token.json.")
