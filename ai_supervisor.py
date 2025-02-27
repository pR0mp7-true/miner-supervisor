import os
import time
import json
import requests
import re
import sys
import subprocess

# 🔥 Configuration
MINER_CMD = os.path.expanduser("~/miner-supervisor/xmrig-bin")
WALLET_ADDRESS = "47mV652Zp3XHKvemVSWLDG5dCqnWteamwhRRSuVSJ5peEUaPKMHkE3jhzsobGQvJE4SsoqPBUyw9C1fSQE8Y6FY216jnfHN"
CONFIG_FILE = os.path.expanduser("~/miner-supervisor/config.json")
POOL_LIST_API = "https://moneroworld.com/hosts.txt"
POOL_API = f"https://xmrpool.eu/api/miner/{WALLET_ADDRESS}"
TRANSFER_API = "https://your-exchange.com/api/withdraw"
TRANSFER_THRESHOLD = 0.004
MAX_RETRIES = 3
CURRENT_POOL = "pool.supportxmr.com:3333"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/pR0mp7-true/miner-supervisor/main/ai_supervisor.py"
UPDATE_INTERVAL = 3600  # Check for updates every 1 hour

# ✅ Validate Wallet
def is_valid_wallet(wallet):
    wallet = wallet.strip()
    print(f"Validating Wallet: '{wallet}'")
    return re.match(r"^[48][0-9A-Za-z]{94}$", wallet) is not None

if not is_valid_wallet(WALLET_ADDRESS):
    print(f"[❌] Invalid Wallet: '{WALLET_ADDRESS}'")
    exit(1)

print("[✅] Wallet is valid! Starting AI Supervisor...")

# 🔄 Auto-Update Script (Fixed Infinite Loop)
def update_script():
    try:
        response = requests.get(GITHUB_SCRIPT_URL, timeout=5)
        if response.status_code == 200:
            script_path = os.path.abspath(__file__)
            
            # Read current script
            with open(script_path, "r") as f:
                current_script = f.read()
            
            # Compare with the new script before updating
            if response.text.strip() == current_script.strip():
                print("[✅] AI Supervisor is up to date. No update needed.")
                return  # No need to restart

            # Update script
            with open(script_path, "w") as f:
                f.write(response.text)

            print("[✅] AI Supervisor updated! Restarting...")
            os.execv(sys.executable, ["python"] + sys.argv)  # Restart script
    except requests.RequestException:
        print("[⚠️] Auto-update failed. Continuing...")

# 🔄 Fetch New Pool if Blocked
def fetch_new_pool():
    global CURRENT_POOL
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(POOL_LIST_API, timeout=5)
            pools = response.text.splitlines()
            available_pools = [p for p in pools if "." in p]

            if available_pools:
                CURRENT_POOL = available_pools[0]
                print(f"[🔄] New Pool Selected: {CURRENT_POOL}")
                return CURRENT_POOL
            else:
                print("[⚠️] No pools available! Using last known pool.")
                return CURRENT_POOL
        except requests.RequestException:
            print(f"[⚠️] Failed to fetch pool list. Retrying... ({retries+1}/{MAX_RETRIES})")
            time.sleep(2)
            retries += 1

    print("[❌] Pool list unreachable! Using last known pool.")

# 🚀 Start Mining
def start_mining():
    global CURRENT_POOL

    print(f"[🚀] Starting mining with wallet: {WALLET_ADDRESS} on pool {CURRENT_POOL}")
    os.system(f"{MINER_CMD} -o {CURRENT_POOL} -u {WALLET_ADDRESS} -p x")  # Command to start mining

# 🔄 Check Miner and Restart if Down
def restart_miner():
    print("[⚠️] Miner is down! Restarting...")
    subprocess.Popen(f"{MINER_CMD} -o {CURRENT_POOL} -u {WALLET_ADDRESS} -p x", shell=True)

# 🛠 Main Execution
if __name__ == "__main__":
    update_script()  # Auto-update before starting
    fetch_new_pool()  # Get a working pool
    while True:
        # Check if miner is running
        miner_running = subprocess.run(["pgrep", "-f", "xmrig"], stdout=subprocess.PIPE).stdout
        if not miner_running:
            restart_miner()

        time.sleep(UPDATE_INTERVAL)  # Wait before checking again
