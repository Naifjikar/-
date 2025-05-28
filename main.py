import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# بيانات الدخول
TOKEN = "7643817024:AAH7eCvHeLw6RsYI5s8fYFVoP8REdGlxGFM"
API_KEY = "PDTlX9ib5N6laEnauklHAgoN8UGr12uh"

logging.basicConfig(level=logging.INFO)

HARAM_KEYWORDS = [
    "bank", "insurance", "gambling", "casino", "alcohol",
    "liquor", "beer", "entertainment", "music", "movie",
    "adult", "porn", "hotel", "nightclub", "lottery", "betting"
]

def filter_stock_yaqeen_style(symbol):
    try:
        symbol = symbol.upper()
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={API_KEY}"
        income_url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=1&apikey={API_KEY}"
        balance_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?limit=1&apikey={API_KEY}"

        profile = requests.get(profile_url).json()[0]
        income = requests.get(income_url).json()[0]
        balance = requests.get(balance_url).json()[0]

        company_name = profile.get("companyName", symbol)
        sector = profile.get("sector", "غير معروف")
        total_assets = balance.get("totalAssets", 0)
        short_debt = balance.get("shortTermDebt", 0)
        long_debt = balance.get("longTermDebt", 0)
        cash = balance.get("cashAndCashEquivalents", 0)
        investments = balance.get("shortTermInvestments", 0)

        total_debt = short_debt + long_debt

        # فحص النشاط
        sector_lower = sector.lower()
        if any(bad in sector_lower for bad in HARAM_KEYWORDS):
            return f"""❌ غير شرعي: نشاط الشركة محرم
- الشركة: {company_name}
- النشاط: {sector}

قنوات JALWE العامة:
📌 الأسهم: https://t.me/JalweTrader
📌 العقود: https://t.me/jalweoption
📌 التعليمية: https://t.me/JalweVip
🔒 الاشتراك بالقنوات الخاصة: https://salla.sa/jalawe/category/AXlzxy
"""

        # فحص نسبة الدين
        if total_assets > 0:
            debt_ratio = total_debt / total_assets
        else:
            return f"⚠️ تعذر تقييم نسبة الدين لعدم توفر إجمالي الأصول."

        if debt_ratio > 0.33:
            return f"""❌ غير شرعي: نسبة الدين {round(debt_ratio*100, 2)}% تتجاوز 33%

قنوات JALWE العامة:
📌 الأسهم: https://t.me/JalweTrader
📌 العقود: https://t.me/jalweoption
📌 التعليمية: https://t.me/JalweVip
🔒 الاشتراك بالقنوات الخاصة: https://salla.sa/jalawe/category/AXlzxy
"""

        # فحص نسبة النقد
        cash_ratio = (cash + investments) / total_assets
        if cash_ratio > 0.49:
            return f"""❌ غير شرعي: نسبة النقد {round(cash_ratio*100, 2)}% تتجاوز 49%

قنوات JALWE العامة:
📌 الأسهم: https://t.me/JalweTrader
📌 العقود: https://t.me/jalweoption
📌 التعليمية: https://t.me/JalweVip
🔒 الاشتراك بالقنوات الخاصة: https://salla.sa/jalawe/category/AXlzxy
"""

        return f"""✅ السهم حلال (مطابق لضوابط فلتر يقين)

- الشركة: {company_name}
- النشاط: {sector}
- نسبة الدين: {round(debt_ratio*100,2)}%
- نسبة النقد: {round(cash_ratio*100,2)}%

قنوات JALWE العامة:
📌 الأسهم: https://t.me/JalweTrader
📌 العقود: https://t.me/jalweoption
📌 التعليمية: https://t.me/JalweVip
🔒 الاشتراك بالقنوات الخاصة: https://salla.sa/jalawe/category/AXlzxy
"""

    except Exception as e:
        return f"⚠️ فشل في جلب أو تحليل بيانات السهم ({symbol}): {e}"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رمز السهم مثل (AAPL أو HUMA) وسأفلتره شرعيًا حسب معايير فلتر يقين.")

# استقبال الرموز
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    if 1 <= len(symbol) <= 6:
        result = filter_stock_yaqeen_style(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("❗ أرسل رمز السهم فقط (مثال: AAPL أو TSLA)")

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
