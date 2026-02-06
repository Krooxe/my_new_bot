"""
Модуль для работы с UFC/MMA API (ESPN)
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class UFCAPIClient:
    """Клиент для работы с ESPN UFC API"""
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/mma/ufc"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UFC-Bot/1.0 (+https://github.com/Krooxe/my_new_bot)'
        })
    
    def get_upcoming_events(self) -> List[Dict]:
        """Получить предстоящие UFC события"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/scoreboard",
                params={"limit": "20"}
            )
            
            if response.status_code != 200:
                logger.error(f"Ошибка ESPN API: {response.status_code}")
                return []
            
            data = response.json()
            
            # Фильтруем только UFC события
            ufc_events = []
            for event in data.get("events", []):
                # Проверяем разными способами, что это UFC
                if self._is_ufc_event(event):
                    parsed_event = self._parse_event(event)
                    if parsed_event:
                        ufc_events.append(parsed_event)
            
            # Сортируем по дате (ближайшие первыми)
            ufc_events.sort(key=lambda x: x.get('date', ''))
            
            return ufc_events[:10]  # Ограничиваем 10 событиями
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к ESPN API: {e}")
            return []
    
    def _is_ufc_event(self, event: Dict) -> bool:
        """Проверяем, что это UFC событие"""
        # Способ 1: По slug сезона
        if event.get("season", {}).get("slug") == "ufc":
            return True
        
        # Способ 2: По названию
        name = event.get("name", "").upper()
        if "UFC" in name or "ULTIMATE FIGHTING CHAMPIONSHIP" in name:
            return True
        
        # Способ 3: По лиге
        competitions = event.get("competitions", [])
        if competitions:
            league = competitions[0].get("league", {})
            if league.get("slug") == "ufc":
                return True
        
        return False
    
    def _parse_event(self, event: Dict) -> Optional[Dict]:
        """Парсим информацию о событии"""
        try:
            event_id = event.get("id")
            name = event.get("name", "Неизвестный турнир")
            
            # Парсим дату
            date_str = event.get("date", "")
            date_formatted = "Дата не указана"
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    date_formatted = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    date_formatted = date_str
            
            # Парсим место
            location = "Место не указано"
            competitions = event.get("competitions", [])
            if competitions:
                venue = competitions[0].get("venue", {})
                if venue:
                    city = venue.get("address", {}).get("city", "")
                    state = venue.get("address", {}).get("state", "")
                    country = venue.get("address", {}).get("country", "")
                    
                    location_parts = []
                    if city:
                        location_parts.append(city)
                    if state:
                        location_parts.append(state)
                    if country:
                        location_parts.append(country)
                    
                    location = ", ".join(location_parts) if location_parts else venue.get("fullName", "Место не указано")
            
            return {
                "id": event_id,
                "name": name,
                "date": date_formatted,
                "location": location,
                "raw_data": event  # Сохраняем сырые данные на всякий случай
            }
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге события: {e}")
            return None

    def get_event_fights(self, event_id: str) -> List[Dict]:
        """Получить бои конкретного турнира"""
        try:
            # Пробуем получить данные о боях
            # ESPN не имеет прямого endpoint для боёв, будем парсить из event
            response = self.session.get(
                f"{self.BASE_URL}/scoreboard",
                params={"limit": "50"}
            )
            
            if response.status_code != 200:
                logger.error(f"Ошибка при запросе турнира {event_id}: {response.status_code}")
                return []
            
            data = response.json()
            
            # Ищем нужный турнир по ID
            target_event = None
            for event in data.get("events", []):
                if str(event.get("id")) == str(event_id):
                    target_event = event
                    break
            
            if not target_event:
                logger.warning(f"Турнир {event_id} не найден в ответе")
                return []
            
            # Парсим бои из турнира
            fights = self._parse_fights_from_event(target_event)
            return fights
            
        except Exception as e:
            logger.error(f"Ошибка при получении боёв турнира {event_id}: {e}")
            return []
    
    def _parse_fights_from_event(self, event: Dict) -> List[Dict]:
        """Парсим список боёв из события"""
        fights = []
        competitions = event.get("competitions", [])
        
        # ESPN хранит бои в competitions
        for competition in competitions:
            competitors = competition.get("competitors", [])
            if len(competitors) >= 2:
                fighter1 = competitors[0].get("athlete", {}).get("displayName", "Боец 1")
                fighter2 = competitors[1].get("athlete", {}).get("displayName", "Боец 2")
                
                # Определяем тип боя (главный/предварительный)
                competition_type = "Предварительный"
                if competition.get("type", {}).get("slug") == "main":
                    competition_type = "Главный"
                
                fights.append({
                    "fighter1": fighter1,
                    "fighter2": fighter2,
                    "type": competition_type,
                    "order": competition.get("order", 99)
                })
        
        # ПРОБЛЕМА: ESPN возвращает бои в обратном порядке!
        # Решение: переворачиваем весь список
        fights.reverse()  # ← ВОТ ЭТА СТРОКА ИСПРАВИТ ПРОБЛЕМУ
        
        return fights
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Получить информацию о конкретном турнире по ID"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/scoreboard",
                params={"limit": "50"}
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            for event in data.get("events", []):
                if str(event.get("id")) == str(event_id):
                    return self._parse_event(event)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении турнира {event_id}: {e}")
            return None

# Создаем глобальный экземпляр клиента
ufc_api = UFCAPIClient()