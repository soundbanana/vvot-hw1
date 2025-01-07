import requests
import os
from constants import FOLDER_ID, SERVICE_ACCOUNT_API_KEY, YANDEX_GPT_API_URL, MESSAGES
from photos_processing import get_file_path, get_image, recognize_text_on_photo

# Handles user text input and generates a response via Yandex GPT API.
def handle_text_message(text):
    answer = get_answer_from_gpt(text)
    if not answer:
        return "Я не смог подготовить ответ на ваш запрос."
    else:
        return answer

# Sends a text input to Yandex GPT API and retrieves the response.
def get_answer_from_gpt(text):
    headers = {
        "Content-Type": "application/json",
        "x-folder-id": FOLDER_ID,
        "Authorization": f"Api-Key {SERVICE_ACCOUNT_API_KEY}",
    }

    # API request payload.
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "messages": [
            {
                "role": "system",
                "text": "Ты преподаватель по предмету Облачные технологии"
            },
            {
                "role": "user",
                "text": text
            },
        ],
    }

    try:
        # Send request to Yandex GPT API.
        response = requests.post(YANDEX_GPT_API_URL, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors.
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to Yandex GPT API: {e}")
        return None

    # Extract the final answer from the response.
    alternatives = response.json().get("result", {}).get("alternatives", [])
    return next(
        (alt["message"].get("text") for alt in alternatives if alt.get("status") == "ALTERNATIVE_STATUS_FINAL"),
        None,
    )

def handle_photo_message(photo, message):
    # Processes photo messages by recognizing text and generating a response.
    if "media_group_id" in message:
        return MESSAGES["multiple_photos_error"]  # Reject multiple photos.

    # Get the file ID of the highest resolution photo.
    file_id = photo[-1]["file_id"]

    # Retrieve the file path from Telegram API.
    file_path = get_file_path(file_id)
    if not file_path:
        return MESSAGES["photo_processing_error"]

    # Download the image file.
    image = get_image(file_path)
    if not image:
        return MESSAGES["photo_download_error"]

    # Recognize text in the image using OCR.
    text, error = recognize_text_on_photo(image)
    if error:
        return error  # Return OCR-specific errors.
    elif not text:
        return "На изображении не удалось распознать текст"
    
    # Return recognized text.
    return text