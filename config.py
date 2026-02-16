import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# --- API Keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# WhatsApp Meta API
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# WispHub CRM
WISPHUB_API_URL = os.getenv("WISPHUB_API_URL", "https://api.wisphub.net")
WISPHUB_API_TOKEN = os.getenv("WISPHUB_API_TOKEN")

# --- Directories ---
PENDING_DIR = BASE_DIR / "pending_receipts"
PROCESSED_DIR = BASE_DIR / "processed_receipts"
ERROR_DIR = BASE_DIR / "error_receipts"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "payments.db"

for directory in [PENDING_DIR, PROCESSED_DIR, ERROR_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# --- WhatsApp API URL ---
WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}"
