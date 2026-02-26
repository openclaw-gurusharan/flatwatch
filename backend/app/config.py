# Database configuration
from pathlib import Path
import os

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# SQLite database path
DATABASE_PATH = DATA_DIR / "flatwatch.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# API settings
API_TITLE = "FlatWatch API"
API_VERSION = "0.1.0"

# SSO Identity Provider
AADHAAR_CHAIN_URL = os.getenv("AADHAAR_CHAIN_URL", "https://aadhaar-chain.com")
