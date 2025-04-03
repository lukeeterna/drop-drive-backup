# agent_registry.py - Traccia tutti gli agenti creati in Drive
import json
import os
from datetime import datetime

REGISTRY_FILE = "agent_registry.json"

def register_agent(agent_name, folder_id):
    entry = {
        "agent": agent_name,
        "folder_id": folder_id,
        "created_at": datetime.now().isoformat()
    }
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE) as f:
            registry = json.load(f)
    else:
        registry = []

    registry.append(entry)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)

    print(f"✅ Agente '{agent_name}' registrato con ID: {folder_id}")

# ESEMPIO USO:
# register_agent("saas_architect_gpt", "1AbcD...XYZ")
