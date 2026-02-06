"""
Обработчики для статистики и таблицы лидеров
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "leaderboard")
async def leaderboard_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Статистика"
    """
    logger.info(f"Пользователь {callback.from_user.id} запросил статистику")
    
    # TODO: Здесь будет логика отображения таблицы лидеров
    await callback.message.answer("Вы нажали кнопку \"Статистика\"")
    await callback.answer()
