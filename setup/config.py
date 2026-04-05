import os
from dotenv import load_dotenv

load_dotenv()

# Google
GOOGLE_CLIENT_SECRET_FILE = os.getenv("GOOGLE_CLIENT_SECRET_FILE", "credentials/client_secret.json")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")

# Sheets tab names
SHEET_TAB_RATES = "単価"
SHEET_TAB_MANAGEMENT = "管理"

# Gmail
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOTIFY_TO = os.getenv("NOTIFY_TO")

# Paths
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansJP-Regular.ttf")
RUNS_DIR = os.path.join(os.path.dirname(__file__), "runs")
