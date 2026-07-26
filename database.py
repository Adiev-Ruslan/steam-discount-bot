import sqlite3

DB_NAME = "steam_bot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


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


def get_all_subscriptions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subscriptions")
    subscriptions = cursor.fetchall()
    conn.close()
    return subscriptions


def update_price(subscription_id, new_price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE subscriptions 
        SET last_price = ? 
        WHERE id = ? 
        """, (new_price, subscription_id)
    )

    conn.commit()
    conn.close()


