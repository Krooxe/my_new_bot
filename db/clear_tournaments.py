"""
Скрипт для очистки турниров из базы данных
"""
import sqlite3
import os

def clear_tournaments():
    """Удаляет все турниры из базы данных"""
    db_path = "db/ufc_bot.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Удаляем все записи из таблицы tournaments
        cursor.execute("DELETE FROM tournaments")
        
        # Сбрасываем autoincrement
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tournaments'")
        
        conn.commit()
        conn.close()
        
        print("✅ Все турниры удалены из базы данных")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке базы: {e}")

if __name__ == "__main__":
    clear_tournaments()