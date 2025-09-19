import sqlite3
import os

DB = "users.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            gender TEXT,
            email TEXT UNIQUE,
            password TEXT,
            age INTEGER,
            region TEXT,
            city TEXT,
            state TEXT,
            level TEXT,
            chosen_career TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register(user):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (name, gender, email, password, age, region, city, state, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user["name"], user.get("gender",""), user["email"], user["password"], user.get("age",None),
              user.get("region",""), user.get("city",""), user.get("state",""), user.get("level","")))
        conn.commit()
        return True, "Registered"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def login(email, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email=?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def update_chosen_career(email, career):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('UPDATE users SET chosen_career=? WHERE email=?', (career, email))
    conn.commit()
    conn.close()

# initialize DB on import
init_db()
