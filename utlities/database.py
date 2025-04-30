import sqlite3

def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id              INTEGER PRIMARY KEY AUTOINCREMENT,
      name            TEXT,
      email           TEXT UNIQUE NOT NULL,
      phone           TEXT UNIQUE NOT NULL,
      device_id   TEXT NOT NULL
    );
    """)
    conn.commit()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            device_id TEXT,
            sensorid TEXT,
            value REAL
        )
    ''')
    conn.commit()
    conn.close()

def store_data(timestamp, device_id, sensorid, value):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (timestamp, device_id, sensorid, value)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, device_id, sensorid, value))
    conn.commit()
    conn.close()

def get_user_readings(userid):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, device_id, sensorid, value FROM sensor_data WHERE device_id = ? ORDER BY timestamp DESC
    ''', (userid,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_user(name, email, phone, device_id):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, email, phone, device_id)
        VALUES (?, ?, ?, ?)
    ''', (name, email, phone, device_id))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def delete_user(uid):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM users WHERE id = ?
    ''', (uid,))
    conn.commit()
    conn.close()

def get_user(userid):
    # Connect and have rows as dicts
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE id = ?
    ''', (userid,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    # Convert sqlite3.Row to a plain dict
    user = { key: row[key] for key in row.keys() }
    return user