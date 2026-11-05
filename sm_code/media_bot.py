import os

import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from config import EXIT_COMMAND
from vk_sender import send_message

load_dotenv()
TOKEN = os.getenv("VK_GROUP_TOKEN")
GROUP_ID = int(os.getenv("VK_GROUP_ID", "0"))
PHOTO_ATTACHMENT = os.getenv("VK_PHOTO_ATTACHMENT", "photo-242585981_457239018")
VIDEO_ATTACHMENT = os.getenv("VK_VIDEO_ATTACHMENT", "video-242585981_456239018")

USERS = {}


def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    long_poll = VkBotLongPoll(vk_session, GROUP_ID, wait=0)

    for event in long_poll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            run(vk, event)


def welcome() -> str:
    return (f"'Медиа'\n"
            f"Чтобы получить медиа используйте команды 'фото' или 'видео'\n"
            f"Для выхода можете использовать: {', '.join(EXIT_COMMAND)}")


def run(vk, event, keyboard=None) -> bool:
    message = event.object.message
    text = message.get("text", "").strip().lower()
    if text == "фото":
        if PHOTO_ATTACHMENT:
            send_message(vk, message["peer_id"], "📸 Вот вам фоточка", attachment=PHOTO_ATTACHMENT, keyboard=keyboard)
        else:
            send_message(vk, message["peer_id"], "Добавьте VK_PHOTO_ATTACHMENT=photoOWNER_ID_MEDIA_ID в .env")
    elif text == "видео":
        if VIDEO_ATTACHMENT:
            send_message(vk, message["peer_id"], "🎥 Вот вам видео", attachment=VIDEO_ATTACHMENT, keyboard=keyboard)
        else:
            send_message(vk, message["peer_id"], "Добавьте VK_VIDEO_ATTACHMENT=videoOWNER_ID_MEDIA_ID в .env")
    elif text in EXIT_COMMAND:
        return True
    else:
        send_message(vk,
                     message["peer_id"],
                     f"⚠️ Команды: фото, видео\nДля выхода: {', '.join(EXIT_COMMAND)}",
                     keyboard=keyboard)
    return False


if __name__ == "__main__":
    print('media_bot started...')
    print(f"Token {'found' if TOKEN else 'not found'}")
    print(f"Token {'correct' if TOKEN.startswith("vk1.a.") and len(TOKEN) > 100 else 'incorrect'}")
    print(f"Group ID {GROUP_ID}")
    print(f"P: {PHOTO_ATTACHMENT}")
    print(f"V: {VIDEO_ATTACHMENT}")
    main()
