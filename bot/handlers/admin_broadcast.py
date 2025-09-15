from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo, FSInputFile
from datetime import datetime, timezone
from bot.config import Config, bot
from bot.keyboards.admin_kb import admin_menu, audience_kb, campaign_type_kb
from bot.services.redis_service import (
    create_campaign, list_campaigns, get_campaign, get_campaign_stats, update_campaign_status,
    filter_users, incr_campaign_stat, set_campaign_started, set_campaign_finished
)

router = Router()

class CampaignStates(StatesGroup):
    title = State()
    text = State()
    media_choice = State()
    waiting_media = State()
    button = State()
    audience = State()
    audience_extra = State()
    type_choice = State()
    schedule_time = State()
    confirm = State()

@router.message(F.text == "📣 Создать рассылку")
async def start_campaign(message: types.Message, state: FSMContext):
    if message.from_user.id not in Config.ADMIN_CACHE:
        return await message.answer("⛔ У вас нет доступа.")
    await state.clear()
    await state.set_state(CampaignStates.title)
    await message.answer("📝 Введите *Название рассылки* (для внутреннего использования):", parse_mode=None)

@router.message(CampaignStates.title)
async def set_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(CampaignStates.text)
    await message.answer("✍️ Введите *текст рассылки* (поддерживает эмодзи и HTML).", parse_mode=None)

@router.message(CampaignStates.text)
async def set_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.html_text or message.text)
    await state.set_state(CampaignStates.media_choice)
    await message.answer(
        "📎 Приложить медиа?\n— Отправьте фото / видео / документ\n— или напишите «Без медиа»",
        parse_mode=None
    )

@router.message(CampaignStates.media_choice, F.text.casefold() == "без медиа")
async def no_media(message: types.Message, state: FSMContext):
    await state.update_data(media_type="", file_id="")
    await state.set_state(CampaignStates.button)
    await message.answer("🔗 Нужна кнопка?\nОтправьте в формате: `Текст кнопки | https://url`\nИли напишите «Без кнопки»", parse_mode="Markdown")

@router.message(CampaignStates.media_choice, F.photo)
async def got_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(media_type="photo", file_id=file_id)
    await state.set_state(CampaignStates.button)
    await message.answer("🔗 Нужна кнопка?\nОтправьте в формате: `Текст кнопки | https://url`\nИли напишите «Без кнопки»", parse_mode="Markdown")

@router.message(CampaignStates.media_choice, F.video)
async def got_video(message: types.Message, state: FSMContext):
    file_id = message.video.file_id
    await state.update_data(media_type="video", file_id=file_id)
    await state.set_state(CampaignStates.button)
    await message.answer("🔗 Нужна кнопка?\nОтправьте в формате: `Текст кнопки | https://url`\nИли напишите «Без кнопки»", parse_mode="Markdown")

