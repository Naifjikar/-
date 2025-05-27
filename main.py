
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رمز السهم (مثال: AAPL) لمعرفة الحالة الشرعية.")

def check_sharia_compliance(symbol):
    responses = {}

    try:
        r1 = requests.get(f'https://chart-idea.com/filter?q={symbol}')
        responses["Chart Idea"] = "مباح ✅" if "مباح" in r1.text else "غير واضح ❓"
    except:
        responses["Chart Idea"] = "تعذر الاتصال ❌"

    try:
        r2 = requests.get(f'https://yaaqen.com/stocks/{symbol}')
        responses["Yaqeen"] = "مباح ✅" if "مباح" in r2.text else "غير واضح ❓"
    except:
        responses["Yaqeen"] = "تعذر الاتصال ❌"

    try:
        r3 = requests.get(f'https://filterna.com/stocks/{symbol}')
        responses["Filterna"] = "مباح ✅" if "مباح" in r3.text else "غير واضح ❓"
    except:
        responses["Filterna"] = "تعذر الاتصال ❌"

    return responses

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    results = check_sharia_compliance(symbol)

    response_text = f"رمز السهم: {symbol}\n\n"

"
    for source, result in results.items():
        response_text += f"- {source}: {result}
"

    response_text += """
قنوات JALWE:
- الأسهم: https://t.me/JalweTrader
- العقود: https://t.me/jalweoption
- التعليمية: https://t.me/JalweVip

للاشتراك في القنوات الخاصة:
https://salla.sa/jalawe/category/AXlzxy
"""
    await update.message.reply_text(response_text)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
