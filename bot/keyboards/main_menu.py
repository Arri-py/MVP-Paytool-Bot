from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пополнить Steam по логину")],
        [KeyboardButton(text="Получить 50 рублей на первую покупку")],
        [KeyboardButton(text="Отзывы"), KeyboardButton(text="FAQ")],
        [KeyboardButton(text="Гарантии"), KeyboardButton(text="Личный кабинет")],
        [KeyboardButton(text="Поддержка"), KeyboardButton(text="Другие товары")],
        [KeyboardButton(text="АКТУАЛЬНЫЕ СКИДКИ В STEAM")],
        [KeyboardButton(text="Telegram-канал"), KeyboardButton(text="Наш сайт")],
    ],
    resize_keyboard=True
)
