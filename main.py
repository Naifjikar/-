import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رمز السهم (مثال: AAPL) لمعرفة الحالة الشرعية.")

def check_yaqeen(symbol):
    url = f"https://yaaqen.com/stocks/{symbol}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # افحص نص أو عناصر معينة داخل الصفحة تحدد حالة السهم
        status_element = soup.find("div", class_="status")  # مثال على class
        if status_element:
            status_text = status_element.get_text(strip=True)
            if "مباح" in status_text:
                return "مباح ✅"
            elif "غير مباح" in status_text:
                return "غير مباح ❌"
        return "غير محدث"
    except Exception:
        return "تعذر الاتصال"

    try:
        r3 = requests.get(f'https://chart-idea.com/filter?q={symbol}')
        results["Chart Idea"] = "مباح ✅" if "مباح" in r3.text else "غير محدث"
        # لا توجد نسبة تطهير حالياً
        results["Chart Idea_purification"] = ""
    except:
        results["Chart Idea"] = "تعذر الاتصال"

    return results

def extract_yaqeen_purification(symbol):
    url = f"https://yaaqen.com/stocks/{symbol}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all(string=True):
            if "نسبة التطهير" in tag or ("% تطهير" in tag) or ("% للتطهير" in tag):
                return tag.strip()

        return ""
    except Exception:
        return ""

def format_response(symbol, results):
    response_text = f"رمز السهم: {symbol}\n\n"

    order = ["Yaqeen", "Filterna", "Chart Idea"]
    arabic_names = {
        "Yaqeen": "فلتر يقين",
        "Filterna": "فلترنا",
        "Chart Idea": "فلتر فكرة شارت"
    }

    for key in order:
        value = results.get(key, "غير محدث")
        if "✅" in value:
            percentage = results.get(f"{key}_purification", "")
            if percentage:
                response_text += f"{arabic_names[key]}:\nحلال، نسبة التطهير {percentage}\n\n"
            else:
                response_text += f"{arabic_names[key]}:\nحلال (نسبة التطهير غير متوفرة حالياً)\n\n"
        elif "❌" in value:
            response_text += f"{arabic_names[key]}:\nغير شرعي\n\n"
        else:
            response_text += f"{arabic_names[key]}:\nغير محدث\n\n"

    response_text += (
        "قنوات JALWE العامة:\n"
        "- الأسهم: https://t.me/JalweTrader\n"
        "- العقود: https://t.me/jalweoption\n"
        "- التعليمية: https://t.me/JalweVip\n"
    )

    return response_text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    print("User sent symbol:", symbol)  # للتأكد في اللوق
    results = check_sharia_compliance(symbol)
    response_text = format_response(symbol, results)
    await update.message.reply_text(response_text)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
