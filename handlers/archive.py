"""
Обработчики для архива турниров
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "archive")
async def archive_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "История турниров"
    """
    logger.info(f"Пользователь {callback.from_user.id} запросил архив турниров")
    
    # TODO: Здесь будет логика отображения истории турниров
    await callback.message.answer("Вы нажали кнопку \"История турниров\"")
    await callback.answer()
