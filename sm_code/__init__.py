from .victorina import run as victorina_run, welcome as victorina_welcome
from .media_bot import run as media_run, welcome as media_welcome
from .notes import run as notes_run, welcome as notes_welcome

MODULES_NAME = (
    "Викторина",
    "Медиа",
    "Заметки"
)

MODULES = {
    'викторина': victorina_run,
    'медиа': media_run,
    'заметки': notes_run
}

WELCOME = {
    'викторина': victorina_welcome,
    'медиа': media_welcome,
    'заметки': notes_welcome
}
