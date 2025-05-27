import logging
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# إعداد اللوغ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# دالة الفلترة الشرعية
def filter_sharia_compliance(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # استخراج البيانات
        debt_ratio = info.get("debtToEquity", 0)
        sector = info.get("sector", "غير متوفر").lower()

        # فلترة النشاطات المحرمة
        haram_sectors = ["bank", "alcohol", "gambling", "insurance", "tobacco", "loan"]
        if any(haram in sector for haram in haram_sectors):
            return f"""❌ السهم غير شرعي
- النشاط: {sector.title()}
- نسبة الدين: {round(debt_ratio * 100, 2)}%
- نسبة التطهير التقديرية: تتجاوز 5%"""

        # التحقق من نسبة الدين
        if debt_ratio and debt_ratio > 1.0:
            return f"""❌ السهم غير شرعي (نسبة الدين مرتفعة)
- النشاط: {sector.title()}
- نسبة الدين: {round(debt_ratio * 100, 2)}%
- نسبة التطهير التقديرية: قد تتجاوز 5%"""

        # إذا كل شيء سليم
        return f"""✅ السهم حلال حسب البيانات المالية
- النشاط: {sector.title()}
- نسبة الدين: {round(debt_ratio * 100, 2)}%
- نسبة التطهير التقديرية: أقل من 5%"""

    except Exception as e:
        return f"⚠️ تعذر التحقق من البيانات: {e}"

# الدالة التي تتعامل مع الرسائل
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
