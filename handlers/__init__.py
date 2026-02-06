"""
Модуль handlers - содержит все обработчики команд и callback'ов бота
"""
from aiogram import Router
from .start import router as start_router
from .tournament import router as tournament_router
from .leaderboard import router as leaderboard_router
from .archive import router as archive_router
from .tournament_fights import router as tournament_fights_router
from .ppv_selection import router as ppv_selection_router

# Импортируем админ-роутеры из папки admin
from .admin import admin_main_router  # Импортируем собранный роутер

def get_all_routers() -> list[Router]:
    """
    Возвращает список всех роутеров для регистрации в диспетчере
    """
    return [
        tournament_fights_router,
        ppv_selection_router,
        admin_main_router,  # ОДИН админ-роутер вместо многих
        start_router,
        tournament_router,
        leaderboard_router,
        archive_router
    ]