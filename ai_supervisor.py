import os
import time
import json
import requests
import re
import sys

# 🔥 Configuration
MINER_CMD = os.path.expanduser("~/miner-supervisor/xmrig-bin")
WALLET_ADDRESS = "47mV652Zp3XHKvemVSWLDG5..."  # Replace with your actual wallet
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
    global CURRENT_POOL
    update_script()  # Check for updates before starting

    while True:
        print(f"[🚀] Starting miner at {CURRENT_POOL}...")
        miner_process = os.popen(f"{MINER_CMD} -o {CURRENT_POOL} -u {WALLET_ADDRESS} --tls --coin monero")

        time.sleep(60)  # Check status every 60 seconds

        if miner_process.close() is not None:
            print("[⚠️] Miner crashed! Restarting...")
            CURRENT_POOL = fetch_new_pool()
            continue

# 🔄 Auto-Withdraw Profits
def check_balance_and_withdraw():
    try:
        response = requests.get(POOL_API, timeout=5)
        data = response.json()
        balance = data.get("stats", {}).get("balance", 0) / 1e12

        print(f"[💰] Current balance: {balance} XMR")

        if balance >= TRANSFER_THRESHOLD:
            print("[✅] Balance threshold reached! Withdrawing...")
            payload = {"amount": balance, "to": WALLET_ADDRESS}
            withdraw_response = requests.post(TRANSFER_API, json=payload)
            print("[💸] Withdrawal Status:", withdraw_response.text)
        else:
            print("[⏳] Balance too low for withdrawal.")
    except requests.RequestException:
        print("[⚠️] Failed to check balance. Retrying later.")

# 🔁 Main Loop
if __name__ == "__main__":
    while True:
        start_mining()
        check_balance_and_withdraw()
        time.sleep(300)  # Check every 5 minutes
