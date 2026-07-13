import sqlite3

DB_NAME = "steam_bot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def add_subscription(user_id, app_id, game_name, last_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO subscriptions
        (user_id, app_id, game_name, last_price)
        VALUES (?, ?, ?, ?)
        """, (user_id, app_id, game_name, last_price)
    )

    conn.commit()
    conn.close()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
         CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            app_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            last_price INTEGER,
            notified INTEGER DEFAULT 0
            )
    """)

    conn.commit()
    conn.close()