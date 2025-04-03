# sync_agent_directory.py - Sincronizza struttura AGENTI su Google Drive

import os
from uploader_module import DriveUploader

AGENTS_ROOT = "./agents"
DRIVE_ROOT_NAME = "luke_backup_root"
TOKEN_PATH = os.environ.get("TOKEN_FILE", "./token.json")
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")

uploader = DriveUploader(token_path=TOKEN_PATH)

def sync_all_agents():
    if not GDRIVE_FOLDER_ID:
        raise ValueError("❌ GDRIVE_FOLDER_ID mancante nelle variabili d'ambiente")

    for agent_name in os.listdir(AGENTS_ROOT):
        agent_path = os.path.join(AGENTS_ROOT, agent_name)
        if not os.path.isdir(agent_path):
            continue

        print(f"\n🚀 Sincronizzazione agente: {agent_name}")
        for subfolder in ["input", "output", "log"]:
            local_dir = os.path.join(agent_path, subfolder)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            for filename in os.listdir(local_dir):
                local_path = os.path.join(local_dir, filename)
                if os.path.isfile(local_path):
                    try:
                        drive_id = uploader.upload_file(
                            local_path,
                            parent_id=GDRIVE_FOLDER_ID,
                            subfolder_name=f"{agent_name}/{subfolder}",
                            hash_check=True
                        )
                        print(f"✅ {filename} caricato con ID {drive_id}")
                    except Exception as e:
                        print(f"❌ Errore upload {filename}: {e}")

if __name__ == "__main__":
    sync_all_agents()
