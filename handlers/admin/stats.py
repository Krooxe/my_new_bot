"""
Обработчик кнопки "Статистика"
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Статистика"
    """
    logger.info(f"Администратор {callback.from_user.id} нажал 'Статистика'")
    
    await callback.message.answer("Вы нажали на кнопку <b>Статистика</b>", parse_mode="HTML")
    await callback.answer()