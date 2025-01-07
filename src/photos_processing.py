import base64
import requests
from constants import TELEGRAM_API_URL, TELEGRAM_FILE_URL, YANDEX_OCR_API_URL, SERVICE_ACCOUNT_API_KEY, MESSAGES

# Encodes byte content to a Base64 string.
def encode_to_base64(bytes_content):
    return base64.b64encode(bytes_content).decode("utf-8")

# Retrieves the file path of a Telegram file using its file_id.
def get_file_path(file_id):
    url = f"{TELEGRAM_API_URL}/getFile"
    try:
        response = requests.get(url, params={"file_id": file_id})
        response.raise_for_status()  # Raise an exception for HTTP errors.
        return response.json().get("result", {}).get("file_path")
    except requests.RequestException as e:
        print(f"Failed to get file path: {e}", {"file_id": file_id})
        return None

# Downloads the image content from Telegram servers.
def get_image(file_path):
    url = f"{TELEGRAM_FILE_URL}/{file_path}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors.
        return response.content
    except requests.RequestException as e:
        print(f"Failed to download image: {e}", {"file_path": file_path})
        return None

# Sends an image to Yandex OCR API and returns the (response, error).
def recognize_text_on_photo(image):
    # Sends an image to Yandex OCR API and returns the recognized text or an error.
    base64_image = encode_to_base64(image)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {SERVICE_ACCOUNT_API_KEY}",
    }
    body = {
        "content": base64_image,
        "mimeType": "image/jpeg",
        "languageCodes": ["ru", "en"],  # OCR supports Russian and English.
    }

    try:
        # Send OCR recognition request.
        response = requests.post(YANDEX_OCR_API_URL, headers=headers, json=body)
        response.raise_for_status()  # Raise an exception for HTTP errors.
        # Extract and return the recognized text.
        return (response.json().get("result", {}).get("textAnnotation", {}).get("fullText"), None)
    except requests.RequestException as e:
        print(f"OCR recognition failed: {e}")
        return (None, MESSAGES["ocr_recognition_error"])