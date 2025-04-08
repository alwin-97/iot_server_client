import sqlite3

def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            userid TEXT,
            sensorid TEXT,
            value REAL
        )
    ''')
    conn.commit()
    conn.close()

def store_data(timestamp, userid, sensorid, value):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (timestamp, userid, sensorid, value)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, userid, sensorid, value))
    conn.commit()
    conn.close()

def get_user_readings(userid):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, userid, sensorid, value FROM sensor_data WHERE userid = ? ORDER BY timestamp DESC
    ''', (userid,))
    rows = cursor.fetchall()
    conn.close()
    return rows