"""
Обработчики для работы с активным турниром
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from .ufc_api import ufc_api
from utils.json_storage import storage

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data.startswith("confirm_tournament_"))
async def confirm_tournament_selection(callback: CallbackQuery):
    """
    Сохраняет выбранный турнир как текущий
    """
    event_id = callback.data.replace("confirm_tournament_", "")
    
    # Получаем информацию о турнире
    event = ufc_api.get_event_by_id(event_id)
    if not event:
        await callback.answer(
            "❌ Не удалось загрузить информацию о турнире",
            show_alert=True
        )
        return
    
    # Получаем бои турнира
    fights = ufc_api.get_event_fights(event_id)
    
    # Подготавливаем данные для сохранения
    tournament_data = {
        "id": event_id,
        "name": event["name"],
        "date": event["date"],
        "location": event["location"],
        "fights": fights,
        "status": "active",  # active, finished, cancelled
        "bets_open": True,   # Приём ставок открыт
    }
    
    # Сохраняем в JSON
    if storage.save_current_tournament(tournament_data):
        # Показываем сообщение об успехе
        await callback.answer(
            f"✅ Турнир выбран!\n\n"
            f"{event['name']}\n"
            f"Теперь пользователи могут делать ставки на бои этого турнира.",
            show_alert=True
        )
        
        # Обновляем сообщение с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚙️ Управление турниром", 
                    callback_data=f"manage_tournament_{event_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика ставок", 
                    callback_data=f"tournament_stats_{event_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад в меню", 
                    callback_data="back_to_main_menu"
                )
            ]
        ])
        
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        
    else:
        await callback.answer(
            "❌ Не удалось сохранить турнир",
            show_alert=True
        )


@router.callback_query(lambda c: c.data.startswith("manage_tournament_"))
async def manage_tournament(callback: CallbackQuery):
    """
    Меню управления активным турниром
    """
    event_id = callback.data.replace("manage_tournament_", "")
    
    tournament = storage.get_current_tournament()
    if not tournament or tournament.get("id") != event_id:
        await callback.answer(
            "❌ Турнир не найден или не активен",
            show_alert=True
        )
        return
    
    # Клавиатура управления
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📢 Открыть/закрыть ставки", 
                callback_data=f"toggle_bets_{event_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Список боёв", 
                callback_data=f"show_fights_{event_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏁 Завершить турнир", 
                callback_data=f"finish_tournament_{event_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Отменить турнир", 
                callback_data=f"cancel_tournament_{event_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад", 
                callback_data=f"back_to_tournament_{event_id}"
            )
        ]
    ])
    
    status_text = "✅ Открыт" if tournament.get("bets_open", False) else "❌ Закрыт"
    
    await callback.message.answer(
        f"⚙️ <b>Управление турниром</b>\n\n"
        f"🏆 {tournament['name']}\n"
        f"📅 {tournament['date']}\n"
        f"📍 {tournament['location']}\n"
        f"📊 Статус ставок: {status_text}\n"
        f"🥊 Количество боёв: {len(tournament.get('fights', []))}\n\n"
        f"Выберите действие:",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    """
    Возврат в главное меню (заглушка)
    """
    await callback.answer("Возвращаемся в главное меню...")
    # TODO: Реализовать возврат в главное меню


# Заглушки для остальных кнопок управления
@router.callback_query(lambda c: c.data.startswith("toggle_bets_"))
async def toggle_bets(callback: CallbackQuery):
    await callback.answer("Функция 'Открыть/закрыть ставки' в разработке", show_alert=True)

@router.callback_query(lambda c: c.data.startswith("show_fights_"))
async def show_fights(callback: CallbackQuery):
    await callback.answer("Функция 'Список боёв' в разработке", show_alert=True)

@router.callback_query(lambda c: c.data.startswith("finish_tournament_"))
async def finish_tournament(callback: CallbackQuery):
    await callback.answer("Функция 'Завершить турнир' в разработке", show_alert=True)

@router.callback_query(lambda c: c.data.startswith("cancel_tournament_"))
async def cancel_tournament(callback: CallbackQuery):
    await callback.answer("Функция 'Отменить турнир' в разработке", show_alert=True)

@router.callback_query(lambda c: c.data.startswith("tournament_stats_"))
async def tournament_stats(callback: CallbackQuery):
    await callback.answer("Функция 'Статистика ставок' в разработке", show_alert=True)