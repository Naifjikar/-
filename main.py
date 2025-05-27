import logging
import requests
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# إعداد اللوغ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

API_KEY = "PDTlX9ib5N6laEnauklHAgoN8UGr12uh"

# ترجمة القطاعات
sector_translation = {
    "Technology": "تقنية",
    "Healthcare": "الرعاية الصحية",
    "Financial Services": "الخدمات المالية",
    "Consumer Cyclical": "السلع الاستهلاكية الدورية",
    "Communication Services": "خدمات الاتصالات",
    "Energy": "الطاقة",
    "Industrials": "الصناعات",
    "Real Estate": "العقارات",
    "Utilities": "الخدمات العامة",
    "Materials": "المواد الأساسية",
    "Consumer Defensive": "السلع الدفاعية",
    "Basic Materials": "المواد الأساسية",
    "Insurance": "التأمين",
    "Banks": "البنوك",
    "Telecom": "الاتصالات",
}

# الفلترة الشرعية
def filter_sharia_compliance(symbol):
    try:
        # 1. المحاولة عبر FMP
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={API_KEY}"
        balance_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?limit=1&apikey={API_KEY}"

        profile = requests.get(profile_url).json()
        balance = requests.get(balance_url).json()

        if profile and balance:
            sector_en = profile[0].get("sector", "غير متوفر")
            sector_ar = sector_translation.get(sector_en, sector_en)
            company_name = profile[0].get("companyName", symbol)

            total_debt = balance[0].get("totalDebt", 0)
            total_assets = balance[0].get("totalAssets", 0)

            if not total_assets:
                raise Exception("No asset data")

            debt_ratio = (total_debt / total_assets) * 100
            haram_keywords = ["bank", "insurance", "alcohol", "gambling", "tobacco", "loan"]

            if any(haram in sector_en.lower() for haram in haram_keywords):
                verdict = "❌ السهم غير شرعي (نشاط محرم)"
                purification = "نسبة التطهير: 100%"
            elif debt_ratio > 30:
                verdict = "❌ السهم غير شرعي (نسبة الدين > 30%)"
                purification = "نسبة التطهير: 100%"
            else:
                verdict = "✅ السهم حلال حسب المعايير الشرعية"
                purification = "نسبة التطهير التقديرية: أقل من 5%"

            return f"""{verdict}
- الشركة: {company_name}
- النشاط: {sector_ar}
- نسبة الدين: {round(debt_ratio, 2)}%
- {purification}

قناة JALWE العامة للأسهم:
https://t.me/JalweTrader

قناة JALWE العامة للعقود:
https://t.me/jalweoption

قناة JALWE التعليمية:
https://t.me/JalweVip

للاشتراك بالقنوات الخاصة:
https://salla.sa/jalawe/category/AXlzxy
"""

        # 2. إذا فشل FMP → جلب البيانات من Yahoo
        stock = yf.Ticker(symbol)
        info = stock.info

        sector_en = info.get("sector", "غير متوفر")
        sector_ar = sector_translation.get(sector_en, sector_en)
        company_name = info.get("shortName", symbol)
        debt_to_equity = info.get("debtToEquity", 0)

        haram_keywords = ["bank", "insurance", "alcohol", "gambling", "tobacco", "loan"]
        if any(haram in sector_en.lower() for haram in haram_keywords):
            verdict = "❌ السهم غير شرعي (نشاط محرم)"
            purification = "نسبة التطهير: 100%"
        elif debt_to_equity > 0.7:
            verdict = "❌ السهم غير شرعي (نسبة الدين مرتفعة)"
            purification = "نسبة التطهير: 100%"
        else:
            verdict = "✅ السهم حلال (تقديريًا حسب بيانات Yahoo)"
            purification = "نسبة التطهير التقديرية: أقل من 5%"

        return f"""{verdict}
- الشركة: {company_name}
- النشاط: {sector_ar}
- نسبة الدين (تقريبية): {round(debt_to_equity * 100, 2)}%
- {purification}

قناة JALWE العامة للأسهم:
https://t.me/JalweTrader

قناة JALWE العامة للعقود:
https://t.me/jalweoption

قناة JALWE التعليمية:
https://t.me/JalweVip

للاشتراك بالقنوات الخاصة:
https://salla.sa/jalawe/category/AXlzxy
"""

    except Exception as e:
        return f"⚠️ تعذر جلب البيانات أو السهم غير مدعوم: {e}"

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في بوت فلترة الأسهم الشرعية.\n\n"
        "أرسل رمز السهم (مثل AAPL أو TSLA) وسنخبرك عن حالته الشرعية بدقة.\n\n"
        "قناة JALWE العامة للأسهم:\nhttps://t.me/JalweTrader\n"
        "قناة JALWE العامة للعقود:\nhttps://t.me/jalweoption\n"
        "قناة JALWE التعليمية:\nhttps://t.me/JalweVip\n"
        "للاشتراك بالقنوات الخاصة:\nhttps://salla.sa/jalawe/category/AXlzxy"
    )

# استقبال الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    if len(symbol) <= 6:
        result = filter_sharia_compliance(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("أرسل رمز السهم فقط (مثال: AAPL، TSLA).")

# تشغيل البوت
TOKEN = "7643817024:AAGR3pno8R_IpQHtq1ioTwkPxHqY6uFxNJY"
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
