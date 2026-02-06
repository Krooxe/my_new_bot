"""
Обработчик кнопки "Новый PPV" (только если нет активного турнира)
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery

from utils.json_storage import storage

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "admin_new_ppv")
async def admin_new_ppv_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Новый PPV"
    """
    # Проверяем, нет ли уже активного турнира
    current_tournament = storage.get_current_tournament()
    if current_tournament and current_tournament.get("status") == "active":
        await callback.answer("❌ Уже есть активный PPV турнир!", show_alert=True)
        return
    
    logger.info(f"Администратор {callback.from_user.id} нажал 'Новый PPV'")
    
    # Здесь будет переход к выбору турнира из API
    await callback.answer("Функция выбора нового PPV в разработке", show_alert=True)