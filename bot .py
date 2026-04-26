import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

MATCHES = [
    {"id": 1, "name": "Man United vs Arsenal", "sport": "⚽ Football"},
    {"id": 2, "name": "Lakers vs Warriors", "sport": "🏀 Basketball"},
    {"id": 3, "name": "Djokovic vs Nadal", "sport": "🎾 Tennis"},
]

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🏆 Predict Match", callback_data="predict")],
        [InlineKeyboardButton("💰 My Balance", callback_data="balance")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏆 Welcome to SportsPredictBot!\n\nPredict matches and earn coins!",
        reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "predict":
        keyboard = [[InlineKeyboardButton(f"{m['sport']} {m['name']}", callback_data=f"m_{m['id']}")] for m in MATCHES]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="menu")])
        await query.edit_message_text("Choose a match:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "balance":
        await query.edit_message_text("💰 Balance: 0 coins", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]]))
    elif query.data == "menu":
        await query.edit_message_text("🏆 Main Menu", reply_markup=main_menu())

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
