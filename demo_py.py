import os

import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config import START_COMMANDS, EXIT_COMMAND
from vk_sender import send_message
from sm_code import MODULES, MODULES_NAME, WELCOME

load_dotenv()
TOKEN = os.getenv("VK_GROUP_TOKEN")
GROUP_ID = int(os.getenv("VK_GROUP_ID", "0"))

USERS = {}


def start_menu_keyboard():
    kb = VkKeyboard(one_time=False)
    for i, name in enumerate(MODULES_NAME):
        if i > 0 and i % 2 == 0:
            kb.add_line()
        kb.add_callback_button(name, color=VkKeyboardColor.PRIMARY, payload={"text": name})
    return kb.get_keyboard()


def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    long_poll = VkBotLongPoll(vk_session, GROUP_ID, wait=0)

    for event in long_poll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue
        message = event.obj.message
        text = message.get("text", "").strip().lower()
        user_id = message['from_id']
        user = USERS.get(user_id)
        peer_id = message["peer_id"]
        if user is None:
            if text in START_COMMANDS:
                USERS[user_id] = {'module': None}
                _send_message_select_block(vk, peer_id)
            else:
                answer = f"Чтобы начать, введите одну из команд:\n{', '.join(START_COMMANDS)}"
                send_message(vk, peer_id, answer)
        else:
            module = user['module']
            if module:
                if MODULES[module](vk, event):
                    user['module'] = None
                    _send_message_select_block(vk, peer_id)
            else:
                if text in MODULES:
                    user['module'] = text
                    send_message(vk, peer_id, f'Вы выбрали {WELCOME[text]()}')
                elif text in EXIT_COMMAND:
                    USERS.pop(user_id)
                    send_message(vk, peer_id, 'Пока-пока, приходите еще ❤️')
                else:
                    send_message(vk, peer_id, f"Попробуйте еще раз:\n{', '.join(MODULES_NAME.keys())}")


def _send_message_select_block(vk, peer_id):
    return send_message(
        vk, peer_id, f"Выберите блок:\n{', '.join(MODULES_NAME.keys())}", keyboard=start_menu_keyboard()
    )


if __name__ == "__main__":
    print('demo_py started...')
    print(f"Token {'found' if TOKEN else 'not found'}")
    print(f"Token {'correct' if TOKEN.startswith("vk1.a.") and len(TOKEN) > 100 else 'incorrect'}")
    print(f"Group ID {GROUP_ID}")
    main()
