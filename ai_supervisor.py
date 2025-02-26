import os
import time
import json
import requests
import re
import sys

# 🔥 Configuration
MINER_CMD = os.path.expanduser("~/miner-supervisor/xmrig-bin")
WALLET_ADDRESS = "47mV652Zp3XHKvemVSWLDG5..."  # Initial Wallet Address
CONFIG_FILE = os.path.expanduser("~/miner-supervisor/config.json")
POOL_LIST_API = "https://moneroworld.com/hosts.txt"
POOL_API = f"https://xmrpool.eu/api/miner/{WALLET_ADDRESS}"
TRANSFER_API = "https://your-exchange.com/api/withdraw"
TRANSFER_THRESHOLD = 0.004
MAX_RETRIES = 3
CURRENT_POOL = "pool.supportxmr.com:3333"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/pR0mp7-true/miner-supervisor/main/ai_supervisor.py"

# ✅ Validate Wallet
def is_valid_wallet(wallet):
    return re.match(r"^[48][0-9A-Za-z]{94}$", wallet) is not None

# Function to get new wallet (from MyMonero API or other service)
def fetch_new_wallet():
    # Mock API to fetch new wallet address (replace with actual API or service)
    try:
        response = requests.get("https://your-exchange.com/api/get-new-wallet", timeout=5)
        if response.status_code == 200:
            new_wallet = response.json().get("wallet_address", None)
            if new_wallet and is_valid_wallet(new_wallet):
                return new_wallet
            else:
                print("[⚠️] Invalid wallet fetched! Keeping old wallet.")
                return WALLET_ADDRESS  # Keep the old wallet if new wallet is invalid
        else:
            print("[⚠️] Failed to fetch new wallet. Keeping old wallet.")
            return WALLET_ADDRESS
    except requests.RequestException:
        print("[⚠️] Error fetching new wallet. Keeping old wallet.")
        return WALLET_ADDRESS

# Update WALLET_ADDRESS globally (auto-update)
WALLET_ADDRESS = fetch_new_wallet()  # Update wallet here

if not is_valid_wallet(WALLET_ADDRESS):
    print("[❌] Invalid Wallet! Check your config.")
    exit(1)

print("[✅] Wallet is valid! Starting AI Supervisor...")

# 🔄 Auto-Update Script
def update_script():
    try:
        response = requests.get(GITHUB_SCRIPT_URL, timeout=5)
        if response.status_code == 200:
            script_path = os.path.abspath(__file__)  # Get current script path
            with open(script_path, "w") as f:
                f.write(response.text)  # Overwrite the script with new content
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
    global CURRENT_POOL, WALLET_ADDRESS
    # Update wallet before starting mining if necessary
    WALLET_ADDRESS = fetch_new_wallet()
    print(f"[✅] Using Wallet: {WALLET_ADDRESS}")
    
    # Command to start mining (example)
    miner_command = f"{MINER_CMD} -o {CURRENT_POOL} -u {WALLET_ADDRESS}"
    print(f"[🚀] Starting mining with command: {miner_command}")
    os.system(miner_command)

if __name__ == "__main__":
    update_script()  # Check for script update
    start_mining()   # Start mining with updated configuration
