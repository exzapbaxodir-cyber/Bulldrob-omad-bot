import json
import random
import threading
from flask import Flask
from telegram import *
from telegram.ext import *

TOKEN = "8692829092:AAEzIExDusdb7PpDOy04bTspAFQnsS5v2l8"
ADMIN_ID = 8505635688

# ================= KEEP ALIVE =================
app_flask = Flask("")

@app_flask.route("/")
def home():
    return "Bot ishlayapti ✅"

def run():
    app_flask.run(host="0.0.0.0", port=3000)

def keep_alive():
    threading.Thread(target=run).start()

# ================= DATABASE =================
def load_users():
    try:
        with open("users.json","r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json","w") as f:
        json.dump(data,f,indent=4)

def get_user(uid):
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
    return data[uid]

# ================= PROMO =================
def load_promos():
    promos = {}
    try:
        with open("promo.txt","r") as f:
            for line in f:
                if line.strip():
                    code, amount, ptype, max_use, used = line.strip().split(":")
                    used_list = used.split(",") if used else []
                    promos[code] = {
                        "amount":int(amount),
                        "type":ptype,
                        "max_use":int(max_use),
                        "used":used_list
                    }
    except:
        pass
    return promos

def save_promos(promos):
    with open("promo.txt","w") as f:
        for code,info in promos.items():
            used=",".join(info["used"])
            f.write(f"{code}:{info['amount']}:{info['type']}:{info['max_use']}:{used}\n")

# ================= START =================
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid=str(user.id)
    data=load_users()

    if uid not in data:
        data[uid]=get_user(uid)

        if context.args:
            ref=context.args[0]
            if ref in data and uid not in data[ref]["invited"]:
                data[ref]["coin"]+=15
                data[ref]["ref"]+=1
                data[ref]["invited"].append(uid)

        save_users(data)

    keyboard=[
        [InlineKeyboardButton("💣 Sapyor (5)",callback_data="sapyor")],
        [InlineKeyboardButton("🪜 Narvon (5)",callback_data="narvon")],
        [InlineKeyboardButton("🎡 G'ildirak (2)",callback_data="wheel")],
        [InlineKeyboardButton("📈 Krash (1)",callback_data="crash")],
        [InlineKeyboardButton("💰 Balans",callback_data="balance")],
        [InlineKeyboardButton("👥 Referal",callback_data="ref")],
        [InlineKeyboardButton("🎁 Promo",callback_data="promo_btn")],
        [InlineKeyboardButton("📊 Statistika",callback_data="stats")]
    ]

    await update.message.reply_text(
        "🎮 O'yin tanlang\n⚠️ Barcha o'yinlar 100% random",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= CALLBACK =================
async def button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    await query.answer()
    uid=str(query.from_user.id)
    data=load_users()
    user=get_user(uid)

    if user["banned"]:
        await query.edit_message_text("🚫 Siz bloklangansiz")
        return

    # BALANCE
    if query.data=="balance":
        text=f"💰 Coin: {user['coin']}\n💎 Paid: {user['paid_coin']}"
        if user["premium"]:
            text+="\n👑 PREMIUM"
        await query.edit_message_text(text)
        return

    # REFERAL
    if query.data=="ref":
        link=f"https://t.me/{context.bot.username}?start={uid}"
        await query.edit_message_text(
            f"👥 Referal: {user['ref']}\n🔗 Link:\n{link}"
        )
        return

    # STATS
    if query.data=="stats":
        await query.edit_message_text(
            f"📊 O'yinlar: {user['games']}\n"
            f"🏆 Yutgan: {user['win']}\n"
            f"💸 Yutqazgan: {user['lose']}\n"
            f"👥 Referal: {user['ref']}"
        )
        return

    # PROMO BUTTON
    if query.data=="promo_btn":
        context.user_data["awaiting_promo"]=True
        await query.edit_message_text("Promo kodni yuboring:")
        return

    # SAPYOR
    if query.data=="sapyor":
        if user["coin"]<5:
            await query.edit_message_text("❌ Coin yetarli emas")
            return
        user["coin"]-=5
        user["games"]+=1
        bombs=random.sample(range(25),3)
        grid=["💣" if i in bombs else "⬜" for i in range(25)]
        text=""
        for i in range(0,25,5):
            text+=" ".join(grid[i:i+5])+"\n"
        user["win"]+=1
        save_users(data)
        await query.edit_message_text(text)
        return

    # NARVON
    if query.data=="narvon":
        if user["coin"]<5:
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
        return

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
            text="❌ Yutqazdingiz"
        user["games"]+=1
        save_users(data)
        await query.edit_message_text(text)
        return

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
        await query.edit_message_text(f"🚀 Krash: {result}x")
        return

# ================= PROMO MESSAGE =================
async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_promo"):
        context.user_data["awaiting_promo"]=False
