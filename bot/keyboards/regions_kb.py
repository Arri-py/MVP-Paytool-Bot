from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

regions_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇷🇺 Россия"), KeyboardButton(text="🇰🇿 Казахстан")],
        [KeyboardButton(text="🇧🇾 Республика Беларусь"), KeyboardButton(text="🇦🇿 Азербайджан")],
        [KeyboardButton(text="🇦🇲 Армения"), KeyboardButton(text="🇰🇬 Кыргызстан")],
        [KeyboardButton(text="🇹🇯 Таджикистан"), KeyboardButton(text="🇺🇿 Узбекистан")],
        [KeyboardButton(text="ℹ️ Как узнать регион")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)
