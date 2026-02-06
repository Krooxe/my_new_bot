"""
Главная админ-панель и команда /admin
"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMIN_ID
from utils.json_storage import storage

logger = logging.getLogger(__name__)
router = Router()


def get_admin_menu() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру админского меню в зависимости от наличия активного турнира
    """
    current_tournament = storage.get_current_tournament()
    has_active_tournament = bool(current_tournament and current_tournament.get("status") == "active")
    
    keyboard_buttons = []
    
    if has_active_tournament:
        keyboard_buttons = [
            [InlineKeyboardButton(text="🛑 Завершить текущий PPV", callback_data="admin_finish_ppv")],
            [InlineKeyboardButton(text="📊 Ввести/изменить коэффициенты", callback_data="admin_set_odds")],
            [InlineKeyboardButton(text="📈 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 Объявление", callback_data="admin_announcement")],
            [InlineKeyboardButton(text="🚪 Выход", callback_data="admin_exit")]
        ]
    else:
        keyboard_buttons = [
            [InlineKeyboardButton(text="➕ Новый PPV", callback_data="admin_new_ppv")],
            [InlineKeyboardButton(text="📈 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 Объявление", callback_data="admin_announcement")],
            [InlineKeyboardButton(text="🚪 Выход", callback_data="admin_exit")]
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_admin_message_text(has_active_tournament: bool) -> str:
    """
    Возвращает текст сообщения админ-панели
    """
    if has_active_tournament:
        current_tournament = storage.get_current_tournament()
        tournament_info = (
            f"\n\n🏆 <b>Текущий PPV:</b>\n"
            f"{current_tournament.get('name', 'Неизвестно')}\n"
            f"📅 {current_tournament.get('date', 'Дата не указана')}\n"
            f"📍 {current_tournament.get('location', 'Место не указано')}\n"
            f"🥊 Боев: {len(current_tournament.get('fights', []))}"
        )
    else:
        tournament_info = "\n\nℹ️ <b>Нет активного PPV турнира</b>"
    
    return f"🔧 <b>Админ-панель</b>{tournament_info}\n\nВыберите действие:"


@router.message(Command("admin"))
async def admin_panel_handler(message: Message):
    """
    Обработчик команды /admin
    """
    user = message.from_user

    if user.id != ADMIN_ID:
        logger.warning(f"Попытка доступа к админ-панели от пользователя {user.id} ({user.username})")
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    logger.info(f"Администратор {user.username} (ID: {user.id}) зашел в админ-панель")
    
    current_tournament = storage.get_current_tournament()
    has_active_tournament = bool(current_tournament and current_tournament.get("status") == "active")
    
    message_text = get_admin_message_text(has_active_tournament)
    keyboard = get_admin_menu()
    
    await message.answer(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )