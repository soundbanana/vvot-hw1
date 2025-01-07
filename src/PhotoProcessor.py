import logging
import requests
from constants import TELEGRAM_API_URL, TELEGRAM_FILE_URL, MESSAGES
from utils import ProcessingError
from YandexAPIClient import YandexAPIClient
from typing import Optional

# Set up a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class PhotoProcessor:
    """Handles processing of photo messages."""

    def __init__(self, yandex_api_client: YandexAPIClient):
        self.yandex_api_client = yandex_api_client

    def get_text_from_photo(self, photo, message) -> str:
        """Processes photo messages by recognizing text and generating a response."""
        if "media_group_id" in message:
            return MESSAGES["multiple_photos_error"]  # Reject multiple photos.

        file_id = photo[-1]["file_id"]
        file_path = self.get_file_path(file_id)
        if not file_path:
            raise ProcessingError(MESSAGES["photo_processing_error"])

        image = self.get_image(file_path)
        if not image:
            raise ProcessingError(MESSAGES["photo_download_error"])

        text, error = self.yandex_api_client.recognize_text_on_photo(image)
        if error:
            raise ProcessingError(str(error))
        elif not text:
            raise ProcessingError("На изображении не удалось распознать текст")
        return text
    
    @staticmethod
    def get_file_path(file_id: str) -> Optional[str]:
        """Retrieves the file path of a Telegram file using its file_id."""
        url = f"{TELEGRAM_API_URL}/getFile"
        try:
            response = requests.get(url, params={"file_id": file_id})
            response.raise_for_status()
            return response.json().get("result", {}).get("file_path")
        except requests.RequestException as e:
            logger.error(f"Failed to get file path: {e}", {"file_id": file_id})
            return None
    
    @staticmethod
    def get_image(file_path: str) -> Optional[bytes]:
        """Downloads the image content from Telegram servers."""
        url = f"{TELEGRAM_FILE_URL}/{file_path}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Failed to download image: {e}", {"file_path": file_path})
            return None
