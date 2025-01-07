import os
import json
import requests

from messages_handler import handle_text_message

# Telegram Bot Token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# List of supported commands
SUPPORTED_COMMANDS = ["/start", "/help"]

# Text messages
MESSAGES = {
    "start_help": (
        "Я помогу подготовить ответ на экзаменационный вопрос по дисциплине \"Операционные системы\".\n"
        "Пришлите мне фотографию с вопросом или наберите его текстом."
    ),
    "unknown_command": "Извините, я не понимаю эту команду. Попробуйте /start или /help.",
    "multiple_photos_error": "Я могу обработать только одну фотографию.",
    "incorrect_input": "Извините, я не понимаю эту команду. Попробуйте /start или /help.",
    "no_message": "No message to process.",
    "error": "Произошла ошибка при обработке сообщения.",
}

# Function to send messages
def send_message(chat_id, text):
    print(text)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, data=data)
    return r

# Handle message content (commands, photos, and regular text)
def handle_message(message, chat_id):
    if "photo" in message:  # Check if the message contains a photo
        # If multiple photos
        if "media_group_id" in message:
            send_message(chat_id, MESSAGES["multiple_photos_error"])
            return
        send_message(chat_id, "Я получил фото")
        print("Photo metadata:", message["photo"])
    elif "text" in message:  # Check if the message contains text
        # Check for commands in the text
        entities = message.get("entities", [])
        command_entity = next((e for e in entities if e.get("type") == "bot_command"), None)
        if command_entity:
            command = message["text"][command_entity["offset"]:command_entity["offset"] + command_entity["length"]]
            if command in SUPPORTED_COMMANDS:
                send_message(chat_id, MESSAGES["start_help"])
            else:
                send_message(chat_id, MESSAGES["unknown_command"])
        else:
            send_message(chat_id, "Обрабатываю запрос...")
            response = handle_text_message(message["text"])
            send_message(chat_id, response)
    else:
        send_message(chat_id, MESSAGES["incorrect_input"])

# Main function to handle events
def handler(event, context):
    try:
        body = json.loads(event['body'])
        message = body.get("message")
        if not message:
            return {"statusCode": 200, "body": MESSAGES["no_message"]}

        chat_id = message["from"]["id"]
        print(f"Received message: {message}")

        handle_message(message, chat_id)

        return {"statusCode": 200, "body": "Message processed."}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": f"{MESSAGES['error']}: {str(e)}"}
