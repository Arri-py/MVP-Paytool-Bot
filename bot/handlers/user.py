from aiogram import Router, types, F
from bot.keyboards.faq_menu import faq_kb
from bot.keyboards.guarantees_menu import guarantees_kb
from bot.keyboards.main_menu import main_menu
from bot.keyboards.back_menu import back_kb
from bot.keyboards.regions_kb import regions_kb
from aiogram.types import FSInputFile
from bot.services.redis_service import (
    get_user_purchases,
    get_user_donates,
    has_received_bonus,
    mark_bonus_received,
    add_donates
)

router = Router()

MAIN_MENU_TEXT = (
    "🏠 Главное меню Задонатить.ру\n\n"
    "🎮 Пополнение Steam — быстро и безопасно\n"
    "🎁 Бонусы — получайте кэшбек за каждую покупку\n"
    "⭐️ Отзывы — мнения тысяч довольных клиентов\n"
    "🔒 Гарантии — юридическая защита и надежность\n\n"
    "💬 Поддержка 24/7 — всегда готовы помочь!\n"
    "🛍️ Широкий ассортимент — не только Steam"
)


# --------- бонус ----------
@router.message(F.text == "🎁 Получить 50 рублей на первую покупку")
async def get_bonus(message: types.Message):
    user_id = message.from_user.id
    # если уже получал бонус
    if await has_received_bonus(user_id):
        await message.answer("❌ Вы уже получали бонус или совершали покупки.")
        return
    # выдать бонус
    try:
        await mark_bonus_received(user_id)
        await add_donates(user_id, 50)
        await message.answer("✅ Вы получили +50 рублей на первую покупку!")
    except Exception as e:
        print("Ошибка выдачи бонуса:", e)
        await message.answer("Произошла ошибка при выдаче бонуса — повторите позже.")


# --------- Личный кабинет ----------
@router.message(F.text == "👤 Личный кабинет")
async def personal_account(message: types.Message):
    user = message.from_user
    try:
        purchases = await get_user_purchases(user.id)
        donates = await get_user_donates(user.id)
    except Exception as e:
        print("Redis read error in personal_account:", e)
        purchases = 0
        donates = 0

    text = (
        f"{user.first_name}, добро пожаловать в Личный кабинет Задонатить.ру!\n\n"
        f"📦 Всего покупок: {purchases}\n"
        f"🍩 Баланс в Донатах: {donates}\n\n"
        "Что такое Донаты?\n\n"
        "Донаты — это внутренняя валюта нашего сервиса. За каждую покупку вы получаете кэшбек 0,5% в Донатах 🍩\n\n"
        "1 Донат = 1 рубль\n\n"
        "Вы можете оплатить до 99,99% от суммы заказа Донатами (минимум 1 ₽ — оплачивается вручную)\n\n"
        "Минимальная сумма заказа для использования Донатов — 1000 ₽\n\n"
        "Если нужен перенос баланса — напишите в поддержку: https://t.me/zadonatitru_support"
    )

    await message.answer(text, reply_markup=back_kb, disable_web_page_preview=True)


# --------- Пополнение Steam / регионы ----------
@router.message(F.text == "🎮 Пополнить Steam по логину")
async def choose_region(message: types.Message):
    await message.answer("Выберите регион вашего аккаунта:", reply_markup=regions_kb)


@router.message(F.text == "ℹ️ Как узнать регион")
async def how_to_find_region(message: types.Message):
    text = (
        "Как узнать регион аккаунта?\n\n"
        "💻 На ПК:\n"
        "1. Откройте приложение Steam\n"
        "2. В правом верхнем углу нажмите на свой никнейм\n"
        "3. Перейдите в раздел «Об аккаунте»\n"
        "4. В строке «Страна» вы увидите регион вашего аккаунта\n\n"
        "📱 На мобильном устройстве:\n"
        "1. Откройте приложение Steam\n"
        "2. Перейдите в раздел Меню → Настройки\n"
        "3. Выберите «Информация об аккаунте»\n"
        "4. В строке «Страна» отображается регион вашего аккаунта"
    )
    try:
        photo = FSInputFile("img/replenishment.jpg")
        await message.answer_photo(photo, caption=text, reply_markup=back_kb)
    except Exception as e:
        print("Replenishment photo error:", e)
        await message.answer(text, reply_markup=back_kb)



