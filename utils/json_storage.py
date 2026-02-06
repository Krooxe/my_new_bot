"""
Утилиты для работы с JSON хранилищем
"""
import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from db.database import db
from db.models import Tournament

logger = logging.getLogger(__name__)

class JSONStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.current_tournament_path = os.path.join(data_dir, "current_tournament.json")
        os.makedirs(data_dir, exist_ok=True)
    
    def save_current_tournament(self, tournament_data: Dict[str, Any]) -> bool:
        """
        Сохраняет текущий активный турнир в JSON И в базу данных
        """
        try:
            # Сохраняем в JSON (для обратной совместимости)
            tournament_with_meta = {
                **tournament_data,
                "_meta": {
                    "selected_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "active": True
                }
            }
            
            with open(self.current_tournament_path, 'w', encoding='utf-8') as f:
                json.dump(tournament_with_meta, f, indent=2, ensure_ascii=False)
            
            # Сохраняем в базу данных
            tournament_obj = Tournament(
                tournament_id=tournament_data["id"],
                name=tournament_data["name"],
                date=tournament_data["date"],
                location=tournament_data["location"],
                fights=tournament_data.get("fights", []),
                status="active",
                bets_open=True
            )
            
            db.save_tournament(tournament_obj)
            
            logger.info(f"Турнир сохранён в БД и JSON: {tournament_data.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении турнира: {e}")
            return False
    
    def get_current_tournament(self) -> Optional[Dict[str, Any]]:
        """
        Получает текущий активный турнир из базы данных
        """
        try:
            # Пробуем получить из базы данных
            tournament = db.get_active_tournament()
            
            if tournament:
                return {
                    "id": tournament.tournament_id,
                    "name": tournament.name,
                    "date": tournament.date,
                    "location": tournament.location,
                    "fights": tournament.fights,
                    "status": tournament.status,
                    "bets_open": tournament.bets_open,
                    "_meta": {
                        "selected_at": tournament.created_at.isoformat(),
                        "active": True
                    }
                }
            
            # Если в базе нет, пробуем JSON (для обратной совместимости)
            if os.path.exists(self.current_tournament_path):
                with open(self.current_tournament_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при чтении турнира: {e}")
            return None
    
    # ... остальные методы без изменений ...


# Создаем глобальный экземпляр
storage = JSONStorage()