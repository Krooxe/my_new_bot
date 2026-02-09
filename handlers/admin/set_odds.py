"""
Обработчик кнопки "Ввести/изменить коэффициенты"
"""
import logging
import re
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.json_storage import storage

logger = logging.getLogger(__name__)
router = Router()


# Состояния FSM для ввода коэффициентов
class OddsStates(StatesGroup):
    waiting_for_odds = State()  # Ждём коэффициенты


def format_fights_list(tournament_data: dict) -> str:
    """Форматирует список боёв для отображения"""
    fights = tournament_data.get("fights", [])
    
    if not fights:
        return "❌ В турнире нет информации о боях"
    
    text = "🥊 <b>Бои турнира:</b>\n\n"
    for i, fight in enumerate(fights, 1):
        fighter1 = fight.get("fighter1", "Боец 1")
        fighter2 = fight.get("fighter2", "Боец 2")
        fight_type = fight.get("type", "")
        
        type_emoji = "👑" if fight_type == "Главный" else "🥊"
        type_text = f" ({fight_type})" if fight_type else ""
        
        text += f"{i}. {type_emoji} <b>{fighter1} vs {fighter2}</b>{type_text}\n"
    
    return text


def parse_odds_text(odds_text: str, fights_count: int) -> tuple[bool, str, list]:
    """
    Парсит текст с коэффициентами
    Возвращает: (успех, сообщение_об_ошибке, список_коэффициентов)
    """
    lines = odds_text.strip().split('\n')
    
    # Проверяем количество строк
    if len(lines) != fights_count:
        return False, f"❌ Нужно {fights_count} строк, а получили {len(lines)}", []
    
    odds_list = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # Пропускаем пустые строки
        if not line:
            return False, f"❌ Строка {i}: пустая строка", []
        
        # Проверяем формат: номер. коэффициент1 коэффициент2
        match = re.match(r'^(\d+)\.?\s+([\d\.]+)\s+([\d\.]+)$', line)
        if not match:
            return False, f"❌ Строка {i}: неправильный формат. Должно быть: 'номер. кф1 кф2'", []
        
        line_num, odds1_str, odds2_str = match.groups()
        
        # Проверяем номер строки
        if int(line_num) != i:
            return False, f"❌ Строка {i}: неправильный номер. Должно быть: {i}.", []
        
        # Парсим коэффициенты
        try:
            odds1 = float(odds1_str)
            odds2 = float(odds2_str)
            
            # Проверяем диапазон коэффициентов
            if odds1 <= 1.0 or odds2 <= 1.0:
                return False, f"❌ Строка {i}: коэффициенты должны быть больше 1.0", []
            
            odds_list.append({
                "fight_index": i - 1,
                "fighter1_odds": round(odds1, 2),
                "fighter2_odds": round(odds2, 2)
            })
            
        except ValueError:
            return False, f"❌ Строка {i}: неверный формат чисел", []
    
    return True, "✅ Формат правильный", odds_list


