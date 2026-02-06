"""
Обработчики команды /start и главного меню
"""
import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)
router = Router()


def main_menu() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру главного меню
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Текущий турнир", callback_data="current_tournament")],
        [InlineKeyboardButton(text="Статистика", callback_data="leaderboard")],
        [InlineKeyboardButton(text="История турниров", callback_data="archive")]
    ])
    return keyboard


@router.message(CommandStart())
async def start_handler(message: Message):
    """
    Обработчик команды /start
    """
    user = message.from_user
    username = user.username or user.first_name
    logger.info(f"Пользователь {username} (ID: {user.id}) написал /start")

    await message.answer(
        "Привет! Я живой 🙂\nВыберите действие:",
        reply_markup=main_menu()
    )
