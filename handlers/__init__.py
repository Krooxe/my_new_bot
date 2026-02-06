"""
Модуль handlers - содержит все обработчики команд и callback'ов бота
"""
from aiogram import Router
from .start import router as start_router
from .tournament import router as tournament_router
from .leaderboard import router as leaderboard_router
from .archive import router as archive_router
from .admin import router as admin_router


def get_all_routers() -> list[Router]:
    """
    Возвращает список всех роутеров для регистрации в диспетчере
    """
    return [
        admin_router,      # Админ-панель (первым для приоритета)
        start_router,
        tournament_router,
        leaderboard_router,
        archive_router
    ]