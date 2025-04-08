#!/bin/bash

# === CONFIG ===
PROJECT_NAME="chatgpt"
TIMESTAMP=$(date +%F-%H%M)
BACKUP_FILENAME="backup-${TIMESTAMP}.zip"
BACKUP_SOURCE="/root/drop-drive-backup/output"
BACKUP_DEST="/root/drop-drive-backup/${BACKUP_FILENAME}"
UPLOAD_SCRIPT="/root/drop-drive-backup/upload_file_to_folder.py"
LOG_FILE="/root/drop-drive-backup/cron.log"

# === CREA ARCHIVIO ===
cd /root/drop-drive-backup
zip -r "$BACKUP_FILENAME" output/ >> "$LOG_FILE" 2>&1

# === UPLOAD SU GOOGLE DRIVE ===
/usr/bin/python3 "$UPLOAD_SCRIPT" "$PROJECT_NAME" "$BACKUP_FILENAME" >> "$LOG_FILE" 2>&1

# === LOG ===
echo "[✔] Backup $BACKUP_FILENAME completato @ $TIMESTAMP" >> "$LOG_FILE"
