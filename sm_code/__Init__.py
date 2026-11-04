# Ручной словарь для красивых названий
from importlib import import_module

MODULES_NAME = {
    "Викторина": "victorina",
    "Медиа": "media_bot"
}

# Динамически загружаем функции run из указанных модулей
MODULES = {name.lower(): import_module(f'sm_code.{module_name}').run
           for name, module_name in MODULES_NAME.items()}

# Динамически загружаем функции welcome из указанных модулей
WELCOME = {name.lower(): import_module(f'sm_code.{module_name}').welcome
           for name, module_name in MODULES_NAME.items()}
