"""
Обработчики для выбора PPV турнира (админ-панель)
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from .ufc_api import ufc_api

logger = logging.getLogger(__name__)
router = Router()  # ← ВАЖНО: эта строка должна быть здесь!


def format_events_for_menu(events: list) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком турниров
    """
    keyboard = []
    
    # Добавляем кнопки для каждого турнира
    for i, event in enumerate(events, 1):
        event_name = event['name']
        
        # Форматируем текст для кнопки
        if ":" in event_name:
            # Разделяем по первому двоеточию
            parts = event_name.split(":", 1)
            button_text = f"{parts[0]}:\n{parts[1].strip()}"
        else:
            # Если двоеточия нет - оставляем как есть
            button_text = event_name
        
        # Обрезаем до 64 символов (лимит Telegram)
        if len(button_text) > 64:
            button_text = button_text[:61] + "..."
        
        # Создаем callback_data в формате: select_ppv_123456
        callback_data = f"select_ppv_{event['id']}"
        
        # ОДНА КНОПКА НА ТУРНИР!
        keyboard.append([InlineKeyboardButton(
            text=f"{i}. {button_text}",
            callback_data=callback_data
        )])
    
    # Добавляем кнопку "Назад" в конце
    keyboard.append([InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="admin_back"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(lambda c: c.data == "admin_new_ppv")
async def admin_new_ppv_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Новый PPV" в админ-панели
    """
    user = callback.from_user
    logger.info(f"Администратор {user.id} нажал 'Новый PPV'")
    
    # Показываем "загрузку"
    await callback.answer("🔄 Ищу предстоящие турниры...")
    
    # Получаем турниры из API
    events = ufc_api.get_upcoming_events()
    
    if not events:
        await callback.message.answer(
            "❌ Не удалось найти предстоящие UFC турниры.\n"
            "Проверьте подключение к интернету или попробуйте позже."
        )
        return
    
    # Формируем текст сообщения
    message_text = "🏆 <b>Найдены турниры:</b>\n\n"
    for i, event in enumerate(events, 1):
        message_text += f"{i}. <b>{event['name']}</b>\n"
        message_text += f"   📅 {event['date']}\n"
        message_text += f"   📍 {event['location']}\n\n"
    
    message_text += "👇 Выберите турнир для создания PPV:"
    
    # Создаем клавиатуру с турнирами
    keyboard = format_events_for_menu(events)
    
    # Отправляем сообщение
    await callback.message.answer(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data.startswith("select_ppv_"))
async def select_ppv_handler(callback: CallbackQuery):
    """
    Обработчик выбора конкретного PPV турнира
    """
    # Извлекаем ID события из callback_data
    event_id = callback.data.replace("select_ppv_", "")
    
    # В реальном приложении здесь нужно:
    # 1. Найти событие по ID
    # 2. Сохранить его в базу данных как активный PPV
    # 3. Создать карточки боев для ставок
    
    # Пока просто показываем сообщение
    await callback.message.answer(
        f"✅ Вы выбрали турнир с ID: {event_id}\n\n"
        f"Этот функционал в разработке. Скоро здесь можно будет "
        f"создать PPV событие для ставок!",
        parse_mode="HTML"
    )
    
    await callback.answer(f"Выбрано событие #{event_id}")


@router.callback_query(lambda c: c.data == "admin_back")
async def admin_back_handler(callback: CallbackQuery):
    """
    Обработчик кнопки "Назад" (пока заглушка)
    """
    await callback.answer("Кнопка 'Назад' пока не работает")