"""
Модели данных для базы данных бота
"""
from datetime import datetime
from typing import Optional


class User:
    """Модель пользователя"""
    
    def __init__(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_active: Optional[datetime] = None,
        is_admin: bool = False
    ):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = created_at or datetime.now()
        self.last_active = last_active or datetime.now()
        self.is_admin = is_admin
    
    def __repr__(self):
        return f"User({self.user_id}, @{self.username}, {self.first_name})"


class Tournament:
    """Модель турнира (активного)"""
    
    def __init__(
        self,
        tournament_id: str,
        name: str,
        date: str,
        location: str,
        fights: list,
        status: str = "active",
        bets_open: bool = True,
        created_at: Optional[datetime] = None
    ):
        self.tournament_id = tournament_id
        self.name = name
        self.date = date
        self.location = location
        self.fights = fights  # Список боёв в JSON формате
        self.status = status  # active, finished, cancelled
        self.bets_open = bets_open
        self.created_at = created_at or datetime.now()
    
    def __repr__(self):
        return f"Tournament({self.tournament_id}, {self.name})"


class Bet:
    """Модель ставки пользователя"""
    
    def __init__(
        self,
        bet_id: int,
        user_id: int,
        tournament_id: str,
        fight_index: int,  # Индекс боя в списке fights
        fighter_choice: str,  # Выбранный боец (fighter1 или fighter2)
        amount: int = 1,  # Количество очков/ставка
        created_at: Optional[datetime] = None
    ):
        self.bet_id = bet_id
        self.user_id = user_id
        self.tournament_id = tournament_id
        self.fight_index = fight_index
        self.fighter_choice = fighter_choice
        self.amount = amount
        self.created_at = created_at or datetime.now()
    
    def __repr__(self):
        return f"Bet({self.bet_id}, user:{self.user_id}, fight:{self.fight_index})"