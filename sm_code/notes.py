import os
import sqlite3

import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from config import EXIT_COMMAND
from vk_sender import send_message

load_dotenv()
TOKEN = os.getenv("VK_GROUP_TOKEN")
GROUP_ID = int(os.getenv("VK_GROUP_ID", "0"))
DB_PATH = "notes.sqlite3"

LOCAL_COMMAND = "Команда: 'Заметка <текст>', 'Мои заметки', 'Удалить'"

def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT)"
        )


def add_note(user_id, text):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("INSERT INTO notes(user_id, text) VALUES (?, ?)", (user_id, text))
        connection.commit()


def list_notes(user_id):
    with (sqlite3.connect(DB_PATH) as connection):
        rows = connection.execute(
            "SELECT text FROM notes WHERE user_id= ? ORDER BY id DESC LIMIT 5", (user_id,)
        ).fetchall()
    return "\n".join(f"{index + 1}. {row[0]}" for index, row in enumerate(rows)) or "Заметок нет"


def del_notes(user_id):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
        connection.commit()


def main():
    init_db()
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    long_poll = VkBotLongPoll(vk_session, GROUP_ID)

    for event in long_poll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            run(vk, event)


def welcome() -> str:
    return (f"'Заметки'\n"
            f"{LOCAL_COMMAND}\n"
            f"Для выхода:\n"
            f"{', '.join(EXIT_COMMAND)}")


def run(vk, event, keyboard=None) -> bool:
    message = event.object.message
    text = message.get("text", "").strip()
    if text in EXIT_COMMAND:
        return True
    user_id = message["from_id"]
    if text.lower().startswith("заметка "):
        add_note(user_id, text[8:])
        answer = "Заметка сохранена"
    elif text.lower() == "мои заметки":
        answer = list_notes(user_id)
    elif text.lower() == "удалить":
        del_notes(user_id)
        answer = "Заметки удалены"
    else:
        answer = LOCAL_COMMAND
    send_message(vk, user_id, answer)
    return False


if __name__ == "__main__":
    print('notes started...')
    print(f"Token {'found' if TOKEN else 'not found'}")
    # print(f"Token {'correct' if TOKEN.startswith("vk1.a.") and len(TOKEN) > 100 else 'incorrect'}")
    print(f"Group ID {GROUP_ID}")
    main()
