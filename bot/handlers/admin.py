from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.config import Config
from bot.services.redis_service import set_welcome_text, get_user_count
from bot.keyboards.admin_kb import admin_menu
from bot.keyboards.main_menu import get_main_menu

router = Router()

# --- Состояния для редактирования текста ---
class AdminStates(StatesGroup):
    waiting_for_welcome_text = State()


# --- Вход в админ-панель ---
@router.message(F.text == "🛠 Админ-панель")
async def open_admin_panel(message: types.Message):
    if message.from_user.id not in Config.ADMIN_CACHE:
        return await message.answer("⛔ У вас нет доступа.")
    await message.answer("🛠 Админ-панель", reply_markup=admin_menu)


# --- Кнопка возврата в главное ---
@router.message(F.text == "🏠 Главное меню")
async def back_to_main_from_admin(message: types.Message):
    is_admin = message.from_user.id in Config.ADMIN_CACHE
    await message.answer("Возврат в главное меню", reply_markup=get_main_menu(is_admin))


# --- Редактирование приветственного текста ---
@router.message(F.text == "✏️ Редактировать приветственный текст")
async def ask_new_welcome(message: types.Message, state: FSMContext):
    if message.from_user.id not in Config.ADMIN_CACHE:
        return await message.answer("⛔ У вас нет доступа.")
    await state.set_state(AdminStates.waiting_for_welcome_text)
    await message.answer("✏️ Введите новый приветственный текст:")


@router.message(AdminStates.waiting_for_welcome_text)
async def save_new_welcome(message: types.Message, state: FSMContext):
    if message.from_user.id not in Config.ADMIN_CACHE:
        return await message.answer("⛔ У вас нет доступа.")

    new_text = message.text.strip()
    if not new_text:
        return await message.answer("❌ Текст не может быть пустым. Попробуйте снова:")

    await set_welcome_text(new_text)
    await state.clear()
    await message.answer("✅ Приветственный текст обновлён!", reply_markup=admin_menu)


# --- Статистика ---
@router.message(F.text == "📊 Статистика")
async def stats_cmd(message: types.Message):
    if message.from_user.id not in Config.ADMIN_CACHE:
        return await message.answer("⛔ У вас нет доступа.")
    count = await get_user_count()
    await message.answer(f"📊 Статистика бота:\n👥 Пользователей: {count}")
