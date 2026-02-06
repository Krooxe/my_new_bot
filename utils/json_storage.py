"""
Утилиты для работы с JSON хранилищем
"""
import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class JSONStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.current_tournament_path = os.path.join(data_dir, "current_tournament.json")
        os.makedirs(data_dir, exist_ok=True)
    
    def save_current_tournament(self, tournament_data: Dict[str, Any]) -> bool:
        """
        Сохраняет текущий активный турнир ТОЛЬКО в JSON
        """
        try:
            # Сохраняем в JSON
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
            
            logger.info(f"Турнир сохранён в JSON: {tournament_data.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении турнира: {e}")
            return False
    
    def get_current_tournament(self) -> Optional[Dict[str, Any]]:
        """
        Получает текущий активный турнир ТОЛЬКО из JSON
        """
        try:
            if not os.path.exists(self.current_tournament_path):
                return None
            
            with open(self.current_tournament_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверяем, не устарел ли турнир (больше 7 дней)
            if self._is_tournament_expired(data):
                logger.info("Турнир устарел, очищаем...")
                self.clear_current_tournament()
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка при чтении турнира: {e}")
            return None
    
    def clear_current_tournament(self) -> bool:
        """
        Очищает текущий турнир
        """
        try:
            if os.path.exists(self.current_tournament_path):
                os.remove(self.current_tournament_path)
            logger.info("Текущий турнир очищен из JSON")
            return True
        except Exception as e:
            logger.error(f"Ошибка при очистке турнира: {e}")
            return False
    
    def _is_tournament_expired(self, tournament_data: Dict) -> bool:
        """
        Проверяет, не устарел ли турнир (прошло больше 7 дней)
        """
        try:
            meta = tournament_data.get("_meta", {})
            selected_at = meta.get("selected_at")
            
            if not selected_at:
                return True
            
            selected_date = datetime.fromisoformat(selected_at)
            days_passed = (datetime.now() - selected_date).days
            
            return days_passed > 7
        except:
            return True


# Создаем глобальный экземпляр
storage = JSONStorage()