import random

MAX_MESSAGE_LENGTH = 3500
MAX_RANDOM_ID = 2_147_483_647


def send_message(vk, peer_id, text, attachment=None, keyboard=None):
    params = {"peer_id": peer_id,
              "message": text[:MAX_MESSAGE_LENGTH],
              "random_id": random.randint(1, MAX_RANDOM_ID)
              }
    if attachment:
        params["attachment"] = attachment
    if keyboard:
        params["keyboard"] = keyboard
    vk.messages.send(**params)
