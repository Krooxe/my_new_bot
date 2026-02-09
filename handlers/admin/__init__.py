"""
Импорт всех админ-хэндлеров
"""
from aiogram import Router

# Импортируем КЛАССЫ роутеров, а не сами роутеры
from .panel import router as panel_router
from .new_ppv import router as new_ppv_router
from .finish_ppv import router as finish_ppv_router
from .set_odds import router as set_odds_router  # ← ИМПОРТИРУЕМ
from .stats import router as stats_router
from .announcement import router as announcement_router
from .exit import router as exit_router

# Собираем все админ-роутеры в один
admin_main_router = Router()

# Включаем все роутеры
admin_main_router.include_router(panel_router)
admin_main_router.include_router(new_ppv_router)
admin_main_router.include_router(finish_ppv_router)
admin_main_router.include_router(set_odds_router)  # ← ВКЛЮЧАЕМ
admin_main_router.include_router(stats_router)
admin_main_router.include_router(announcement_router)
admin_main_router.include_router(exit_router)