from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать приветственный текст")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True
)
