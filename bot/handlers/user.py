from aiogram import Router, types, F
from bot.keyboards.faq_menu import faq_kb
from bot.keyboards.guarantees_menu import guarantees_kb
from bot.keyboards.main_menu import main_menu
from bot.config import redis

router = Router()

BONUS_KEY = "bonus:{user_id}"

# 🎁 Получить бонус
@router.message(F.text == "Получить 50 рублей на первую покупку")
async def get_bonus(message: types.Message):
    key = BONUS_KEY.format(user_id=message.from_user.id)
    if await redis.exists(key):
        await message.answer("❌ Вы уже получали бонус или совершали покупки.")
    else:
        await redis.set(key, "1")
        await message.answer("✅ Вы получили +50 рублей на первую покупку!")

# 📌 Отзывы
@router.message(F.text == "Отзывы")
async def reviews(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Отзывы в тг-канале", url="https://t.me/reviews_zadonatit_ru")],
        [types.InlineKeyboardButton(text="Отзывы на 2ГИС", url="https://2gis.ru/novosibirsk/firm/70000001088741377/tab/reviews")],
        [types.InlineKeyboardButton(text="Отзывы на Яндекс.Карты", url="https://yandex.ru/profile/104133210284")],
        [types.InlineKeyboardButton(text="Отзывы на Отзовик.com", url="https://otzovik.com/reviews/paytool_ru-servis_pokupki_kart_apple/")],
        [types.InlineKeyboardButton(text="На главный экран", callback_data="to_main")]
    ])
    await message.answer("Отзывы наших клиентов 📢", reply_markup=kb)

# ❓ FAQ
@router.message(F.text == "FAQ")
async def faq(message: types.Message):
    text = (
        "Здесь собраны инструкции и ответы на самые частые вопросы — чтобы вы могли легко разобраться.\n\n"
        "Если что-то осталось непонятным — не переживайте.\n"
        "Вы всегда можете написать в поддержку 👉 https://t.me/zadonatitru_support"
    )
    await message.answer(text, reply_markup=faq_kb, disable_web_page_preview=True)

# 🔒 Гарантии
@router.message(F.text == "Гарантии")
async def guarantees(message: types.Message):
    text = (
        "Гарантии качества и безопасности от Задонатить.ру\n\n"
        "65 000+ клиентов\n188 976+ успешных пополнений\n13 943+ положительных отзывов\n\n"
        "Юридическая прозрачность\n"
        "Название: ТОО 'PAYTECH CORP (ПЭЙТЕХ КОРП)'\nБИН: 250440032449\n"
        "Адрес: Астана, Кенесары 65, кв. 47\n\n"
        "Круглосуточная поддержка 👉 https://t.me/zadonatitru_support"
    )
    await message.answer(text, reply_markup=guarantees_kb, disable_web_page_preview=True)

# ℹ️ Callback для возврата на главную
@router.callback_query(F.data == "to_main")
async def to_main(cb: types.CallbackQuery):
    await cb.message.answer("Главное меню:", reply_markup=main_menu)
    await cb.answer()

# 🏢 Офис компании
@router.callback_query(F.data == "company_office")
async def office(cb: types.CallbackQuery):
    text = (
        "Офис компании Задонатить.ру находится по адресу:\n\n"
        "🏢 Россия, г. Новосибирск, ул. Титова 22а, офис 604\n\n"
        "В данном офисе работает наша команда."
    )
    await cb.message.answer(text)
    await cb.answer()
