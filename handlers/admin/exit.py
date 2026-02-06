"""
Обработчик кнопки "Выход" из админ-панели
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from handlers.start import main_menu  # Импортируем главное меню

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "admin_exit")
async def admin_exit_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Выход" - возвращает в главное меню
    """
    user = callback.from_user
    logger.info(f"Администратор {user.id} вышел из админ-панели")
    
    # Сначала удаляем админ-сообщение
    await callback.message.delete()
    
    # Затем показываем главное меню
    await callback.message.answer(
        f"👋 Вы вышли из админ-панели, {user.first_name}!\n\nВыберите действие:",
        reply_markup=main_menu()  # Используем главное меню из start.py
    )
    
    await callback.answer()