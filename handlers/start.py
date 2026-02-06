"""
Обработчики команды /start и главного меню
"""
import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from db.database import db
from db.models import User

logger = logging.getLogger(__name__)
router = Router()


def main_menu() -> InlineKeyboardMarkup:
    """Создает клавиатуру главного меню"""
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
    Регистрирует пользователя в базе данных
    """
    user = message.from_user
    logger.info(f"Пользователь {user.username} (ID: {user.id}) написал /start")
    
    # Создаём объект пользователя
    user_obj = User(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Добавляем/обновляем в базе
    is_new_user = db.add_or_update_user(user_obj)
    
    # Формируем приветствие
    welcome_text = "Привет! Я живой 🙂"
    if is_new_user:
        welcome_text = f"👋 Добро пожаловать, {user.first_name or user.username}!\nЯ бот для ставок на UFC!"
    else:
        welcome_text = f"👋 С возвращением, {user.first_name or user.username}!"
    
    await message.answer(
        welcome_text + "\n\nВыберите действие:",
        reply_markup=main_menu()
    )