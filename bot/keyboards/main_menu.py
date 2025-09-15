from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🎮 Пополнить Steam по логину")],
        [KeyboardButton(text="🎁 Получить 50 рублей на первую покупку")],
        [KeyboardButton(text="⭐ Отзывы"), KeyboardButton(text="❓ FAQ")],
        [KeyboardButton(text="🔒 Гарантии"), KeyboardButton(text="👤 Личный кабинет")],
        [KeyboardButton(text="💬 Поддержка"), KeyboardButton(text="🛍️ Другие товары")],
        [KeyboardButton(text="🔥 АКТУАЛЬНЫЕ СКИДКИ В STEAM")],
        [KeyboardButton(text="📢 Telegram-канал"), KeyboardButton(text="🌐 Наш сайт")],
    ]
    # Кнопка только для админов
    if is_admin:
        keyboard.append([KeyboardButton(text="🛠 Админ-панель")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
