import os
import json
import requests

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
    "non_command": "Я могу работать только с командами. Попробуйте /start или /help.",
    "no_message": "No message to process.",
    "error": "Произошла ошибка при обработке сообщения.",
}

# Function to send messages
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, data=data)
    return r

# Process a command or text message
def handle_message(message, chat_id):
    # Check for commands in the message
    entities = message.get("entities", [])
    command_entity = next((e for e in entities if e.get("type") == "bot_command"), None)
    if command_entity:
        command = message["text"][command_entity["offset"]:command_entity["offset"] + command_entity["length"]]
        if command in SUPPORTED_COMMANDS:
            send_message(chat_id, MESSAGES["start_help"])
        else:
            send_message(chat_id, MESSAGES["unknown_command"])
    else:
        send_message(chat_id, MESSAGES["non_command"])

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
