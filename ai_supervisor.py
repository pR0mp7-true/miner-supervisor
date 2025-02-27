# AI Supervisor Script for Termux
# - Validates wallet before mining
# - Restarts miner if it crashes
# - Auto-updates itself from GitHub

import os
import time
import requests
import subprocess

# Configuration
WALLET_ADDRESS = "YOUR_MONERO_WALLET_ADDRESS"
MINER_PATH = "/data/data/com.termux/files/home/miner-supervisor/xmrig-bin"
MINER_COMMAND = f"{MINER_PATH} --donate-level 1 -o pool.minexmr.com:443 -u {WALLET_ADDRESS} -k --tls"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/YOUR_GITHUB/ai_supervisor/main/ai_supervisor.py"
UPDATE_INTERVAL = 3600  # Check for updates every 1 hour


def validate_wallet(wallet):
    print(f"Validating Wallet: '{wallet}'")
    return len(wallet) > 95  # Basic validation


def restart_miner():
    print("[⚠️] Miner is down! Restarting...")
    subprocess.Popen(MINER_COMMAND, shell=True)


def update_script():
    try:
        print("[✅] Checking for script updates...")
        response = requests.get(GITHUB_SCRIPT_URL, timeout=5)
        if response.status_code == 200:
            with open(__file__, "w") as script_file:
                script_file.write(response.text)
            print("[✅] AI Supervisor updated! Restarting...")
            os.execv(__file__, [])
        else:
            print("[⚠️] No updates found.")
    except Exception as e:
        print(f"[⚠️] Update failed: {e}")


# Main Execution
if __name__ == "__main__":
    if validate_wallet(WALLET_ADDRESS):
        print("[✅] Wallet is valid! Starting AI Supervisor...")
    else:
        print("[❌] Invalid wallet address!")
        exit(1)

    while True:
        if not os.path.exists(MINER_PATH):
            print("[⚠️] Miner binary missing! Please install XMRig.")
            exit(1)

        # Check if miner is running
        miner_running = subprocess.run(["pgrep", "-f", "xmrig"], stdout=subprocess.PIPE).stdout
        if not miner_running:
            restart_miner()

        # Check for updates
        update_script()

        time.sleep(UPDATE_INTERVAL)
