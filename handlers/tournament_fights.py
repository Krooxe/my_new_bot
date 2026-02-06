"""
Обработчики для отображения боёв выбранного турнира
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from .ufc_api import ufc_api
from utils.json_storage import storage  # Импортируем наше хранилище

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda c: c.data.startswith("confirm_tournament_"))
async def confirm_tournament_selection(callback: CallbackQuery):
    """
    Сохраняет выбранный турнир как текущий в JSON
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
        "status": "active",
        "bets_open": True,
    }
    
    # Сохраняем в JSON
    if storage.save_current_tournament(tournament_data):
        await callback.answer(
            f"✅ Турнир '{event['name']}' сохранен как текущий!",
            show_alert=True
        )
        
        # Меняем кнопку на "Текущий турнир установлен"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏆 Текущий турнир установлен", 
                    callback_data="tournament_already_set"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data="back_to_tournament_list"
                )
            ]
        ])
        
        # Редактируем только клавиатуру сообщения
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        
    else:
        await callback.answer(
            "❌ Не удалось сохранить турнир",
            show_alert=True
        )


@router.callback_query(lambda c: c.data == "tournament_already_set")
async def tournament_already_set(callback: CallbackQuery):
    """
    Информация о том, что турнир уже установлен
    """
    tournament = storage.get_current_tournament()
    
    if tournament:
        message = (
            f"🏆 <b>Текущий активный турнир:</b>\n\n"
            f"{tournament['name']}\n"
            f"📅 {tournament['date']}\n"
            f"📍 {tournament['location']}\n"
            f"🥊 Боев: {len(tournament.get('fights', []))}\n\n"
            f"Статус: {'✅ Активен' if tournament.get('status') == 'active' else '❌ Не активен'}\n"
            f"Ставки: {'✅ Открыты' if tournament.get('bets_open') else '❌ Закрыты'}"
        )
    else:
        message = "❌ Нет активного турнира"
    
    await callback.answer(message, show_alert=True)
    
@router.callback_query(lambda c: c.data.startswith("select_ppv_"))
async def show_tournament_fights(callback: CallbackQuery):
    """
    Показывает список боёв выбранного турнира
    """
    # Извлекаем ID события из callback_data
    event_id = callback.data.replace("select_ppv_", "")
    
    logger.info(f"Пользователь {callback.from_user.id} выбрал турнир {event_id}")
    
    await callback.answer("🔄 Загружаем информацию о боях...")
    
    # Получаем информацию о турнире
    event = ufc_api.get_event_by_id(event_id)
    if not event:
        await callback.message.answer(
            "❌ Не удалось найти информацию о выбранном турнире.\n"
            "Возможно, данные устарели или турнир отменён."
        )
        return
    
    # Получаем бои турнира
    fights = ufc_api.get_event_fights(event_id)
    
    # Формируем сообщение
    message_text = f"🏆 <b>{event['name']}</b>\n"
    message_text += f"📅 {event['date']}\n"
    message_text += f"📍 {event['location']}\n\n"
    
    if fights:
        message_text += "🥊 <b>Кард боев (от главного к предварительным):</b>\n\n"
        
        # Выводим бои в обратном порядке (главные первыми), но нумерация обычная
        for i, fight in enumerate(fights, 1):
            # Определяем эмодзи для типа боя
            fight_emoji = "👑" if fight["type"] == "Главный" else "🥊"
            fight_type = f" ({fight['type']} кард)" if fight["type"] != "Предварительный" else ""
            
            message_text += f"{i}. {fight_emoji} <b>{fight['fighter1']} vs {fight['fighter2']}</b>{fight_type}\n"
    else:
        message_text += "ℹ️ Информация о боях пока не доступна. Кард будет объявлен позже.\n"
    
    message_text += "\n👇 Выберите действие:"
    
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Выбрать турнир", 
                callback_data=f"confirm_tournament_{event_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад", 
                callback_data="back_to_tournament_list"
            )
        ]
    ])
    
    # Отправляем сообщение
    await callback.message.answer(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data.startswith("confirm_tournament_"))
async def confirm_tournament_selection(callback: CallbackQuery):
    """
    Заглушка для кнопки "Выбрать турнир"
    """
    event_id = callback.data.replace("confirm_tournament_", "")
    
    await callback.answer(
        f"Турнир #{event_id} выбран! (функционал в разработке)",
        show_alert=True
    )


@router.callback_query(lambda c: c.data == "back_to_tournament_list")
async def back_to_tournament_list(callback: CallbackQuery):
    """
    Заглушка для кнопки "Назад"
    """
    await callback.answer(
        "Возврат к списку турниров (функционал в разработке)",
        show_alert=True
    )