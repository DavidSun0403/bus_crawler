import requests
import sqlite3
import time
from datetime import datetime, timedelta
import logging
import random

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 數據庫設置
DB_NAME = 'bus_arrivals.db'
API_URL = 'https://rt.data.gov.hk/v2/transport/nlb/stop.php?action=estimatedArrivals&routeId=37&stopId=152'
API_URL2 = 'https://rt.data.gov.hk/v2/transport/nlb/stop.php?action=estimatedArrivals&routeId=37&stopId=135'
API_URL3 = 'https://rt.data.gov.hk/v2/transport/nlb/stop.php?action=estimatedArrivals&routeId=38&stopId=134'
# 全程約40分鐘
TRIP_DURATION_MINUTES = 40
TRIP_DURATION_MINUTES2 = 4
TRIP_DURATION_MINUTES3 = 40


def init_database():
    """初始化數據庫"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 第一個API的數據表
    # yuen long to shenzhenwan, zhenshenwan arrives
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bus_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estimated_arrival_time TEXT NOT NULL,
            estimated_departure_time TEXT NOT NULL,
            departed INTEGER,
            no_gps INTEGER,
            wheel_chair INTEGER,
            generate_time TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(estimated_departure_time)
        )
    ''')
    
    # 第二個API的數據表
    # yuen long to shenzhenwan, youxinjie arrives
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bus_records_2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estimated_arrival_time TEXT NOT NULL,
            estimated_departure_time TEXT NOT NULL,
            departed INTEGER,
            no_gps INTEGER,
            wheel_chair INTEGER,
            generate_time TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(estimated_departure_time)
        )
    ''')
    
    # 第三個API的數據表
    # 07:10 - 22:50, 每20分鐘一班 (7:10, 7:30, 7:50...)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bus_records_3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estimated_arrival_time TEXT NOT NULL,
            estimated_departure_time TEXT NOT NULL,
            departed INTEGER,
            no_gps INTEGER,
            wheel_chair INTEGER,
            generate_time TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(estimated_departure_time)
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info('數據庫初始化完成')


def calculate_departure_time(arrival_time_str, trip_duration=TRIP_DURATION_MINUTES):
    """
    根據到達時間計算出發時間
    出發時間為整點：6:00, 6:20, 6:40, 7:00, 7:20...
    通過到達時間減去全程時間後找最接近的發車時間
    """
    try:
        arrival_time = datetime.strptime(arrival_time_str, '%Y-%m-%d %H:%M:%S')
        # 減去全程時間得到大約的出發時間
        approx_departure = arrival_time - timedelta(minutes=trip_duration)
        
        # 獲取小時和分鐘
        hour = approx_departure.hour
        minute = approx_departure.minute
        
        # 計算最接近的發車時間（每20分鐘一班：00, 20, 40）
        if minute < 10:
            # 最接近 00 分
            scheduled_minute = 0
        elif minute < 30:
            # 最接近 20 分
            scheduled_minute = 20
        elif minute < 50:
            # 最接近 40 分
            scheduled_minute = 40
        else:
            # 最接近下一小時的 00 分
            scheduled_minute = 0
            hour += 1
        
        # 構建出發時間
        departure_time = approx_departure.replace(hour=hour, minute=scheduled_minute, second=0, microsecond=0)
        
        # 確保出發時間在運營時間內（06:00 - 22:00）
        departure_date = departure_time.date()
        service_start = datetime.combine(departure_date, datetime.strptime('06:00:00', '%H:%M:%S').time())
        service_end = datetime.combine(departure_date, datetime.strptime('22:00:00', '%H:%M:%S').time())
        
        if departure_time < service_start or departure_time > service_end:
            logging.warning(f'出發時間 {departure_time} 不在運營時間內（06:00-22:00）')
        
        return departure_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logging.error(f'計算出發時間錯誤: {e}')
        return None


def calculate_departure_time_offset(arrival_time_str, trip_duration=TRIP_DURATION_MINUTES3):
    """
    根據到達時間計算出發時間（帶10分鐘偏移）
    出發時間為：7:10, 7:30, 7:50, 8:10, 8:30...
    運營時間：07:10 - 22:50
    """
    try:
        arrival_time = datetime.strptime(arrival_time_str, '%Y-%m-%d %H:%M:%S')
        # 減去全程時間得到大約的出發時間
        approx_departure = arrival_time - timedelta(minutes=trip_duration)
        
        # 獲取小時和分鐘
        hour = approx_departure.hour
        minute = approx_departure.minute
        
        # 計算最接近的發車時間（每20分鐘一班，但偏移10分鐘：10, 30, 50）
        if minute < 20:
            # 最接近 10 分
            scheduled_minute = 10
        elif minute < 40:
            # 最接近 30 分
            scheduled_minute = 30
        elif minute < 60:
            # 最接近 50 分
            scheduled_minute = 50
        else:
            # 不應該發生
            scheduled_minute = 10
            hour += 1
        
        # 構建出發時間
        departure_time = approx_departure.replace(hour=hour, minute=scheduled_minute, second=0, microsecond=0)
        
        # 確保出發時間在運營時間內（07:10 - 22:50）
        departure_date = departure_time.date()
        service_start = datetime.combine(departure_date, datetime.strptime('07:10:00', '%H:%M:%S').time())
        service_end = datetime.combine(departure_date, datetime.strptime('22:50:00', '%H:%M:%S').time())
        
        if departure_time < service_start or departure_time > service_end:
            logging.warning(f'出發時間 {departure_time} 不在運營時間內（07:10-22:50）')
        
        return departure_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logging.error(f'計算出發時間錯誤: {e}')
        return None


def is_duplicate(departure_time, table_name='bus_records'):
    """檢查是否為重複記錄"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        f'SELECT COUNT(*) FROM {table_name} WHERE estimated_departure_time = ?',
        (departure_time,)
    )
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0


