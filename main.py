import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import get_all_routers

# -----------------------
# Настройка логов
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# -----------------------
# Загружаем токен из .env
# -----------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Не найден BOT_TOKEN в .env")
    exit(1)


# -----------------------
# Установка команд в меню бота
# -----------------------
async def set_bot_commands(bot: Bot):
    """
    Устанавливает команды бота, которые будут видны в меню
    """
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="admin", description="Админ-панель")
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Команды бота установлены в меню")


# -----------------------
# Основная функция
# -----------------------
async def main():
    logger.info("Инициализация бота...")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем все роутеры из папки handlers
    for router in get_all_routers():
        dp.include_router(router)
    
    # Устанавливаем команды в меню бота
    await set_bot_commands(bot)
    
    logger.info("Бот запущен! Ожидание сообщений...")
    
    # ================================================================
    # =====================Завершение работы бота=====================
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        logger.info("Работа бота прервана")
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения (Ctrl+C)")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        try:
            await bot.session.close()
            logger.info("Сессия бота закрыта.")
        except:
            pass
        logger.info("Бот завершил работу.")
    # ================================================================
    # ================================================================


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот завершил работу.")