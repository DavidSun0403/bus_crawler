from flask import Flask, jsonify, render_template
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


@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')


@app.route('/api/bus_records')
def get_bus_records():
    """獲取第一個表的數據（元朗到深圳灣 - 深圳灣站）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bus_records 
            ORDER BY estimated_departure_time DESC 
            LIMIT 50
        ''')
        records = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': format_records(records),
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bus_records_2 
            ORDER BY estimated_departure_time DESC 
            LIMIT 50
        ''')
        records = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': format_records(records),
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bus_records_3 
            ORDER BY estimated_departure_time DESC 
            LIMIT 50
        ''')
        records = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': format_records(records),
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
