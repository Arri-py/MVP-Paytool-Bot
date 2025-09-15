from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

guarantees_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отзывы", url="https://t.me/reviews_zadonatit_ru")],
    [InlineKeyboardButton(text="Оферта", url="https://zadonatit.ru/offer")],
    [InlineKeyboardButton(text="Политика конфиденциальности", url="https://zadonatit.ru/privacy")],
    [InlineKeyboardButton(text="Пользовательское соглашение", url="https://zadonatit.ru/rules")],
    [InlineKeyboardButton(text="Офис нашей компании", callback_data="company_office")],
    [InlineKeyboardButton(text="Главная", callback_data="to_main")]
])