@router.callback_query(lambda c: c.data == "admin_set_odds")
async def admin_set_odds_start(callback: CallbackQuery, state: FSMContext):
    """
    Начало ввода коэффициентов
    """
    # Получаем текущий турнир
    tournament = storage.get_current_tournament()
    
    if not tournament:
        await callback.answer("❌ Нет активного турнира", show_alert=True)
        return
    
    fights = tournament.get("fights", [])
    if not fights:
        await callback.answer("❌ В турнире нет боёв", show_alert=True)
        return
    
    logger.info(f"Администратор {callback.from_user.id} начал ввод коэффициентов")
    
    # Сохраняем информацию о турнире в состоянии
    await state.update_data(
        tournament_id=tournament.get("id"),
        fights_count=len(fights)
    )
    
    # Формируем сообщение с инструкцией
    message_text = (
        "📊 <b>Ввод коэффициентов на бои</b>\n\n"
        f"{format_fights_list(tournament)}\n"
        "👇 <b>Введите коэффициенты в формате:</b>\n"
        "<code>1. 1.05 2.0\n"
        "2. 1.8 1.9\n"
        "3. 2.5 1.4</code>\n\n"
        "<b>Правила:</b>\n"
        "• Одна строка = один бой\n"
        "• Формат: 'номер. кф1 кф2'\n"
        "• Точка после номера - опционально\n"
        "• Коэффициенты через пробел\n"
        "• Коэффициенты должны быть > 1.0\n\n"
        f"<i>Нужно ввести {len(fights)} строк</i>\n\n"
        "Для отмены напишите /cancel"
    )
    
    # Кнопка "Назад"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="odds_cancel")]
    ])
    
    await callback.message.answer(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    await state.set_state(OddsStates.waiting_for_odds)
    await callback.answer()


@router.callback_query(lambda c: c.data == "odds_cancel", StateFilter(OddsStates))
async def odds_cancel_handler(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода коэффициентов"""
    await state.clear()
    await callback.message.answer("❌ Ввод коэффициентов отменён")
    await show_admin_panel(callback.message)
    await callback.answer()


@router.message(OddsStates.waiting_for_odds, F.text)
async def process_odds_input(message: Message, state: FSMContext):
    """
    Обрабатывает введённые коэффициенты
    """
    data = await state.get_data()
    fights_count = data.get("fights_count", 0)
    
    # Парсим коэффициенты
    success, error_msg, odds_list = parse_odds_text(message.text, fights_count)
    
    if not success:
        # Показываем ошибку и просим ввести снова
        await message.answer(
            f"{error_msg}\n\n"
            f"Пожалуйста, введите {fights_count} строк с коэффициентами заново.\n"
            f"Для отмены напишите /cancel",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем коэффициенты в JSON
    tournament = storage.get_current_tournament()
    if tournament:
        # Добавляем коэффициенты к боям
        fights = tournament.get("fights", [])
        for odds_data in odds_list:
            fight_index = odds_data["fight_index"]
            if fight_index < len(fights):
                fights[fight_index]["odds"] = {
                    "fighter1": odds_data["fighter1_odds"],
                    "fighter2": odds_data["fighter2_odds"]
                }
        
        # Обновляем турнир
        tournament["fights"] = fights
        tournament["has_odds"] = True
        
        if storage.save_current_tournament(tournament):
            # Формируем подтверждение
            confirmation_text = "✅ <b>Коэффициенты сохранены!</b>\n\n"
            
            for i, fight in enumerate(fights, 1):
                if "odds" in fight:
                    odds = fight["odds"]
                    fighter1 = fight.get("fighter1", "Боец 1")
                    fighter2 = fight.get("fighter2", "Боец 2")
                    
                    confirmation_text += (
                        f"{i}. <b>{fighter1}</b>: {odds['fighter1']:.2f} | "
                        f"<b>{fighter2}</b>: {odds['fighter2']:.2f}\n"
                    )
            
            await message.answer(confirmation_text, parse_mode="HTML")
            logger.info(f"Администратор {message.from_user.id} сохранил коэффициенты")
        else:
            await message.answer("❌ Ошибка при сохранении коэффициентов")
    
    await state.clear()
    await show_admin_panel(message)


@router.message(OddsStates.waiting_for_odds)
async def invalid_odds_input(message: Message):
    """Обрабатывает некорректный ввод (не текст)"""
    await message.answer(
        "❌ Пожалуйста, введите коэффициенты текстом.\n"
        "Для отмены напишите /cancel"
    )


async def show_admin_panel(message: Message):
    """
    Показывает админ-панель с кнопками
    """
    from handlers.admin.panel import get_admin_menu, get_admin_message_text
    
    current_tournament = storage.get_current_tournament()
    has_active_tournament = bool(current_tournament and current_tournament.get("status") == "active")
    
    await message.answer(
        get_admin_message_text(has_active_tournament),
        parse_mode="HTML",
        reply_markup=get_admin_menu()
    )