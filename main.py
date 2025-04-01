# main.py - Avvia bootstrap Drive se mancano le directory essenziali

import os
import json
from uploader_module import DriveUploader
from bootstrap_drive import structure, DRIVE_ROOT_NAME, DRIVE_LOG_FILE, DRIVE_REGISTRY

uploader = DriveUploader()

def check_or_create_drive_structure():
    """
    Controlla se il file di log esiste, altrimenti crea la struttura su Drive.
    """
    if os.path.exists(DRIVE_LOG_FILE) and os.path.exists(DRIVE_REGISTRY):
        print("📂 Struttura già inizializzata. Nessuna azione necessaria.")
        return

    print("🛠️ Avvio bootstrap Drive (trigger da main.py)...")
    log_data = {}
    registry_data = {}

    root_id = uploader._ensure_subfolder(DRIVE_ROOT_NAME)
    log_data[DRIVE_ROOT_NAME] = root_id

    for section, contents in structure.items():
        section_id = uploader._ensure_subfolder(section, parent_id=root_id)
        log_data[section] = section_id

        for main_folder, subfolders in contents.items():
            main_id = uploader._ensure_subfolder(main_folder, parent_id=section_id)
            registry_data[main_folder] = {
                "id": main_id,
                "section": section
            }
            for sub in subfolders:
                sub_id = uploader._ensure_subfolder(sub, parent_id=main_id)
                log_data[f"{main_folder}/{sub}"] = sub_id

    with open(DRIVE_LOG_FILE, "w") as log:
        json.dump(log_data, log, indent=2)

    with open(DRIVE_REGISTRY, "w") as reg:
        json.dump(registry_data, reg, indent=2)

    print("✅ STRUTTURA CREATA SU DRIVE")
    print(json.dumps(log_data, indent=2))

if __name__ == "__main__":
    check_or_create_drive_structure()
