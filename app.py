from flask import Flask, jsonify, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'bus_arrivals.db'


def get_db_connection():
    """獲取數據庫連接"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def format_records(records):
    """格式化記錄為字典列表"""
    return [dict(record) for record in records]


def filter_by_date_and_search(table_name, date_str=None, search_query=None):
    """根據日期和搜索關鍵詞過濾數據"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = f'SELECT * FROM {table_name} WHERE 1=1'
    params = []
    
    # 日期過濾
    if date_str:
        query += ' AND DATE(estimated_departure_time) = ?'
        params.append(date_str)
    
    # 搜索過濾（搜索到達時間或出發時間）
    if search_query:
        query += ' AND (estimated_arrival_time LIKE ? OR estimated_departure_time LIKE ?)'
        search_pattern = f'%{search_query}%'
        params.extend([search_pattern, search_pattern])
    
    query += ' ORDER BY estimated_departure_time DESC LIMIT 100'
    
    cursor.execute(query, params)
    records = cursor.fetchall()
    conn.close()
    
    return format_records(records)


@app.route('/')
def index():
    """主頁面 - 導航頁面"""
    return render_template('index.html')


@app.route('/route1')
def route1():
    """路線1頁面 - 37路深圳灣站"""
    return render_template('route1.html')


@app.route('/route2')
def route2():
    """路線2頁面 - 37路友新街站"""
    return render_template('route2.html')


@app.route('/route3')
def route3():
    """路線3頁面 - 38路"""
    return render_template('route3.html')


@app.route('/api/bus_records')
def get_bus_records():
    """獲取第一個表的數據（元朗到深圳灣 - 深圳灣站）"""
    try:
        date_str = request.args.get('date')
        search_query = request.args.get('search')
        
        records = filter_by_date_and_search('bus_records', date_str, search_query)
        
        return jsonify({
            'success': True,
            'data': records,
            'count': len(records)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bus_records_2')
def get_bus_records_2():
    """獲取第二個表的數據（元朗到深圳灣 - 友新街站）"""
    try:
        date_str = request.args.get('date')
        search_query = request.args.get('search')
        
        records = filter_by_date_and_search('bus_records_2', date_str, search_query)
        
        return jsonify({
            'success': True,
            'data': records,
            'count': len(records)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bus_records_3')
def get_bus_records_3():
    """獲取第三個表的數據（38路線）"""
    try:
        date_str = request.args.get('date')
        search_query = request.args.get('search')
        
        records = filter_by_date_and_search('bus_records_3', date_str, search_query)
        
        return jsonify({
            'success': True,
            'data': records,
            'count': len(records)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/all')
def get_all_records():
    """獲取所有表的數據"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 獲取第一個表
        cursor.execute('SELECT * FROM bus_records ORDER BY estimated_departure_time DESC LIMIT 50')
        records_1 = format_records(cursor.fetchall())
        
        # 獲取第二個表
        cursor.execute('SELECT * FROM bus_records_2 ORDER BY estimated_departure_time DESC LIMIT 50')
        records_2 = format_records(cursor.fetchall())
        
        # 獲取第三個表
        cursor.execute('SELECT * FROM bus_records_3 ORDER BY estimated_departure_time DESC LIMIT 50')
        records_3 = format_records(cursor.fetchall())
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'bus_records': records_1,
                'bus_records_2': records_2,
                'bus_records_3': records_3
            },
            'counts': {
                'bus_records': len(records_1),
                'bus_records_2': len(records_2),
                'bus_records_3': len(records_3)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
