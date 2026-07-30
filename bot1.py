import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize Database for Permanent Scores
def init_db():
    conn = sqlite3.connect('scores.db')
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
    conn = sqlite3.connect('scores.db')
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
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, high_score FROM scores ORDER BY high_score DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Hello {user.first_name}!\n"
        "Welcome to *Apple Snake: Literary Edition*.\n\n"
        "Commands:\n"
        "/play - Launch the game\n"
        "/leaderboard - View top scores"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In a full setup, you can link your HTML5 game hosted via GitHub Pages/Vercel here 
    # as a Telegram Web App button, or provide instructions.
    await update.message.reply_text(
        "🎮 Click the link below to play Apple Snake!\n"
        "*(Note: Deploy your game to Vercel/Netlify or link a web app URL here)*\n"
        "https://your-hosted-game-url.com"
    )

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
    # REPLACE WITH YOUR ACTUAL BOT TOKEN FROM BOTFATHER
    TOKEN = '8892637400:AAHI_G85Fkp3XMuHyCh-7TZuxtecihgR9cY'
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("leaderboard", leaderboard))

    print("🤖 Bot is running locally on your laptop... Press Ctrl+C to stop.")
    app.run_polling()