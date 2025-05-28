import yfinance as yf
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# توكن البوت
TOKEN = "7643817024:AAH7eCvHeLw6RsYI5s8fYFVoP8REdGlxGFM"

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
        sector = info.get("sector", "غير معروف")

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

        return f"""✅ السهم حلال (مطابق لضوابط فلتر يقين)

- الشركة: {company_name}
- النشاط: {sector}
- نسبة الدين: {round(debt_ratio*100, 2)}%
- نسبة النقد: {round(cash_ratio*100, 2)}%

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
