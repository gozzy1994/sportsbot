import logging
import sqlite3
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

CORRECT_PREDICTION_REWARD = 50
REFERRAL_REWARD = 30
MIN_WITHDRAWAL = 500

QUESTIONS = [
    {"id": 1, "sport": "⚽ Football", "match": "Man United vs Arsenal", "date": "Today 8:00 PM", "options": ["Man United", "Arsenal", "Draw"]},
    {"id": 2, "sport": "⚽ Football", "match": "Barcelona vs Real Madrid", "date": "Tomorrow 9:00 PM", "options": ["Barcelona", "Real Madrid", "Draw"]},
    {"id": 3, "sport": "🏀 Basketball", "match": "Lakers vs Warriors", "date": "Today 10:00 PM", "options": ["Lakers", "Warriors"]},
    {"id": 4, "sport": "🏀 Basketball", "match": "Bulls vs Celtics", "date": "Tomorrow 7:00 PM", "options": ["Bulls", "Celtics"]},
    {"id": 5, "sport": "🎾 Tennis", "match": "Djokovic vs Nadal", "date": "Today 3:00 PM", "options": ["Djokovic", "Nadal"]},
    {"id": 6, "sport": "🥊 Boxing", "match": "Fury vs Joshua", "date": "Saturday 11:00 PM", "options": ["Fury", "Joshua"]},
]

logging.basicConfig(level=logging.INFO)

def init_db():
    conn = sqlite3.connect("sportsbot.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        coins INTEGER DEFAULT 0,
        referral_code TEXT,
        referred_by INTEGER,
        total_predictions INTEGER DEFAULT 0,
        correct_predictions INTEGER DEFAULT 0,
        btc_address TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        match_id INTEGER,
        prediction TEXT,
        result TEXT DEFAULT 'pending',
        coins_earned INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("sportsbot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, username, referred_by=None):
    conn = sqlite3.connect("sportsbot.db")
    c = conn.cursor()
    ref_code = f"REF{user_id}"
    c.execute("INSERT OR IGNORE INTO users (user_id, username, referral_code, referred_by) VALUES (?,?,?,?)",
              (user_id, username, ref_code, referred_by))
    if referred_by:
        c.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (REFERRAL_REWARD, referred_by))
    conn.commit()
    conn.close()

def get_coins(user_id):
    conn = sqlite3.connect("sportsbot.db")
    c = conn.cursor()
    c.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_stats(user_id):
    conn = sqlite3.connect("sportsbot.db")
    c = conn.cursor()
    c.execute("SELECT total_predictions, correct_predictions FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result if result else (0, 0)

def get_ref_code(user_id):
    conn = sqlite3.connect("sportsbot.db")
    c = conn.cursor()
    c.execute("SELECT referral_code FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else f"REF{user_id}"

def save_prediction(user_id, match_id, prediction):
    conn = sqlite3.connect("sportsbot.db")
    c = conn.cursor()
    c.execute("SELECT id FROM predictions WHERE user_id=? AND match_id=?", (user_id, match_id))
    existing = c.fetchone()
    if existing:
        conn.close()
        return False
    c.execute("INSERT INTO predictions (user_id, match_id, prediction, created_at) VALUES (?,?,?,?)",
              (user_id, match_id, prediction, datetime.now().strftime("%Y-%m-%d %H:%M")))
    c.execute("UPDATE users SET total_predictions=total_predictions+1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return True

def get_user_predictions(user_id):
    conn = sqlite3.connect("sportsbot.db
