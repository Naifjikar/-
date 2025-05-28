import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# التوكن الخاص بك
TOKEN = "7643817024:AAEdh2RK0iDgAYQgA5qOq3VGvDa66GMFgQk"
# API Key من FMP
API_KEY = "PDTlX9ib5N6laEnauklHAgoN8UGr12uh"

logging.basicConfig(level=logging.INFO)

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

        total_assets = balance["totalAssets"]
        total_liabilities = balance["totalLiabilities"]
        cash = balance.get("cashAndCashEquivalents", 0)
        investments = balance.get("shortTermInvestments", 0)
        revenue = income.get("revenue", 0)
        non_halal_income = 0  # تقدر تضيف تقدير لو لاحقاً صار عندك مصدر

        debt_ratio = total_liabilities / total_assets
        cash_ratio = (cash + investments) / total_assets
        non_halal_ratio = non_halal_income / revenue if revenue else 0

        if "bank" in sector.lower() or "insurance" in sector.lower():
            verdict = "❌ غير شرعي: نشاط الشركة محرم"
        elif debt_ratio > 0.33:
            verdict = f"❌ غير شرعي: نسبة الدين {round(debt_ratio*100,2)}% تتجاوز 33%"
        elif cash_ratio > 0.49:
            verdict = f"❌ غير شرعي: النقدية {round(cash_ratio*100,2)}% تتجاوز 49%"
        elif non_halal_ratio > 0.05:
            verdict = f"❌ غير شرعي: إيرادات محرمة {round(non_halal_ratio*100,2)}% تتجاوز 5%"
        else:
            verdict = f"✅ السهم حلال (مطابق لضوابط يقين)"

        return f"""📊 نتيجة الفلترة الشرعية:

{verdict}

- الشركة: {company_name}
- النشاط: {sector}
- نسبة الدين: {round(debt_ratio*100,2)}%
- نسبة النقد: {round(cash_ratio*100,2)}%

قناة JALWE العامة للأسهم  :
https://t.me/JalweTrader
قناة JALWE العامة للعقود :
https://t.me/jalweoption
قناة JALWE التعليمية :
https://t.me/JalweVip
للاشتراك بالقنوات الخاصة :
https://salla.sa/jalawe/category/AXlzxy
"""

    except Exception as e:
        return f"⚠️ فشل في جلب بيانات السهم ({symbol}): {e}"

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رمز السهم (مثال: AAPL أو HUMA) وسأقوم بفلترته شرعيًا حسب معايير فلتر يقين.")

# استقبال الرموز
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    if 1 <= len(symbol) <= 6:
        result = filter_stock_yaqeen_style(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("❗ أرسل رمز السهم فقط (مثال: AAPL أو TSLA)")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
