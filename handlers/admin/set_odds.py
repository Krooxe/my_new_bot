"""
Обработчик кнопки "Ввести/изменить коэффициенты"
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "admin_set_odds")
async def admin_set_odds_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Ввести/изменить коэффициенты"
    """
    logger.info(f"Администратор {callback.from_user.id} нажал 'Ввести/изменить коэффициенты'")
    
    await callback.answer(
        "Функция 'Ввести/изменить коэффициенты' в разработке.\n"
        "Здесь можно будет установить коэффициенты на каждый бой.",
        show_alert=True
    )