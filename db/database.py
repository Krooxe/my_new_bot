"""
Класс для работы с базой данных SQLite
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from .models import User, Tournament, Bet

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = "db/ufc_bot.db"):
        self.db_path = db_path
        self._create_tables()
        logger.info(f"База данных инициализирована: {db_path}")
    
    def _get_connection(self):
        """Создаёт соединение с базой данных"""
        Path("db").mkdir(exist_ok=True)  # Создаём папку если её нет
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Чтобы получать строки как словари
        return conn
    
    def _create_tables(self):
        """Создаёт таблицы если они не существуют"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Таблица турниров
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tournaments (
                    tournament_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    date TEXT,
                    location TEXT,
                    fights TEXT,  -- JSON список боёв
                    status TEXT DEFAULT 'active',
                    bets_open BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица ставок
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bets (
                    bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tournament_id TEXT NOT NULL,
                    fight_index INTEGER NOT NULL,
                    fighter_choice TEXT NOT NULL,
                    amount INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (tournament_id) REFERENCES tournaments (tournament_id)
                )
            """)
            
            conn.commit()
            logger.info("Таблицы базы данных созданы/проверены")
    
    # ========== МЕТОДЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========
    
    def add_or_update_user(self, user: User) -> bool:
        """
        Добавляет или обновляет пользователя
        Возвращает True если пользователь новый, False если обновлён существующий
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Проверяем, есть ли уже пользователь
                cursor.execute(
                    "SELECT user_id FROM users WHERE user_id = ?",
                    (user.user_id,)
                )
                exists = cursor.fetchone()
                
                if exists:
                    # Обновляем существующего
                    cursor.execute("""
                        UPDATE users 
                        SET username = ?, first_name = ?, last_name = ?, 
                            last_active = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (user.username, user.first_name, user.last_name, user.user_id))
                    logger.info(f"Пользователь обновлён: {user.user_id}")
                    return False
                else:
                    # Добавляем нового
                    cursor.execute("""
                        INSERT INTO users 
                        (user_id, username, first_name, last_name, is_admin, created_at, last_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user.user_id, user.username, user.first_name, user.last_name,
                        user.is_admin, user.created_at.isoformat(), user.last_active.isoformat()
                    ))
                    logger.info(f"Новый пользователь добавлен: {user.user_id}")
                    return True
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя {user.user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Получает пользователя по ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row['user_id'],
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_active=datetime.fromisoformat(row['last_active']),
                        is_admin=bool(row['is_admin'])
                    )
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя {user_id}: {e}")
            return None
    
    def get_all_users(self, only_active: bool = True) -> List[User]:
        """Получает всех пользователей"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if only_active:
                    # Только активные за последние 30 дней
                    cursor.execute("""
                        SELECT * FROM users 
                        WHERE last_active > datetime('now', '-30 days')
                        ORDER BY last_active DESC
                    """)
                else:
                    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
                
                users = []
                for row in cursor.fetchall():
                    users.append(User(
                        user_id=row['user_id'],
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_active=datetime.fromisoformat(row['last_active']),
                        is_admin=bool(row['is_admin'])
                    ))
                
                return users
        except Exception as e:
            logger.error(f"Ошибка при получении всех пользователей: {e}")
            return []
    
    def get_users_count(self) -> int:
        """Возвращает количество пользователей"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM users")
                return cursor.fetchone()['count']
        except:
            return 0
    
    # ========== МЕТОДЫ ДЛЯ ТУРНИРОВ ==========
    
    def save_tournament(self, tournament: Tournament) -> bool:
        """Сохраняет турнир в базу"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Конвертируем бои в JSON
                fights_json = json.dumps(tournament.fights, ensure_ascii=False)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO tournaments 
                    (tournament_id, name, date, location, fights, status, bets_open, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tournament.tournament_id, tournament.name, tournament.date,
                    tournament.location, fights_json, tournament.status,
                    tournament.bets_open, tournament.created_at.isoformat()
                ))
                
                conn.commit()
                logger.info(f"Турнир сохранён: {tournament.tournament_id}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении турнира {tournament.tournament_id}: {e}")
            return False
    
    def get_active_tournament(self) -> Optional[Tournament]:
        """Получает активный турнир"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM tournaments WHERE status = 'active' ORDER BY created_at DESC LIMIT 1"
                )
                row = cursor.fetchone()
                
                if row:
                    fights = json.loads(row['fights']) if row['fights'] else []
                    return Tournament(
                        tournament_id=row['tournament_id'],
                        name=row['name'],
                        date=row['date'],
                        location=row['location'],
                        fights=fights,
                        status=row['status'],
                        bets_open=bool(row['bets_open']),
                        created_at=datetime.fromisoformat(row['created_at'])
                    )
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении активного турнира: {e}")
            return None
    
    # ========== МЕТОДЫ ДЛЯ СТАВОК ==========
    # (пока заглушки, добавим позже)
    
    def add_bet(self, bet: Bet) -> bool:
        """Добавляет ставку"""
        # TODO: реализовать позже
        return True
    
    def get_user_bets(self, user_id: int, tournament_id: str) -> List[Bet]:
        """Получает ставки пользователя на турнир"""
        # TODO: реализовать позже
        return []


# Глобальный экземпляр базы данных
db = Database()