import threading
import time
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")
API_KEY = os.getenv("API_KEY")
API_URL = "https://securebank.com/api/transaction"

# Lock for thread safety
balance_lock = threading.Lock()

# In-memory user database (simulated)
users = {
    "alice": {"balance": 1000, "account_number": "123-456-789"},
    "bob": {"balance": 500, "account_number": "987-654-321"}
}

# ---------------- AUTH MODULE ----------------
def authenticate(username: str, password: str) -> bool:
    """Authenticate the user securely."""
    if username == ADMIN_USER and password == ADMIN_PASS:
        return True
    return False

# ---------------- LOGGER MODULE ----------------
def audit_log(event: str):
    """Log event securely without sensitive information."""
    with open("audit.log", "a") as log_file:
        log_file.write(f"{time.ctime()} - EVENT: {event}\n")

# ---------------- TRANSACTION MODULE ----------------
def is_valid_user(username: str) -> bool:
    return username in users

def get_user_balance(username: str) -> float:
    return users[username]["balance"]

def transfer_funds(sender: str, receiver: str, amount: float) -> bool:
    if not (is_valid_user(sender) and is_valid_user(receiver)):
        audit_log(f"Transfer failed: Invalid user(s): {sender}, {receiver}")
        return False

    if amount <= 0:
        audit_log(f"Transfer failed: Invalid amount: {amount}")
        return False

    with balance_lock:
        if users[sender]["balance"] >= amount:
            users[sender]["balance"] -= amount
            time.sleep(1)  # Simulate processing delay
            users[receiver]["balance"] += amount

            audit_log(f"Transferred ₹{amount} from {sender} to {receiver}")
            return True
        else:
            audit_log(f"Transfer failed: Insufficient balance for {sender}")
            return False

# ---------------- API CALL MODULE ----------------
def call_transaction_api():
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(API_URL, headers=headers, timeout=5)
        print("API call status:", response.status_code)
        return response.ok
    except requests.RequestException as e:
        audit_log(f"API call failed: {e}")
        return False

# ---------------- MAIN EXECUTION ----------------
def run_transaction_flow():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")

    if not authenticate(username, password):
        print("Authentication failed.")
        audit_log("Unauthorized login attempt")
        return

    success = transfer_funds("alice", "bob", 200)
    if success:
        print("Transaction successful.")
    else:
        print("Transaction failed.")

    call_transaction_api()

def simulate_multiple_transfers():
    """Simulates concurrent transfers to test thread safety."""
    threads = []
    for _ in range(5):
        t = threading.Thread(target=transfer_funds, args=("alice", "bob", 50))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    print("🔐 Secure Banking Transaction Simulation 🔐\n")
    run_transaction_flow()
    simulate_multiple_transfers()

    print("\nCurrent User Balances:")
    for user, data in users.items():
        print(f"{user.title()}: ₹{data['balance']} (Account: {data['account_number']})")
    # test for sync