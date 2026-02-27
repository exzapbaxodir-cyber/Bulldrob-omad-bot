import json
import random
import threading
from flask import Flask
from telegram import *
from telegram.ext import *

TOKEN = "8692829092:AAEzIExDusdb7PpDOy04bTspAFQnsS5v2l8"
ADMIN_ID = 8505635688

# ---------------- KEEP ALIVE ----------------
app_flask = Flask("")

@app_flask.route("/")
def home():
    return "Bot Live ✅"

def run():
    app_flask.run(host="0.0.0.0", port=3000)

def keep_alive():
    threading.Thread(target=run).start()

# ---------------- LANG ----------------
TEXTS = {
    "uz": {
        "menu": "🎮 O'yin tanlang",
        "balance": "💰 Balans",
        "ref": "👥 Referal",
        "promo": "🎁 Promo",
        "stats": "📊 Statistika",
        "premium": "👑 PREMIUM",
        "random": "⚠️ Bu o'yin 100% random",
    },
    "ru": {
        "menu": "🎮 Выберите игру",
        "balance": "💰 Баланс",
        "ref": "👥 Реферал",
        "promo": "🎁 Промо",
        "stats": "📊 Статистика",
        "premium": "👑 ПРЕМИУМ",
        "random": "⚠️ Игра 100% случайная",
    },
    "en": {
        "menu": "🎮 Choose game",
        "balance": "💰 Balance",
        "ref": "👥 Referral",
        "promo": "🎁 Promo",
        "stats": "📊 Statistics",
        "premium": "👑 PREMIUM",
        "random": "⚠️ 100% random game",
    }
}

# ---------------- DATA ----------------
def load_users():
    with open("users.json","r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json","w") as f:
        json.dump(data,f,indent=4)

def get_user(uid):
    data = load_users()
    if uid not in data:
        data[uid] = {
            "coin":0,
            "paid_coin":0,
            "premium":False,
            "ref":0,
            "invited":[],
            "games":0,
            "win":0,
            "lose":0,
            "lang":"uz",
            "banned":False
        }
        save_users(data)
    return data[uid]

# ---------------- START ----------------
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    data = load_users()

    if uid not in data:
        data[uid] = {
            "coin":50,
            "paid_coin":0,
            "premium":False,
            "ref":0,
            "invited":[],
            "games":0,
            "win":0,
            "lose":0,
            "lang":"uz",
            "banned":False
        }
        save_users(data)

    keyboard = [
        [InlineKeyboardButton("💣 Sapyor (5)", callback_data="sapyor")],
        [InlineKeyboardButton("🪜 Narvon (5)", callback_data="narvon")],
        [InlineKeyboardButton("🎡 G'ildirak (2)", callback_data="wheel")],
        [InlineKeyboardButton("📈 Krash (1)", callback_data="crash")],
        [InlineKeyboardButton("💰 Balans", callback_data="balance")],
        [InlineKeyboardButton("👥 Referal", callback_data="ref")],
        [InlineKeyboardButton("🎁 Promo", callback_data="promo")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton("🌍 Til", callback_data="lang")]
    ]

    await update.message.reply_text(
        TEXTS[data[uid]["lang"]]["menu"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- CALLBACK ----------------
async def button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    data = load_users()
    user = get_user(uid)

    if user["banned"]:
        await query.edit_message_text("🚫 Siz bloklangansiz")
        return

    # BALANCE
    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Coin: {user['coin']}\n💎 Paid: {user['paid_coin']}"
        )

    # SAPYOR
    if query.data == "sapyor":
        if user["coin"] < 5:
            await query.edit_message_text("❌ Coin yetarli emas")
            return
        user["coin"] -= 5
        user["games"] += 1

        bombs = 3
        grid = ["⬜"]*25
        for i in random.sample(range(25), bombs):
            grid[i] = "💣"

        text=""
        for i in range(0,25,5):
            text+=" ".join(grid[i:i+5])+"\n"

        user["win"]+=1
        save_users(data)
        await query.edit_message_text(text)

    # NARVON
    if query.data == "narvon":
        if user["coin"] < 5:
            await query.edit_message_text("❌ Coin yetarli emas")
            return
        user["coin"]-=5
        user["games"]+=1

        line=["🪜"]*20
        for i in random.sample(range(20),3):
            line[i]="🪨"

        user["win"]+=1
        save_users(data)
        await query.edit_message_text("-->"+"".join(line)+"-->")

    # WHEEL
    if query.data=="wheel":
        if user["coin"]<2:
            await query.edit_message_text("❌ Coin yetarli emas")
            return
        user["coin"]-=2
        multi=random.choice([0,2,3,5])
        if multi>0:
            win=2*multi
            user["coin"]+=win
            user["win"]+=1
            text=f"🎡 x{multi}\n+{win}"
        else:
            user["lose"]+=1
            text="❌ Lose"
        user["games"]+=1
        save_users(data)
        await query.edit_message_text(text)

    # CRASH
    if query.data=="crash":
        if user["coin"]<1:
            await query.edit_message_text("❌ Coin yetarli emas")
            return
        user["coin"]-=1
        chance=random.random()
        if chance<0.5:
            result=round(random.uniform(1,2),2)
        elif chance<0.8:
            result=round(random.uniform(2,3),2)
        elif chance<0.95:
            result=round(random.uniform(3,5),2)
        else:
            result=round(random.uniform(5,10),2)

        user["games"]+=1
        user["win"]+=1
        save_users(data)
        await query.edit_message_text(f"🚀 {result}x")

    # STATS
    if query.data=="stats":
        await query.edit_message_text(
            f"📊 O'yinlar: {user['games']}\n"
            f"🏆 Yutgan: {user['win']}\n"
            f"💸 Yutqazgan: {user['lose']}\n"
            f"👥 Referal: {user['ref']}"
        )

    # LANG
    if query.data=="lang":
        keyboard=[
            [InlineKeyboardButton("🇺🇿 Uzbek",callback_data="lang_uz")],
            [InlineKeyboardButton("🇷🇺 Русский",callback_data="lang_ru")],
            [InlineKeyboardButton("🇺🇸 English",callback_data="lang_en")]
        ]
        await query.edit_message_text("Tilni tanlang:",reply_markup=InlineKeyboardMarkup(keyboard))

    if query.data.startswith("lang_"):
        lang=query.data.split("_")[1]
        user["lang"]=lang
        save_users(data)
        await query.edit_message_text("✅ Til o'zgartirildi")

# ---------------- RUN ----------------
app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(button))

keep_alive()
app.run_polling()
