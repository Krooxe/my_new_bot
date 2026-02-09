import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def parse_date(date_str):
    """Парсит дату из строки в формате 'February 21, 2026'"""
    try:
        # Удаляем возможные лишние пробелы и парсим
        date_str = date_str.strip()
        # Пробуем разные форматы дат
        for fmt in ('%B %d, %Y', '%b %d, %Y'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
    except Exception as e:
        print(f"Ошибка парсинга даты '{date_str}': {e}")
    return None

def get_ufc_events():
    """Получает все турниры с UFC Stats и фильтрует по дате"""
    events = []
    
    try:
        # Получаем завершенные турниры
        url = "http://ufcstats.com/statistics/events/completed"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу с событиями
        table = soup.find('table', class_='b-statistics__table-events')
        
        if table:
            rows = table.find_all('tr')[1:]  # Пропускаем заголовок
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 1:
                    # Извлекаем полный текст ячейки
                    full_text = cols[0].get_text(strip=True)
                    
                    # Парсим название и дату
                    event_data = parse_event_data(full_text)
                    if event_data:
                        # Получаем ссылку на детали события
                        link = cols[0].find('a')
                        if link and link.get('href'):
                            event_data['url'] = link['href']
                        
                        events.append(event_data)
        
        return events
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return []

def parse_event_data(text):
    """Парсит название и дату из текста события"""
    # Ищем дату в формате "Month DD, YYYY"
    date_pattern = r'([A-Z][a-z]+ \d{1,2}, \d{4})'
    match = re.search(date_pattern, text)
    
    if match:
        date_str = match.group(1)
        event_date = parse_date(date_str)
        
        if event_date:
            # Извлекаем название (все до даты)
            event_name = text.split(date_str)[0].strip()
            
            return {
                'name': event_name,
                'date': event_date,
                'date_str': date_str
            }
    
    return None

def filter_past_events(events):
    """Фильтрует события, дата которых меньше или равна текущей"""
    current_date = datetime.now()
    past_events = []
    
    for event in events:
        if event['date'] <= current_date:
            past_events.append(event)
    
    # Сортируем по дате (от новых к старым)
    past_events.sort(key=lambda x: x['date'], reverse=True)
    
    return past_events

def get_event_fights(event_url):
    """Получает список боев для конкретного события"""
    try:
        response = requests.get(event_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        fights = []
        
        # Ищем таблицу с боями
        fights_table = soup.find('table', class_='b-fight-details__table')
        
        if not fights_table:
            # Пробуем другой вариант класса таблицы
            fights_table = soup.find('table', class_='b-statistics__table')
        
        if fights_table:
            # Получаем все строки кроме заголовка
            rows = fights_table.find_all('tr')[1:]  # Пропускаем заголовок
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:  # Минимум 3 колонки должны быть
                    try:
                        # Попробуем несколько способов извлечения имен
                        fighters = []
                        
                        # Способ 1: искать ссылки с именами
                        fighter_links = row.find_all('a', class_='b-link_style_black')
                        if fighter_links:
                            for link in fighter_links:
                                name = link.get_text(strip=True)
                                if name and len(name) > 1:  # Фильтруем пустые имена
                                    fighters.append(name)
                        
                        # Способ 2: искать в ячейках с классом
                        if len(fighters) < 2:
                            fighter_cells = row.find_all('td', class_='b-fight-details__table-col')
                            for cell in fighter_cells:
                                text = cell.get_text(strip=True)
                                if text and ' vs ' not in text and len(text) > 2:
                                    fighters.append(text)
                        
                        # Если нашли двух бойцов
                        if len(fighters) >= 2:
                            fighter1 = fighters[0]
                            fighter2 = fighters[1]
                            
                            # Определяем победителя
                            winner = determine_winner(row, fighter1, fighter2)
                            
                            fights.append({
                                'fighter1': fighter1,
                                'fighter2': fighter2,
                                'winner': winner
                            })
                            
                            # Ограничим количество боев для вывода
                            if len(fights) >= 15:  # Обычно в карде до 15 боев
                                break
                    
                    except Exception as e:
                        print(f"Ошибка при парсинге боя: {e}")
                        continue
        
        return fights
        
    except Exception as e:
        print(f"Ошибка при получении боев: {e}")
        return []

def determine_winner(row, fighter1, fighter2):
    """Определяет победителя боя"""
    try:
        # Способ 1: искать выделенный текст (победитель часто выделен жирным)
        bold_text = row.find(['b', 'strong'])
        if bold_text:
            winner_name = bold_text.get_text(strip=True)
            if winner_name and len(winner_name) > 1:
                return winner_name
        
        # Способ 2: искать маркер победы (W/L)
        cells = row.find_all('td')
        for cell in cells:
            text = cell.get_text(strip=True)
            if text == 'W' or text == 'win':
                # Предполагаем, что первый боец - победитель
                return fighter1
            elif text == 'L' or text == 'loss':
                # Предполагаем, что второй боец - победитель
                return fighter2
        
        # Способ 3: проверяем первый столбец на наличие символа победы
        first_col = cells[0].get_text(strip=True) if cells else ''
        if '✓' in first_col or '★' in first_col or 'W' in first_col:
            return fighter1
        
        # Если не определили, возвращаем первого бойца как предположительного победителя
        return fighter1
        
    except:
        # Если не удалось определить, возвращаем первого бойца
        return fighter1

def print_last_event_results(past_events):
    """Выводит результаты последнего турнира"""
    if not past_events:
        print("Нет прошедших турниров для анализа.")
        return
    
    last_event = past_events[0]
    
    print("=" * 70)
    print("ПОСЛЕДНИЙ ПРОШЕДШИЙ ТУРНИР")
    print("=" * 70)
    
    formatted_date = last_event['date'].strftime('%d.%m.%Y')
    print(f"*{last_event['name']} ({formatted_date})*\n")
    
    # Получаем бои для этого события
    if 'url' in last_event:
        print("Загружаем результаты боев...")
        fights = get_event_fights(last_event['url'])
        
        if fights:
            print("Бои:")
            for i, fight in enumerate(fights, 1):
                print(f"{i}. {fight['fighter1']} vs {fight['fighter2']} (победитель — {fight['winner']})")
        else:
            print("Не удалось загрузить информацию о боях.")
            print(f"Попробуйте посмотреть детали по ссылке: {last_event['url']}")
    else:
        print("Нет ссылки на детали турнира.")
    
    print("\n" + "=" * 70)
    
    # Показываем статистику
    print(f"Всего прошедших турниров: {len(past_events)}")
    if len(past_events) > 1:
        print(f"\nСледующие турниры в списке:")
        for i, event in enumerate(past_events[1:4], 2):  # Следующие 3 турнира
            date_str = event['date'].strftime('%d.%m.%Y')
            print(f"{i}. {event['name']} ({date_str})")
    
    print("=" * 70)

def main():
    print("=" * 70)
    print("АНАЛИЗ ПОСЛЕДНЕГО ТУРНИРА UFC")
    print("=" * 70)
    
    # Получаем все события
    print("\nЗагружаем турниры с UFC Stats...")
    all_events = get_ufc_events()
    
    if not all_events:
        print("Не удалось загрузить события.")
        return
    
    print(f"Загружено событий: {len(all_events)}")
    
    # Фильтруем прошедшие события
    past_events = filter_past_events(all_events)
    
    # Выводим результаты последнего турнира
    print_last_event_results(past_events)

if __name__ == "__main__":
    main()