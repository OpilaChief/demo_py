import os
import random

import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

load_dotenv()
TOKEN = os.getenv("VK_GROUP_TOKEN")
GROUP_ID = int(os.getenv("VK_GROUP_ID", "0"))

MAX_MESSAGE_LENGTH = 3500
MAX_RANDOM_ID = 2_147_483_647

START_WORD = 'викторина'

QUESTIONS = [
    ("Какой тип данных хранит пары ключ-значение?", "словарь"),
    ("Как называется файл для секретных переменных?", ".env"),
    ("Куда отвечаем в VK: peer_id или from_id?", "peer_id"),
]
GAMES = {}


def send_message(vk, peer_id, text):
    vk.messages.send(peer_id=peer_id, message=text[:MAX_MESSAGE_LENGTH], random_id=random.randint(1, MAX_RANDOM_ID))


def start_game(user_id):
    game = GAMES.get(user_id)
    if game is None:
        GAMES[user_id] = game = {"step": 0, "score": 0}
    return QUESTIONS[game["step"]][0]


def answer_quiz(user_id, text):
    game = GAMES.get(user_id)
    if game is None:
        return "Напиши: " + START_WORD

    if not text:
        return QUESTIONS[game["step"]][0]

    question, right_answer = QUESTIONS[game["step"]]
    if text == right_answer:
        game["score"] += 1

    game["step"] += 1
    if game["step"] >= len(QUESTIONS):
        score = game["score"]
        del GAMES[user_id]
        return f"Игра окончена. Счёт: {score}/{len(QUESTIONS)}"

    return QUESTIONS[game["step"]][0]


def main():
    session = vk_api.VkApi(token=TOKEN)
    vk = session.get_api()
    longpoll = VkBotLongPoll(session, GROUP_ID)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.object.message
            text = message.get("text", "").strip().lower()
            from_id = message["from_id"]
            if text == START_WORD:
                answer = start_game(from_id)
            else:
                answer = answer_quiz(from_id, text)
            send_message(vk, message["peer_id"], answer)


if __name__ == "__main__":
    print(f"Token {'found' if TOKEN else 'not found'}")
    print(f"Token {'correct' if len(TOKEN) > 100 else 'incorrect'}")
    print(f"Group ID {GROUP_ID}")
    main()
