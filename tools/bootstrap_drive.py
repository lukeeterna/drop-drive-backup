# LUKE_SYSTEM_BOOTSTRAP - Inizializza struttura AGENTI/PROGETTI su Drive con log degli ID

import os
import json
from uploader_module import DriveUploader

DRIVE_ROOT_NAME = "LUKE_SYSTEM_ROOT"
DRIVE_AGENTI = "AGENTI"
DRIVE_PROGETTI = "PROGETTI"
DRIVE_LOG_FILE = "drive_structure_log.json"
DRIVE_REGISTRY = "AGENT_REGISTRY.json"

uploader = DriveUploader()

# Struttura iniziale da creare
structure = {
    "AGENTI": {
        "LUKE_TEST_AGENT": ["LOG", "XML"]
    },
    "PROGETTI": {
        "PROVA_PROGETTO": []
    }
}

# Funzione per creare ricorsivamente e loggare
log_data = {}
registry_data = {}

print("🛠️ Avvio bootstrap Drive...")

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

# Salvo log
with open(DRIVE_LOG_FILE, "w") as log:
    json.dump(log_data, log, indent=2)

with open(DRIVE_REGISTRY, "w") as reg:
    json.dump(registry_data, reg, indent=2)

print("✅ STRUTTURA CREATA SU DRIVE")
print(json.dumps(log_data, indent=2))
