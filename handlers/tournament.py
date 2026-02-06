"""
Обработчики для текущего турнира
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "current_tournament")
async def current_tournament_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Текущий турнир"
    """
    logger.info(f"Пользователь {callback.from_user.id} запросил текущий турнир")
    
    # TODO: Здесь будет логика отображения текущего турнира
    await callback.message.answer("Вы нажали кнопку \"Текущий турнир\"")
    await callback.answer()
