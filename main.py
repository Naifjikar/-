import yfinance as yf
import pandas as pd
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "7643817024:AAH8baB7d0QllfO4PcPpbg6lTR7VdEc7r7o"

# ترجمة النشاطات
sector_translation = {
    "Technology": "تقنية",
    "Healthcare": "الرعاية الصحية",
    "Financial Services": "خدمات مالية",
    "Consumer Cyclical": "السلع الاستهلاكية",
    "Communication Services": "اتصالات",
    "Energy": "طاقة",
    "Industrials": "صناعات",
    "Real Estate": "عقارات",
    "Utilities": "خدمات عامة",
    "Materials": "مواد أساسية",
    "Consumer Defensive": "سلع استهلاكية دفاعية",
    "Basic Materials": "مواد أولية",
    "Financial": "خدمات مالية",
    "": "غير مذكور"
}

# أنشطة محرمة
banned_keywords = ["Alcohol", "Tobacco", "Gambling", "Gaming", "Adult", "Weapon", "Porn", "Cannabis", "Casino", "Brewery"]

# دالة استخراج نسبة التطهير من FMP
def get_purification_ratio(symbol):
    try:
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol.upper()}?limit=1&apikey=PDTlX9ib5N6laEnauklHAgoN8UGr12uh"
        response = requests.get(url)
        data = response.json()

        if not data or "cashAndShortTermInvestments" not in data[0] or "totalAssets" not in data[0]:
            return None

        cash = data[0]['cashAndShortTermInvestments']
        total_assets = data[0]['totalAssets']
        if total_assets == 0:
            return None

        purification_ratio = round((cash / total_assets) * 100, 2)
        return purification_ratio

    except Exception as e:
        print(f"Error fetching purification ratio: {e}")
        return None

# الفلترة الشرعية
def check_stock_sharia(symbol):
    try:
        symbol = symbol.upper()
        stock = yf.Ticker(symbol)
        balance = stock.balance_sheet
        info = stock.info

        if balance.empty:
            return f"⚠️ لم يتم العثور على بيانات مالية للسهم ({symbol})"

        total_assets = balance.loc['Total Assets'][0] if 'Total Assets' in balance.index else 0
        short_debt = balance.loc['Short Long Term Debt'][0] if 'Short Long Term Debt' in balance.index else 0
        long_debt = balance.loc['Long Term Debt'][0] if 'Long Term Debt' in balance.index else 0
        total_debt = short_debt + long_debt

        cash = balance.loc['Cash'][0] if 'Cash' in balance.index else 0
        investments = balance.loc['Short Term Investments'][0] if 'Short Term Investments' in balance.index else 0

        if total_assets == 0:
            return f"⚠️ تعذر حساب النسب لعدم توفر إجمالي الأصول."

        debt_ratio = total_debt / total_assets
        cash_ratio = (cash + investments) / total_assets

        company_name = info.get("longName", symbol)
        sector_en = info.get("sector", "غير معروف")
        industry = info.get("industry", "")

        # ترجمة القطاع
        sector_ar = sector_translation.get(sector_en, sector_en)

        # فلترة النشاط
        industry_lower = industry.lower()
        if any(bad_word.lower() in industry_lower for bad_word in banned_keywords):
            return f"""❌ غير شرعي: النشاط ({industry}) يحتوي على أنشطة محرّمة

قنوات JALWE العامة:
📌 الأسهم: https://t.me/JalweTrader
📌 العقود: https://t.me/jalweoption
📌 التعليمية: https://t.me/JalweVip
🔒 الاشتراك بالقنوات الخاصة:
https://salla.sa/jalawe/category/AXlzxy
"""

        if debt_ratio > 0.33:
            return f"""❌ غير شرعي: نسبة الدين {round(debt_ratio*100, 2)}% تتجاوز 33%

قنوات JALWE العامة:
📌 الأسهم: https://t.me/JalweTrader
📌 العقود: https://t.me/jalweoption
📌 التعليمية: https://t.me/JalweVip
🔒 الاشتراك بالقنوات الخاصة:
https://salla.sa/jalawe/category/AXlzxy
"""

        if cash_ratio > 0.49:
            return f"""❌ غير شرعي: نسبة النقد {round(cash_ratio*100, 2)}% تتجاوز 49%

قنوات JALWE العامة:
📌 الأسهم: https://t.me/JalweTrader
📌 العقود: https://t.me/jalweoption
📌 التعليمية: https://t.me/JalweVip
🔒 الاشتراك بالقنوات الخاصة:
https://salla.sa/jalawe/category/AXlzxy
"""

        # حساب نسبة التطهير من FMP
        purification_ratio = get_purification_ratio(symbol)
        purification_text = f"{purification_ratio}%" if purification_ratio is not None else "غير متوفرة"

        return f"""✅ السهم حلال (مطابق للضوابط الشرعية)

- الشركة: {company_name}
- النشاط: {sector_ar} ({industry})
- نسبة الدين: {round(debt_ratio*100, 2)}%
- نسبة النقد (نسبة التطهير): {purification_text}

قنوات JALWE العامة:
📌 الأسهم: https://t.me/JalweTrader
📌 العقود: https://t.me/jalweoption
📌 التعليمية: https://t.me/JalweVip
🔒 الاشتراك بالقنوات الخاصة:
https://salla.sa/jalawe/category/AXlzxy
"""

    except Exception as e:
        return f"⚠️ فشل في جلب أو تحليل بيانات السهم ({symbol}): {e}"

# رسالة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رمز السهم (مثل AAPL أو HUMA) وسأفلتره شرعيًا بدقة مثل فلتر يقين.")

# عند استقبال رمز سهم
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    if 1 <= len(symbol) <= 6:
        result = check_stock_sharia(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("❗ أرسل رمز السهم فقط (مثال: AAPL أو TSLA)")

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == '__main__':
    main()
