"""
Обработчики для админ-панели
"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from config import ADMIN_ID

logger = logging.getLogger(__name__)
router = Router()


def admin_menu() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру админского меню
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Новый PPV", callback_data="admin_new_ppv")],
        [InlineKeyboardButton(text="Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="Объявление", callback_data="admin_announcement")],
        [InlineKeyboardButton(text="Выход", callback_data="admin_exit")]
    ])
    return keyboard


@router.message(Command("admin"))
async def admin_panel_handler(message: Message):
    """
    Обработчик команды /admin
    Доступен только для администратора
    """
    user = message.from_user
    
    # Проверка прав администратора
    if user.id != ADMIN_ID:
        logger.warning(f"Попытка доступа к админ-панели от пользователя {user.id} ({user.username})")
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    logger.info(f"Администратор {user.username} (ID: {user.id}) зашел в админ-панель")
    
    await message.answer(
        "🔧 <b>Админ-панель</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )


@router.callback_query(lambda c: c.data == "admin_new_ppv")
async def admin_new_ppv_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Новый PPV"
    """
    logger.info(f"Администратор {callback.from_user.id} нажал 'Новый PPV'")
    
    await callback.message.answer("Вы нажали на кнопку <b>Новый PPV</b>", parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Статистика"
    """
    logger.info(f"Администратор {callback.from_user.id} нажал 'Статистика'")
    
    await callback.message.answer("Вы нажали на кнопку <b>Статистика</b>", parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_announcement")
async def admin_announcement_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Объявление"
    """
    logger.info(f"Администратор {callback.from_user.id} нажал 'Объявление'")
    
    await callback.message.answer("Вы нажали на кнопку <b>Объявление</b>", parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_exit")
async def admin_exit_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Выход"
    """
    logger.info(f"Администратор {callback.from_user.id} вышел из админ-панели")
    
    await callback.message.answer("👋 Вы вышли из админ-панели")
    await callback.answer()