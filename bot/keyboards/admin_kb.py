from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📣 Создать рассылку")],
        [KeyboardButton(text="🗂 История рассылок"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="✏️ Редактировать приветственный текст")],
        [KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True
)

# Клавиатура выбора типа сегментации
def audience_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Все пользователи")],
            [KeyboardButton(text="Новые пользователи")],
            [KeyboardButton(text="Есть покупки"), KeyboardButton(text="Нет покупок")],
            [KeyboardButton(text="Покупали за 7 дней"), KeyboardButton(text="Покупали за 30 дней")],
            [KeyboardButton(text="Покупали за 90 дней")],
            [KeyboardButton(text="Открывали бота X дней")],
            [KeyboardButton(text="По списку ID")],
            [KeyboardButton(text="⬅️ Отмена")],
        ],
        resize_keyboard=True
    )

# Клавиатура выбора типа рассылки
def campaign_type_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Отправить сейчас")],
            [KeyboardButton(text="⏰ Запланировать")],
            [KeyboardButton(text="⬅️ Отмена")],
        ],
        resize_keyboard=True
    )
