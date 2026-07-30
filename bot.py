import logging
import sqlite3
import threading
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.request import HTTPXRequest

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def init_db():
    conn = sqlite3.connect('scores.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            high_score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_score(user_id, username, score):
    conn = sqlite3.connect('scores.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT high_score FROM scores WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        cursor.execute('INSERT INTO scores (user_id, username, high_score) VALUES (?, ?, ?)', (user_id, username, score))
    else:
        current_high = row[0]
        if score > current_high:
            cursor.execute('UPDATE scores SET high_score = ?, username = ? WHERE user_id = ?', (score, username, user_id))
            
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect('scores.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT username, high_score FROM scores ORDER BY high_score DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    return rows

HTML_CONTENT = ""
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        HTML_CONTENT = f.read()
except Exception as e:
    HTML_CONTENT = f"<h1>Error loading game: {str(e)}</h1>"

app_flask = Flask(__name__)
CORS(app_flask)

@app_flask.route('/')
def home():
    return HTML_CONTENT, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app_flask.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    score = data.get('score')
    
    if user_id and score is not None:
        save_score(user_id, username if username else "Player", score)
        return jsonify({"status": "success", "message": "Score saved permanently!"}), 200
    return jsonify({"status": "error", "message": "Invalid data"}), 400

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Hello {user.first_name}!\n"
        "Welcome to *Apple Snake*.\n\n"
        "Click the button below to play right inside Telegram:"
    )
    
    game_url = "https://eight-hotels-serve.loca.lt"
    
    keyboard = [
        [InlineKeyboardButton("🎮 Play Apple Snake", web_app=WebAppInfo(url=game_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_url = "https://eight-hotels-serve.loca.lt"
    keyboard = [
        [InlineKeyboardButton("🎮 Launch Game", web_app=WebAppInfo(url=game_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Tap below to open your game inside Telegram:", reply_markup=reply_markup)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_scores = get_leaderboard()
    text = "🏆 *Apple Snake Leaderboard* 🏆\n\n"
    if not top_scores:
        text += "No scores recorded yet. Be the first!"
    else:
        for idx, (uname, hscore) in enumerate(top_scores, start=1):
            name = uname if uname else "Anonymous"
            text += f"{idx}. {name} — *{hscore} pts*\n"
            
    await update.message.reply_text(text, parse_mode="Markdown")

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    TOKEN = '8892637400:AAHI_G85Fkp3XMuHyCh-7TZuxtecihgR9cY'
    
    custom_request = HTTPXRequest(
        connect_timeout=30.0, 
        read_timeout=30.0
    )
    
    telegram_app = ApplicationBuilder().token(TOKEN).request(custom_request).build()

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("play", play))
    telegram_app.add_handler(CommandHandler("leaderboard", leaderboard))

    print("🤖 Bot and Local Score Server running... Press Ctrl+C to stop.")
    telegram_app.run_polling()