# --------- Отзывы (с картинкой) ----------
@router.message(F.text == "⭐ Отзывы")
async def reviews(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Отзывы в тг-канале", url="https://t.me/reviews_zadonatit_ru")],
        [types.InlineKeyboardButton(text="Отзывы на 2ГИС", url="https://2gis.ru/novosibirsk/firm/70000001088741377/tab/reviews")],
        [types.InlineKeyboardButton(text="Отзывы на Яндекс.Карты", url="https://yandex.ru/profile/104133210284")],
        [types.InlineKeyboardButton(text="Отзывы на Отзовик.com", url="https://otzovik.com/reviews/paytool_ru-servis_pokupki_kart_apple/")]
    ])
    try:
        photo = FSInputFile("img/reviews.jpg")
        await message.answer_photo(photo, caption="Отзывы наших клиентов 📢", reply_markup=kb)
    except Exception as e:
        print("Reviews photo error:", e)
        await message.answer("Отзывы наших клиентов 📢", reply_markup=kb)



# --------- Гарантии ----------
@router.message(F.text == "🔒 Гарантии")
async def guarantees(message: types.Message):
    text = (
        "🔒 Гарантии качества и безопасности от Задонатить.ру\n\n"
        "📊 65 000+ клиентов\n✅ 188 976+ успешных пополнений\n⭐ 13 943+ положительных отзывов\n\n"
        "🏢 Юридическая прозрачность:\n"
        "• Название: ТОО 'PAYTECH CORP (ПЭЙТЕХ КОРП)'\n"
        "• БИН: 250440032449\n"
        "• Адрес: Астана, Кенесары 65, кв. 47\n\n"
        "💬 Круглосуточная поддержка 👉 https://t.me/zadonatitru_support"
    )
    await message.answer(text, reply_markup=guarantees_kb, disable_web_page_preview=True)


# --------- FAQ (без кнопки "На главную") ----------
@router.message(F.text == "❓ FAQ")
async def faq(message: types.Message):
    text = (
        "❓ Часто задаваемые вопросы\n\n"
        "Здесь собраны инструкции и ответы на самые частые вопросы — чтобы вы могли легко разобраться.\n\n"
        "Если что-то осталось непонятным — не переживайте!\n"
        "Вы всегда можете написать в поддержку 👉 https://t.me/zadonatitru_support"
    )
    await message.answer(text, reply_markup=faq_kb, disable_web_page_preview=True)


# --------- Поддержка ----------
@router.message(F.text == "💬 Поддержка")
async def support(message: types.Message):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Написать в поддержку", url="https://t.me/zadonatitru_support")]]
    )
    await message.answer("Нужна помощь? Свяжитесь с нашей поддержкой:", reply_markup=kb)


# --------- Другие товары ----------
@router.message(F.text == "🛍️ Другие товары")
async def other_products(message: types.Message):
    text = (
        "Задонатить.ру — это часть проекта Paytool, где мы специализируемся на пополнении Steam\n\n"
        "Удобная оплата, низкая комиссия и всё в одном месте\n\n"
        "Хочешь узнать больше? Переходи в @paytool_hub_bot или на сайт https://paytool.ru/"
    )
    await message.answer(text, disable_web_page_preview=True, reply_markup=back_kb)


# --------- Скидки (ссылка) ----------
@router.message(F.text == "🔥 АКТУАЛЬНЫЕ СКИДКИ В STEAM")
async def steam_discounts(message: types.Message):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Открыть скидки 🎮", url="https://store.steampowered.com/search/?os=win&specials=1&filter=topsellers&ndl=")]]
    )
    await message.answer("🔥 Актуальные скидки в Steam:", reply_markup=kb)


# --------- Канал и сайт ----------
@router.message(F.text == "📢 Telegram-канал")
async def telegram_channel(message: types.Message):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Наш канал 📢", url="https://t.me/zadonatit_ru")]]
    )
    await message.answer("Подпишись на наш Telegram-канал:", reply_markup=kb)


@router.message(F.text == "🌐 Наш сайт")
async def website(message: types.Message):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="🌐 Перейти на сайт", url="https://zadonatit.ru/")]]
    )
    await message.answer("Наш официальный сайт:", reply_markup=kb)


# --------- Callbacks и возврат на главное ----------
@router.callback_query(F.data == "to_main")
async def cb_to_main(cb: types.CallbackQuery):
    await cb.message.answer(MAIN_MENU_TEXT, reply_markup=main_menu)
    await cb.answer()


@router.callback_query(F.data == "company_office")
async def cb_office(cb: types.CallbackQuery):
    text = (
        "🏢 Офис компании Задонатить.ру\n\n"
        "📍 Адрес: Россия, г. Новосибирск, ул. Титова 22а, офис 604\n\n"
        "🕒 Время работы: Пн-Пт 10:00-18:00\n\n"
        "В данном офисе работает наша команда специалистов."
    )
    await cb.message.answer(text)
    await cb.answer()


# --------- Кнопка "⬅️ Назад" ----------
@router.message(F.text == "⬅️ Назад")
async def back_to_main(message: types.Message):
    await message.answer(MAIN_MENU_TEXT, reply_markup=main_menu)
