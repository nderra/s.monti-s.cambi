import sqlite3
import logging
import json
from datetime import datetime

class Database:
    def __init__(self):
        self.db_path = 'pokemon_trade.db'
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_bot BOOLEAN,
                    language_code TEXT,
                    last_active TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    card_name TEXT,
                    rarity TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    card_name TEXT,
                    rarity TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

    async def save_user(self, user_data: dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO users 
                (id, username, first_name, last_name, is_bot, language_code, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['id'],
                user_data.get('username'),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('is_bot', False),
                user_data.get('language_code'),
                datetime.now()
            ))

    async def get_user_info(self, user_id: int) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(zip([col[0] for col in cursor.description], row))
            return None

    async def save_offer(self, user_id: int, card_name: str, rarity: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO offers (user_id, card_name, rarity, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, card_name.lower(), rarity, datetime.now()))
            return cursor.lastrowid

    async def save_search(self, user_id: int, card_name: str, rarity: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO searches (user_id, card_name, rarity, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, card_name.lower(), rarity, datetime.now()))
            return cursor.lastrowid

    async def get_user_offers(self, user_id: int) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM offers WHERE user_id = ?
                ORDER BY timestamp DESC
            ''', (user_id,))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

    async def get_user_searches(self, user_id: int) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM searches WHERE user_id = ?
                ORDER BY timestamp DESC
            ''', (user_id,))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

    async def find_matching_searches(self, card_name: str, rarity: str) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT s.*, u.username, u.first_name 
                FROM searches s
                JOIN users u ON s.user_id = u.id
                WHERE LOWER(card_name) = LOWER(?) AND rarity = ?
            ''', (card_name, rarity))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

    async def find_matching_offers(self, card_name: str, rarity: str) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT o.*, u.username, u.first_name 
                FROM offers o
                JOIN users u ON o.user_id = u.id
                WHERE LOWER(card_name) = LOWER(?) AND rarity = ?
            ''', (card_name, rarity))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

    async def get_all_cards(self) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    o.card_name,
                    o.rarity,
                    REPLACE(GROUP_CONCAT(DISTINCT u.username), ',', '') AS users
                FROM offers o
                JOIN users u ON o.user_id = u.id
                GROUP BY o.card_name, o.rarity
                ORDER BY o.card_name COLLATE NOCASE
            ''')
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

    async def check_existing_card(self, card_name: str, rarity: str) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT o.*, u.username, u.first_name 
                FROM offers o
                JOIN users u ON o.user_id = u.id
                WHERE LOWER(card_name) = LOWER(?) AND rarity = ?
            ''', (card_name, rarity))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

    async def get_user_matches(self, user_id: int) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    s.id as search_id,
                    o.id as offer_id,
                    s.card_name,
                    s.rarity,
                    o.user_id as offer_user_id,
                    u.username
                FROM searches s
                JOIN offers o ON LOWER(s.card_name) = LOWER(o.card_name) 
                            AND s.rarity = o.rarity
                JOIN users u ON o.user_id = u.id
                WHERE s.user_id = ?
                ORDER BY s.timestamp DESC
            ''', (user_id,))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

    async def complete_trade(self, search_id: int, offer_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''BEGIN TRANSACTION;
                DELETE FROM searches WHERE id = ?;
                DELETE FROM offers WHERE id = ?;
                COMMIT;
            ''', (search_id, offer_id))