@router.message(CampaignStates.media_choice, F.document)
async def got_doc(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    await state.update_data(media_type="document", file_id=file_id)
    await state.set_state(CampaignStates.button)
    await message.answer("🔗 Нужна кнопка?\nОтправьте в формате: `Текст кнопки | https://url`\nИли напишите «Без кнопки»", parse_mode="Markdown")

@router.message(CampaignStates.button, F.text.regexp(r"(?i)^без кнопки$"))
async def no_button(message: types.Message, state: FSMContext):
    await state.update_data(button_text="", button_url="")
    await state.set_state(CampaignStates.audience)
    await message.answer("👥 Выберите сегмент аудитории:", reply_markup=audience_kb())

@router.message(CampaignStates.button)
async def set_button(message: types.Message, state: FSMContext):
    parts = [p.strip() for p in message.text.split("|", maxsplit=1)]
    if len(parts) != 2 or not parts[0] or not parts[1].startswith("http"):
        return await message.answer("❌ Формат некорректный. Пример: `Купить со скидкой | https://example.com`", parse_mode="Markdown")
    await state.update_data(button_text=parts[0], button_url=parts[1])
    await state.set_state(CampaignStates.audience)
    await message.answer("👥 Выберите сегмент аудитории:", reply_markup=audience_kb())

@router.message(CampaignStates.audience, F.text == "⬅️ Отмена")
async def cancel_campaign(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Создание рассылки отменено.", reply_markup=admin_menu)

@router.message(CampaignStates.audience)
async def choose_audience(message: types.Message, state: FSMContext):
    t = message.text

    if t == "Все пользователи":
        await state.update_data(audience={"kind": "all"})
        await state.set_state(CampaignStates.type_choice)
        return await message.answer("🧭 Выберите тип рассылки:", reply_markup=campaign_type_kb())

    if t == "Новые пользователи":
        await state.update_data(audience={"kind": "new"})
        await state.set_state(CampaignStates.type_choice)
        return await message.answer("🧭 Выберите тип рассылки:", reply_markup=campaign_type_kb())

    if t == "Есть покупки":
        await state.update_data(audience={"kind": "has_purchases"})
        await state.set_state(CampaignStates.type_choice)
        return await message.answer("🧭 Выберите тип рассылки:", reply_markup=campaign_type_kb())

    if t == "Нет покупок":
        await state.update_data(audience={"kind": "no_purchases"})
        await state.set_state(CampaignStates.type_choice)
        return await message.answer("🧭 Выберите тип рассылки:", reply_markup=campaign_type_kb())

    if t in ("Покупали за 7 дней", "Покупали за 30 дней", "Покупали за 90 дней"):
        days = int(t.split()[2])  # 7/30/90
        await state.update_data(audience={"kind": "purchased_last_days", "days": days})
        await state.set_state(CampaignStates.type_choice)
        return await message.answer("🧭 Выберите тип рассылки:", reply_markup=campaign_type_kb())

    if t == "Открывали бота X дней":
        await state.set_state(CampaignStates.audience_extra)
        return await message.answer("Введите число дней (например: 14):")

    if t == "По списку ID":
        await state.set_state(CampaignStates.audience_extra)
        return await message.answer("Отправьте список ID через запятую: 123,456,789")

    await message.answer("Выберите вариант из меню 👆", reply_markup=audience_kb())

@router.message(CampaignStates.audience_extra)
async def audience_extra(message: types.Message, state: FSMContext):
    prev = (await state.get_data())
    await state.set_state(CampaignStates.type_choice)

    if message.text.replace(" ", "").isdigit():  # открывали X дней
        days = int(message.text)
        await state.update_data(audience={"kind": "opened_last_days", "days": days})
        return await message.answer("🧭 Выберите тип рассылки:", reply_markup=campaign_type_kb())
    else:
        try:
            ids = [int(x.strip()) for x in message.text.split(",") if x.strip().isdigit()]
            if not ids:
                raise ValueError
            await state.update_data(audience={"kind": "ids_list", "ids": ids})
            return await message.answer("🧭 Выберите тип рассылки:", reply_markup=campaign_type_kb())
        except Exception:
            return await message.answer("❌ Некорректный ввод. Введите число дней *или* список ID через запятую.")

@router.message(CampaignStates.type_choice, F.text == "⬅️ Отмена")
async def cancel_type(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Создание рассылки отменено.", reply_markup=admin_menu)

@router.message(CampaignStates.type_choice, F.text == "🚀 Отправить сейчас")
async def choose_now(message: types.Message, state: FSMContext):
    await state.update_data(send_type="now")
    await finalize_campaign(message, state)

@router.message(CampaignStates.type_choice, F.text == "⏰ Запланировать")
async def choose_schedule(message: types.Message, state: FSMContext):
    await state.update_data(send_type="scheduled")
    await state.set_state(CampaignStates.schedule_time)
    await message.answer("🗓 Введите дату и время в формате `YYYY-MM-DD HH:MM` по UTC.\nНапример: `2025-09-16 12:30`", parse_mode="Markdown")

@router.message(CampaignStates.schedule_time)
async def set_schedule_time(message: types.Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text.strip(), "%Y-%m-%d %H:%M")
        # сохраняем как ISO в UTC (тут считаем, что ввод уже в UTC)
        iso = dt.replace(tzinfo=timezone.utc).isoformat()
        await state.update_data(schedule_at=iso)
        await finalize_campaign(message, state)
    except Exception:
        await message.answer("❌ Неверный формат. Пример: `2025-12-31 23:59` (UTC)", parse_mode="Markdown")

async def finalize_campaign(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data.get("title","")
    text = data.get("text","")
    media_type = data.get("media_type","")
    file_id = data.get("file_id","")
    btn_text = data.get("button_text","")
    btn_url = data.get("button_url","")
    audience = data.get("audience", {"kind":"all"})
    send_type = data.get("send_type","now")
    schedule_at = data.get("schedule_at","")

    cid = await create_campaign({
        "title": title,
        "text": text,
        "media_type": media_type,
        "file_id": file_id,
        "button_text": btn_text,
        "button_url": btn_url,
        "audience": str(audience),  # строка простоты str
        "type": "scheduled" if send_type == "scheduled" else "now",
        "schedule_at": schedule_at,
        "created_by": str(message.from_user.id),
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    await state.clear()

    if send_type == "now":
        # Отмечаем как pending — обработает фон-джоб немедленно
        await update_campaign_status(cid, "pending")
        await message.answer(f"✅ Кампания #{cid} создана и поставлена в отправку.", reply_markup=admin_menu)
    else:
        await message.answer(f"✅ Кампания #{cid} запланирована на {schedule_at} (UTC).", reply_markup=admin_menu)

# --- История рассылок ---
@router.message(F.text == "🗂 История рассылок")
async def history(message: types.Message):
    if message.from_user.id not in Config.ADMIN_CACHE:
        return await message.answer("⛔ У вас нет доступа.")
    campaigns = await list_campaigns()
    if not campaigns:
        return await message.answer("Пока нет кампаний.", reply_markup=admin_menu)

    lines = []
    for c in campaigns[-20:]:
        cid = c.get("id")
        stats = await get_campaign_stats(cid)
        lines.append(
            f"#{cid} — {c.get('title','')}\n"
            f"Статус: {c.get('status')} | Тип: {c.get('type')} | Запланировано: {c.get('schedule_at','-')}\n"
            f"Отправлено: {stats.get('sent','0')} | Ошибок: {stats.get('failed','0')}"
        )
    await message.answer("🗂 Последние кампании:\n\n" + "\n\n".join(lines), reply_markup=admin_menu)
