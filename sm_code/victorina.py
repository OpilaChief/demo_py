import os

import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from config import START_COMMANDS, EXIT_COMMAND
from vk_sender import send_message

load_dotenv()
TOKEN = os.getenv("VK_GROUP_TOKEN")
GROUP_ID = int(os.getenv("VK_GROUP_ID", "0"))

QUESTIONS = [
    ("Какой тип данных хранит пары ключ-значение?", "словарь"),
    ("Как называется файл для секретных переменных?", ".env"),
    ("Куда отвечаем в VK: peer_id или from_id?", "peer_id"),
]
GAMES = {}


def start_game(user_id):
    game = GAMES.get(user_id)
    if game is None:
        GAMES[user_id] = game = {"step": 0, "score": 0}
    return QUESTIONS[game["step"]][0]


def answer_quiz(user_id, text):
    game = GAMES.get(user_id)
    if game is None:
        return "⚠️ Сначала запустите викторину.\nИспользуйте команды:\n" + ", ".join(START_COMMANDS)

    if not text:
        return QUESTIONS[game["step"]][0]

    question, right_answer = QUESTIONS[game["step"]]
    if text == right_answer:
        game["score"] += 1

    game["step"] += 1
    if game["step"] >= len(QUESTIONS):
        score = game["score"]
        del GAMES[user_id]
        return f"🏆 Игра окончена. Счёт: {score}/{len(QUESTIONS)}"

    return QUESTIONS[game["step"]][0]


def main():
    session = vk_api.VkApi(token=TOKEN)
    vk = session.get_api()
    long_poll = VkBotLongPoll(session, GROUP_ID)

    for event in long_poll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            run(vk, event)


def welcome() -> str:
    return (f"'Викторина'\n"
            f"Чтобы начать викторину используйте команды:\n"
            f"{', '.join(START_COMMANDS)}\n"
            f"Для выхода:\n"
            f"{', '.join(EXIT_COMMAND)}")


def run(vk, event, keyboard=None) -> bool:
    message = event.object.message
    text = message.get("text", "").strip().lower()
    from_id = message["from_id"]
    if text in START_COMMANDS:
        answer = start_game(from_id)
    elif text in EXIT_COMMAND:
        GAMES.pop(from_id, None)
        return True
    else:
        answer = answer_quiz(from_id, text)
    send_message(vk, message["peer_id"], answer)
    return "Игра окончена" in answer


if __name__ == "__main__":
    print('victorina started...')
    print(f"Token {'found' if TOKEN else 'not found'}")
    print(f"Token {'correct' if len(TOKEN) > 100 else 'incorrect'}")
    print(f"Group ID {GROUP_ID}")
    main()
