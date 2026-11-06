import os
import random
import sqlite3

import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

load_dotenv()
TOKEN = os.getenv("VK_GROUP_TOKEN")
GROUP_ID = int(os.getenv("VK_GROUP_ID", "0"))
DB_PATH ="notes.sqlite3"

def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT)"
        )

def add_note(user_id, text):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("INTERNT INTO notes VALUES (?, ?)", (user_id, text))

def list_notes(user_id):
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("SELECT text FROM notes WHERE user_id= ? ORDER BY id DESC LIMIT 5", (user_id,)).fetchall()
    return "\n".join(f"(index + 1), {row[0]}" for index, row in enumerate(rows)) or "Заметок нет"

# TODO Сделать из кода модуль
#  - send_message - использовать общий
#  - сделать welcome() и выделить run(), не забыть про возврат bool
#
# TODO Исправить откровенные ошибки
#  - строка 22
#  - строка 27
#
# TODO Доработки (легкие)
#  Добавить 'логи' старта (по аналогии)
#  Добавить команду для выхода
#  Привести сообщения к одному языку, стандартному виду
#
# TODO Доработки (SQL)
#  В запросе добавления явно указать колонки для вставки
#  Добавить возможность удаления всех заметок
#  Добавить коммит после добавления (для корректности выполнения DML)

def send_message(vk, peer_id, text):
    vk.messages.send(peer_id=peer_id, message=text, random_id=random.randint(1, 2_147_483_647))


def main():
    init_db()
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.object.message
            text = message.get("text", "").strip()
            if text.lower().startswith("заметка "):
                add_note(message["from_id"], text[8:])
                answer = "Заметка is save."
            elif text.lower() == "мои заметки":
                answer = list_notes(message["from_id"])
            else:
                answer = "Команда: заметка купить тетрадь, мои заметки"
            send_message(vk, message["from_id"], answer)

if __name__ == "__main__":
    main()