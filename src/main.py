import json
import logging
import requests

from constants import TELEGRAM_API_URL, MESSAGES, SERVICE_ACCOUNT_API_KEY, FOLDER_ID
from utils import ProcessingError, CommandHandler, MessageResponse

from YandexAPIClient import YandexAPIClient
from PhotoProcessor import PhotoProcessor

# Set up a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send_message(chat_id, text):
    """Sends a message to a given Telegram chat."""
    logger.info(f"Sending message to chat {chat_id}: {text}")
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    return requests.post(url, data=data)

def get_message_id(processing_message):
    """Extracts the message ID from the Telegram response."""
    return processing_message.json().get("result", {}).get("message_id")

def delete_message(chat_id, message_id):
    """Deletes a specific message in Telegram."""
    url = f"{TELEGRAM_API_URL}/deleteMessage"
    data = {'chat_id': chat_id, 'message_id': message_id}
    r = requests.post(url, data=data)
    return r

# Get text with processing messages
def process_text_from_photo(photo, message, chat_id, photo_processor: PhotoProcessor):
    # Send "Получаю текст с фото..." message and save the response
    processing_message = send_message(chat_id, "Получаю текст с фото...")
    processing_message_id = get_message_id(processing_message)

    # Get message text
    response = photo_processor.get_text_from_photo(photo, message)
    
    # Delete the "Получаю текст с фото..." message
    if processing_message_id:
        delete_message(chat_id, processing_message_id)

    return response

def process_answer(question, chat_id, yandex_api_client: YandexAPIClient):
    # Send "Генерирую ответ..." message and save the response
    processing_message = send_message(chat_id, "Генерирую ответ...")
    processing_message_id = get_message_id(processing_message)

    # Get message text
    response = yandex_api_client.get_answer_from_gpt(question)
    
    # Delete the "Генерирую ответ..." message
    if processing_message_id:
        delete_message(chat_id, processing_message_id)

    send_message(chat_id, response)

def get_message_type(message, chat_id, photo_processor: PhotoProcessor):
    """Processes the message and returns the appropriate response."""
    # Check if the message contains a photo
    if photo := message.get("photo"):  # If the message contains a photo
        response = process_text_from_photo(photo, message, chat_id, photo_processor)
        return MessageResponse(response, MessageResponse.TEXT)
    elif text := message.get("text"):  # If the message contains text
        entities = message.get("entities", [])
        command_entity = next((e for e in entities if e.get("type") == "bot_command"), None)

        if command_entity:  # If the message is a command
            command = text[command_entity["offset"]:command_entity["offset"] + command_entity["length"]]
            return MessageResponse(command, MessageResponse.INFO)

        return MessageResponse(text, MessageResponse.TEXT)

    raise ProcessingError(MESSAGES["incorrect_input"])

def process_message(message, chat_id, yandex_api_client: YandexAPIClient, photo_processor: PhotoProcessor) -> None:
    """Processes the incoming message and responds accordingly."""
    try:
        response = get_message_type(message, chat_id, photo_processor)

        if response.is_error():  # If it's an error, send it immediately
            send_message(chat_id, response.message)
            return

        if response.is_info():  # If it's an info message, send it
            commandHandler = CommandHandler(response.message, chat_id)
            send_message(chat_id, commandHandler.process().message)
            return

        if response.is_text():  # If it's regular text, query GPT and respond
            process_answer(response.message, chat_id, yandex_api_client)

    except ProcessingError as e:
        logger.error(f"Processing error: {e}")
        send_message(chat_id, str(e))

def handler(event, context):
    """Handles the incoming event from Telegram and processes the message."""
    try:
        body = json.loads(event['body'])
        message = body.get("message")

        if not message:
            return {"statusCode": 200, "body": MESSAGES["no_message"]}

        chat_id = message["from"]["id"]
        logger.info(f"Received message from chat {chat_id}: {message}")

        # Initialize API client and photo processor
        yandex_api_client = YandexAPIClient(SERVICE_ACCOUNT_API_KEY, FOLDER_ID)
        photo_processor = PhotoProcessor(yandex_api_client)

        # Process the message
        process_message(message, chat_id, yandex_api_client, photo_processor)

        return {"statusCode": 200, "body": "Message processed."}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": f"{MESSAGES['error']}: {str(e)}"}
