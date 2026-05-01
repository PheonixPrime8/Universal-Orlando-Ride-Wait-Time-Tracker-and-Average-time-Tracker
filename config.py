import os


DB_NAME = os.getenv("DB_NAME", "wait_times.db")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
REFRESH_COOLDOWN_SECONDS = int(os.getenv("REFRESH_COOLDOWN_SECONDS", "60"))
AUTO_REFRESH_INTERVAL_SECONDS = int(os.getenv("AUTO_REFRESH_INTERVAL_SECONDS", "600"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
APP_PORT = int(os.getenv("PORT", "5000"))
