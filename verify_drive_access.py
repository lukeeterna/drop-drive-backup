# render.yaml - Configurazione servizio Render per backup
services:
  - type: worker
    name: drop-drive-backup
    env: python
    region: frankfurt
    plan: starter
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    envVars:
      - key: BACKUP_SOURCE
        value: output
      - key: GDRIVE_FOLDER_ID
        value: 16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC
      - key: TOKEN_FILE
        value: token.json
