import os

# Telegram Constants
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Yandex Cloud Constants
FOLDER_ID = os.getenv("FOLDER_ID")
SERVICE_ACCOUNT_API_KEY = os.getenv("SERVICE_ACCOUNT_API_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
BUCKET_OBJECT_GPT_INSTRUCTIONS_KEY = os.getenv("BUCKET_OBJECT_GPT_INSTRUCTIONS_KEY")

# API URLs
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
TELEGRAM_FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}"
YANDEX_GPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
YANDEX_OCR_API_URL = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"

# Text messages
MESSAGES = {
    "start_help": (
        "Я помогу подготовить ответ на экзаменационный вопрос по дисциплине \"Операционные системы\".\n"
        "Пришлите мне фотографию с вопросом или наберите его текстом."
    ),
    "unknown_command": "Извините, я не понимаю эту команду. Попробуйте /start или /help.",
    "multiple_photos_error": "Я могу обработать только одну фотографию.",
    "incorrect_input": "Я могу обработать только текстовое сообщение или фотографию.\nИспользуйте /help для получения подсказок.",
    "no_message": "No message to process.",
    "photo_processing_error": "Я не могу обработать эту фотографию.",
    "photo_download_error": "Ошибка загрузки изображения.", 
    "ocr_recognition_error": "Не удалось распознать текст на изображении.",
    "error": "Произошла ошибка при обработке сообщения.",
}