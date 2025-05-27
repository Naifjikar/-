import logging
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# إعداد اللوغ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ترجمة القطاعات
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

# الفلترة الشرعية
def filter_sharia_compliance(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        balance = stock.balance_sheet

        raw_sector = info.get("sector", "غير متوفر").lower()
        sector = sector_translation.get(raw_sector, raw_sector)

        # استخراج إجمالي الدين والأصول
        try:
            total_debt = float(balance.loc["Total Debt"][0])
            total_assets = float(balance.loc["Total Assets"][0])
            debt_percentage = (total_debt / total_assets) * 100
        except:
            debt_percentage = None

        # قائمة الأنشطة المحرمة
        haram_sectors = ["bank", "alcohol", "gambling", "insurance", "tobacco", "loan"]
        if any(haram in raw_sector for haram in haram_sectors):
            verdict = "❌ السهم غير شرعي"
            notes = "نشاط محرم أو مشبوه"
            purification = "نسبة التطهير: 100%"

        elif debt_percentage is not None and debt_percentage > 30:
            verdict = "❌ السهم غير شرعي"
            notes = "نسبة الدين تتجاوز 30% من إجمالي الأصول"
            purification = "نسبة التطهير: 100%"

        else:
            verdict = "✅ السهم حلال حسب البيانات المالية"
            notes = "نشاط نظيف ونسبة الدين ضمن الضوابط"
            purification = "نسبة التطهير التقديرية: أقل من 5%"

        response = f"""{verdict}
- النشاط: {sector}
- نسبة الدين: {round(debt_percentage, 2) if debt_percentage is not None else "غير متوفرة"}%
- {purification}
- الملاحظة: {notes}

قناة JALWE العامة للأسهم:
https://t.me/JalweTrader

قناة JALWE العامة للعقود:
https://t.me/jalweoption

قناة JALWE التعليمية:
https://t.me/JalweVip

للاشتراك بالقنوات الخاصة:
https://salla.sa/jalawe/category/AXlzxy
"""
        return response

    except Exception as e:
        return f"⚠️ تعذر التحقق من البيانات: {e}"

# رسالة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في بوت فلترة الأسهم الشرعية.\n\n"
        "أرسل رمز السهم (مثل AAPL أو TSLA) وسنخبرك عن حالته الشرعية حسب البيانات المالية.\n\n"
        "قناة JALWE العامة للأسهم:\nhttps://t.me/JalweTrader\n"
        "قناة JALWE العامة للعقود:\nhttps://t.me/jalweoption\n"
        "قناة JALWE التعليمية:\nhttps://t.me/JalweVip\n"
        "للاشتراك بالقنوات الخاصة:\nhttps://salla.sa/jalawe/category/AXlzxy"
    )

# رد على الرسائل
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
