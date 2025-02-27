import os
import sys
import time
import requests
import json
import subprocess

# Configuration
WALLET_ADDRESS = "47mV652Zp3XHKvemVSWLDG5dCqnWteamwhRRSuVSJ5peEUaPKMHkE3jhzsobGQvJE4SsoqPBUyw9C1fSQE8Y6FY216jnfHN"
MINER_PATH = os.path.expanduser("~/miner-supervisor/xmrig-bin")
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/YOUR_GITHUB/ai_supervisor/main/ai_supervisor.py"
AUTO_UPDATE = False  # Set to False to disable auto-restart

def validate_wallet():
    print(f"Validating Wallet: '{WALLET_ADDRESS}'")
    return WALLET_ADDRESS.startswith("4") or WALLET_ADDRESS.startswith("8")

def check_miner():
    return os.path.exists(MINER_PATH) and os.access(MINER_PATH, os.X_OK)

def start_miner():
    if not check_miner():
        print("[⚠️] Miner is missing or not executable!")
        return
    print("[✅] Starting miner...")
    subprocess.Popen([MINER_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def update_script():
    print("[🔄] Checking for script updates...")
    try:
        response = requests.get(GITHUB_SCRIPT_URL, timeout=5)
        if response.status_code == 200:
            with open(__file__, "w") as f:
                f.write(response.text)
            print("[✅] AI Supervisor updated! Restarting...")
            if AUTO_UPDATE:
                os.execv(__file__, sys.argv)
        else:
            print("[⚠️] No updates found.")
    except Exception as e:
        print(f"[❌] Update failed: {e}")

if __name__ == "__main__":
    if not validate_wallet():
        print("[❌] Invalid Wallet Address!")
        sys.exit(1)

    print("[✅] Wallet is valid! Starting AI Supervisor...")

    if AUTO_UPDATE:
        update_script()

    while True:
        if not check_miner():
            print("[⚠️] Miner is down! Restarting...")
            start_miner()
        time.sleep(10)  # Check every 10 seconds
