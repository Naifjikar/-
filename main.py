import logging
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# إعداد اللوغ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# قاموس ترجمة النشاط
sector_translation = {
    "technology": "تقنية",
    "healthcare": "الرعاية الصحية",
    "financial services": "الخدمات المالية",
    "consumer cyclical": "السلع الاستهلاكية الدورية",
    "communication services": "خدمات الاتصالات",
    "energy": "الطاقة",
    "industrials": "الصناعات",
    "real estate": "العقارات",
    "utilities": "الخدمات العامة",
    "materials": "المواد الأساسية",
    "consumer defensive": "السلع الاستهلاكية الدفاعية",
    "basic materials": "المواد الأساسية",
    "insurance": "التأمين",
    "banking": "البنوك",
    "telecom": "الاتصالات",
}

# دالة الفلترة الشرعية
def filter_sharia_compliance(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        debt_ratio = info.get("debtToEquity", 0)
        raw_sector = info.get("sector", "غير متوفر").lower()
        sector = sector_translation.get(raw_sector, raw_sector)

        haram_sectors = ["bank", "alcohol", "gambling", "insurance", "tobacco", "loan"]
        if any(haram in raw_sector for haram in haram_sectors):
            verdict = "❌ السهم غير شرعي"
            notes = "نشاط محرم أو مشبوه"
            purification = "نسبة التطهير: 100%"

        elif debt_ratio and debt_ratio > 1.0:
            verdict = "❌ السهم غير شرعي"
            notes = "نسبة الدين مرتفعة"
            purification = "نسبة التطهير: 100%"

        else:
            verdict = "✅ السهم حلال حسب البيانات المالية"
            notes = "نشاط نظيف ونسبة الدين مقبولة"
            purification = "نسبة التطهير التقديرية: أقل من 5%"

        response = f"""{verdict}
- النشاط: {sector}
- نسبة الدين: {round(debt_ratio * 100, 2)}%
- {purification}
- الملاحظة: {notes}

قنوات JALWE العامة:
- الأسهم: https://t.me/JalweTrader
- العقود: https://t.me/jalweoption
- التعليمية: https://t.me/JalweVip
"""
        return response

    except Exception as e:
        return f"⚠️ تعذر التحقق من البيانات: {e}"

# استقبال الرسائل من المستخدمين
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    if len(symbol) <= 6:
        result = filter_sharia_compliance(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("أرسل رمز السهم فقط (مثال: AAPL، TSLA).")

# توكن البوت
TOKEN = "7643817024:AAGR3pno8R_IpQHtq1ioTwkPxHqY6uFxNJY"

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
