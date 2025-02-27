import os
import time
import json
import requests
import re
import sys
import subprocess

# 🔥 Configuration
WALLET_ADDRESS = "47mV652Zp3XHKvemVSWLDG5dCqnWteamwhRRSuVSJ5peEUaPKMHkE3jhzsobGQvJE4SsoqPBUyw9C1fSQE8Y6FY216jnfHN"  # Replace after withdrawal
MINER_CMD = os.path.expanduser("~/miner-supervisor/xmrig-bin")
POOL_LIST_API = "https://moneroworld.com/hosts.txt"
POOL_API = f"https://xmrpool.eu/api/miner/{WALLET_ADDRESS}"
TRANSFER_API = "https://your-exchange.com/api/withdraw"
TRANSFER_THRESHOLD = 0.004
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/pR0mp7-true/miner-supervisor/main/ai_supervisor.py"
UPDATE_INTERVAL = 3600  # Check for updates every hour
MAX_RETRIES = 3
CURRENT_POOL = "pool.supportxmr.com:3333"
MINER_COMMAND = f"{MINER_CMD} --donate-level 1 -o {CURRENT_POOL} -u {WALLET_ADDRESS} -k --tls"

# ✅ Validate Wallet
def is_valid_wallet(wallet):
    wallet = wallet.strip()
    print(f"Validating Wallet: '{wallet}'")
    return re.match(r"^[48][0-9A-Za-z]{94}$", wallet) is not None

if not is_valid_wallet(WALLET_ADDRESS):
    print(f"[❌] Invalid Wallet: '{WALLET_ADDRESS}'")
    exit(1)

print("[✅] Wallet is valid! Starting AI Supervisor...")

# 🔄 Auto-Update Script
def update_script():
    try:
        print("[✅] Checking for script updates...")
        response = requests.get(GITHUB_SCRIPT_URL, timeout=5)
        if response.status_code == 200:
            script_path = os.path.abspath(__file__)
            with open(script_path, "w") as f:
                f.write(response.text)
            print("[✅] AI Supervisor updated! Restarting...")
            os.execv(sys.executable, ["python"] + sys.argv)
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
    print(f"[🚀] Starting mining with wallet: {WALLET_ADDRESS} on pool {CURRENT_POOL}")
    subprocess.Popen(MINER_COMMAND, shell=True)

# 🔄 Restart Miner if Crashed
def restart_miner():
    print("[⚠️] Miner is down! Restarting...")
    subprocess.Popen(MINER_COMMAND, shell=True)

# Main Execution
if __name__ == "__main__":
    update_script()
    fetch_new_pool()

    while True:
        if not os.path.exists(MINER_CMD):
            print("[⚠️] Miner binary missing! Please install XMRig.")
            exit(1)

        # Check if miner is running
        miner_running = subprocess.run(["pgrep", "-f", "xmrig"], stdout=subprocess.PIPE).stdout
        if not miner_running:
            restart_miner()

        # Check for updates periodically
        time.sleep(UPDATE_INTERVAL)
