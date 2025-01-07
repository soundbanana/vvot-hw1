import os

# Telegram Constants
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Yandex Cloud Constants
FOLDER_ID = os.getenv("FOLDER_ID")
SERVICE_ACCOUNT_API_KEY = os.getenv("SERVICE_ACCOUNT_API_KEY")

# API URLs
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
YANDEX_GPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
