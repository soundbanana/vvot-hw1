import requests
import os
from constants import FOLDER_ID, SERVICE_ACCOUNT_API_KEY, YANDEX_GPT_API_URL

def handle_text_message(text):
    answer = get_answer_from_gpt(text)
    if not answer:
        return "Я не смог подготовить ответ на ваш запрос."
    else:
        return answer

def get_answer_from_gpt(text):
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
                "text": "Ты преподаватель по предмету Облачные технологии"
            },
            {
                "role": "user",
                "text": text
            },
        ],
    }

    response = requests.post(YANDEX_GPT_API_URL, headers=headers, json=data)

    if not response.ok:
        print("Failed to get GPT response")
        return None
    alternatives = response.json().get("result", {}).get("alternatives", [])
    final_answer = next((alt["message"].get("text") for alt in alternatives if alt.get("status") == "ALTERNATIVE_STATUS_FINAL"), None)
    return final_answer