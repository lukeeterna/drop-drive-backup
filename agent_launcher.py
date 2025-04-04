# agent_launcher.py
import sys
from create_drive_folder import create_drive_folder

if __name__ == "__main__":
    agent = sys.argv[1] if len(sys.argv) > 1 else "default_agent"
    create_drive_folder(agent)
