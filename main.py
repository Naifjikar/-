import logging
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# إعداد البوت - ضع التوكن الخاص بك هنا
TOKEN = "7643817024:AAEdh2RK0iDgAYQgA5qOq3VGvDa66GMFgQk"
logging.basicConfig(level=logging.INFO)

# ترجمة القطاعات
sector_translation = {
    "Technology": "تقنية",
    "Healthcare": "الرعاية الصحية",
    "Financial Services": "الخدمات المالية",
    "Consumer Cyclical": "السلع الاستهلاكية الدورية",
    "Communication Services": "الاتصالات",
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

# دالة الفلترة عبر yfinance
def check_sharia_yahoo(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        sector_en = info.get("sector", "غير متوفر")
        sector_ar = sector_translation.get(sector_en, sector_en)
        company_name = info.get("shortName", symbol)
        debt_to_equity = info.get("debtToEquity", None)

        if sector_en == "غير متوفر" or debt_to_equity is None:
            return "⚠️ تعذر الحصول على البيانات الكافية للسهم، تأكد من الرمز أو جرب لاحقًا."

        haram_keywords = ["bank", "insurance", "alcohol", "gambling", "tobacco", "loan"]
        if any(haram in sector_en.lower() for haram in haram_keywords):
            verdict = "❌ السهم غير شرعي (نشاط محرم)"
            purification = "نسبة التطهير: 100%"
        elif debt_to_equity > 0.7:
            verdict = "❌ السهم غير شرعي (نسبة الدين مرتفعة)"
            purification = "نسبة التطهير: 100%"
        else:
            verdict = "✅ السهم حلال (حسب بيانات Yahoo)"
            purification = "نسبة التطهير التقديرية: أقل من 5%"

        message = f"""{verdict}
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
https://salla.sa/jalawe/category/AXlzxy"""
        return message

    except Exception as e:
        return f"⚠️ حدث خطأ أثناء جلب البيانات من Yahoo Finance: {e}"

# أمر البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رمز السهم (مثال: AAPL) لمعرفة حالته الشرعية (باستخدام Yahoo Finance فقط).")

# التعامل مع الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    if len(symbol) <= 6:
        result = check_sharia_yahoo(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("أرسل رمز السهم فقط (مثل AAPL أو TSLA).")

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
