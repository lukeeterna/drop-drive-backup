# Drop Drive Backup

Servizio Flask indipendente per il backup automatico su Google Drive.

## Funzionalità
- Autenticazione OAuth con Google
- Upload automatico da /output/ su Drive
- Deploy su Render con cron job ogni 3 ore

## Endpoint
- `/auth/init` — Avvia autenticazione
- `/auth/callback` — Completa autenticazione

## Backup manuale
```bash
curl -X POST https://drop-drive-backup.onrender.com/backup
```
