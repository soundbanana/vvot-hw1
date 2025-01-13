import base64
import logging
import requests
from constants import YANDEX_GPT_API_URL, YANDEX_OCR_API_URL, SERVICE_ACCOUNT_API_KEY, FOLDER_ID, MESSAGES, BUCKET_OBJECT_GPT_INSTRUCTIONS_KEY
from utils import ProcessingError
from helpers import get_object_from_bucket

# Set up a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class YandexAPIClient:
    """Handles communication with Yandex GPT and OCR APIs."""
    
    def __init__(self, service_account_api_key: str, folder_id: str):
        self.service_account_api_key = service_account_api_key
        self.folder_id = folder_id

    def get_answer_from_gpt(self, text):
        """Gets a response from Yandex GPT API."""
        try:
            answer = self.ask_gpt(text)
            if not answer:
                raise ProcessingError("No answer was returned from GPT.")
            return answer
        except ProcessingError as e:
            logger.error(f"Error getting answer from GPT: {e}")
            return str(e)
        
    def ask_gpt(self, text):
        """Sends a request to Yandex GPT API and retrieves the response."""
        headers = {
            "Content-Type": "application/json",
            "x-folder-id": FOLDER_ID,
            "Authorization": f"Api-Key {SERVICE_ACCOUNT_API_KEY}",
        }
        data = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
            "messages": [
                {
                    "role": "system",
                    "text": get_object_from_bucket(BUCKET_OBJECT_GPT_INSTRUCTIONS_KEY)
                },
                {
                    "role": "user",
                    "text": text
                },
            ],
        }
        try:
            response = requests.post(YANDEX_GPT_API_URL, headers=headers, json=data)
            response.raise_for_status()  # Raise exception for HTTP errors.
            alternatives = response.json().get("result", {}).get("alternatives", [])
            return next(
                (alt["message"].get("text") for alt in alternatives if alt.get("status") == "ALTERNATIVE_STATUS_FINAL"),
                None,
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Yandex GPT API: {e}")
            raise ProcessingError("Failed to connect to Yandex GPT API", str(e))
        
    # Sends an image to Yandex OCR API and returns the (response, error).
    def recognize_text_on_photo(self, image):
        # Sends an image to Yandex OCR API and returns the recognized text or an error.
        base64_image = self.encode_to_base64(image)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.service_account_api_key}",
        }
        body = {
            "content": base64_image,
            "mimeType": "image/jpeg",
            "languageCodes": ["ru", "en"],
        }

        try:
            response = requests.post(YANDEX_OCR_API_URL, headers=headers, json=body)
            response.raise_for_status()  # Raise an exception for HTTP errors.
            # Extract and return the recognized text.
            return (response.json().get("result", {}).get("textAnnotation", {}).get("fullText"), None)
        except requests.RequestException as e:
            print(f"OCR recognition failed: {e}")
            return (None, MESSAGES["ocr_recognition_error"])
        
    @staticmethod
    def encode_to_base64(bytes_content: bytes) -> str:
        """Encodes byte content to a Base64 string."""
        return base64.b64encode(bytes_content).decode("utf-8")