def save_to_database(arrival_data, trip_duration=TRIP_DURATION_MINUTES, table_name='bus_records', use_offset=False):
    """保存數據到數據庫"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    saved_count = 0
    updated_count = 0
    
    for item in arrival_data:
        arrival_time = item.get('estimatedArrivalTime')
        
        if not arrival_time:
            continue
        
        # 計算出發時間（根據是否使用偏移）
        if use_offset:
            departure_time = calculate_departure_time_offset(arrival_time, trip_duration)
        else:
            departure_time = calculate_departure_time(arrival_time, trip_duration)
        
        logging.info(f'[{table_name}] 計算出發時間: {departure_time} 對應到達時間: {arrival_time}')
        if not departure_time:
            continue
        
        # 檢查是否重複
        if is_duplicate(departure_time, table_name):
            # 更新現有記錄的預計到達時間
            try:
                cursor.execute(f'''
                    UPDATE {table_name} 
                    SET estimated_arrival_time = ?,
                        departed = ?,
                        no_gps = ?,
                        wheel_chair = ?,
                        generate_time = ?
                    WHERE estimated_departure_time = ?
                ''', (
                    arrival_time,
                    item.get('departed'),
                    item.get('noGPS'),
                    item.get('wheelChair'),
                    item.get('generateTime'),
                    departure_time
                ))
                updated_count += 1
                logging.info(f'[{table_name}] 更新記錄 - 到達: {arrival_time}, 出發: {departure_time}')
            except Exception as e:
                logging.error(f'[{table_name}] 更新記錄錯誤: {e}')
            continue
        
        try:
            cursor.execute(f'''
                INSERT INTO {table_name} 
                (estimated_arrival_time, estimated_departure_time, departed, no_gps, wheel_chair, generate_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                arrival_time,
                departure_time,
                item.get('departed'),
                item.get('noGPS'),
                item.get('wheelChair'),
                item.get('generateTime')
            ))
            
            saved_count += 1
            logging.info(f'[{table_name}] 保存新記錄 - 到達: {arrival_time}, 出發: {departure_time}')
        
        except sqlite3.IntegrityError:
            logging.warning(f'[{table_name}] 數據庫約束錯誤 - 出發時間: {departure_time}')
        except Exception as e:
            logging.error(f'[{table_name}] 保存記錄錯誤: {e}')
    
    conn.commit()
    conn.close()
    
    logging.info(f'[{table_name}] 本次操作: {saved_count} 條新記錄, {updated_count} 條更新記錄')


def fetch_and_save():
    """請求API並保存數據"""
    # 請求第一個API
    try:
        logging.info(f'開始請求API 1: {API_URL}')
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        estimated_arrivals = data.get('estimatedArrivals', [])
        
        if not estimated_arrivals:
            logging.warning('API 1: 未獲取到預計到達時間數據')
        else:
            logging.info(f'API 1: 獲取到 {len(estimated_arrivals)} 條到達時間記錄')
            save_to_database(estimated_arrivals, TRIP_DURATION_MINUTES, 'bus_records')
        
    except requests.exceptions.RequestException as e:
        logging.error(f'API 1 請求錯誤: {e}')
    except Exception as e:
        logging.error(f'API 1 處理數據錯誤: {e}')
    
    # 請求第二個API
    try:
        logging.info(f'開始請求API 2: {API_URL2}')
        response = requests.get(API_URL2, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        estimated_arrivals = data.get('estimatedArrivals', [])
        
        if not estimated_arrivals:
            logging.warning('API 2: 未獲取到預計到達時間數據')
        else:
            logging.info(f'API 2: 獲取到 {len(estimated_arrivals)} 條到達時間記錄')
            save_to_database(estimated_arrivals, TRIP_DURATION_MINUTES2, 'bus_records_2', use_offset=False)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'API 2 請求錯誤: {e}')
    except Exception as e:
        logging.error(f'API 2 處理數據錯誤: {e}')
    
    # 請求第三個API
    try:
        logging.info(f'開始請求API 3: {API_URL3}')
        response = requests.get(API_URL3, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        estimated_arrivals = data.get('estimatedArrivals', [])
        
        if not estimated_arrivals:
            logging.warning('API 3: 未獲取到預計到達時間數據')
        else:
            logging.info(f'API 3: 獲取到 {len(estimated_arrivals)} 條到達時間記錄')
            save_to_database(estimated_arrivals, TRIP_DURATION_MINUTES3, 'bus_records_3', use_offset=True)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'API 3 請求錯誤: {e}')
    except Exception as e:
        logging.error(f'API 3 處理數據錯誤: {e}')


def is_within_service_hours():
    """檢查當前時間是否在運營時間內（06:00-22:00）"""
    now = datetime.now()
    current_time = now.time()
    service_start = datetime.strptime('06:00:00', '%H:%M:%S').time()
    service_end = datetime.strptime('22:00:00', '%H:%M:%S').time()
    return service_start <= current_time <= service_end


def scheduled_fetch_and_save():
    """定時任務：僅在運營時間內執行"""
    if is_within_service_hours():
        fetch_and_save()
    else:
        logging.info('當前時間不在運營時間內（06:00-22:00），跳過執行')


def main():
    """主函數"""
    logging.info('程序啟動')
    
    # 初始化數據庫
    init_database()
    
    # 如果當前在運營時間內，立即執行一次
    if is_within_service_hours():
        fetch_and_save()
    else:
        logging.info('當前時間不在運營時間內（06:00-22:00），等待運營時間開始')
    
    logging.info('定時任務已設置，每3-7分鐘隨機執行一次（僅在06:00-22:00運營時間內）')
    
    # 持續運行，使用隨機間隔
    while is_within_service_hours():
        delay = random.randint(180, 242)
        logging.info(f'等待 {delay} 秒後執行下一次請求')
        time.sleep(delay)
        
        # 執行任務（會檢查運營時間）
        scheduled_fetch_and_save()


if __name__ == '__main__':
    main()
