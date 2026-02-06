"""
Обработчик кнопки "Завершить текущий PPV"
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "admin_finish_ppv")
async def admin_finish_ppv_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Завершить текущий PPV"
    """
    logger.info(f"Администратор {callback.from_user.id} нажал 'Завершить текущий PPV'")
    
    await callback.answer(
        "Функция 'Завершить текущий PPV' в разработке.\n"
        "Здесь будет подведение итогов и распределение призов.",
        show_alert=True
    )