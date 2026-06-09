import os
import logging
import asyncio
from dotenv import load_dotenv
from groq import Groq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ChatAction
 
load_dotenv()
 
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
 
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
 
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    logger.error("❌ Ошибка: проверь TELEGRAM_BOT_TOKEN и GROQ_API_KEY")
    exit(1)
 
client = Groq(api_key=GROQ_API_KEY)
 
COMPANY_DATA = {
    "requisites": {
        "name": "Центр Красок #1",
        "legal_name": "ТОО «Экспонента1»",
        "bin": "220940047271",
        "oked": "47521",
        "industry": "Розничная торговля лакокрасочными материалами",
        "website": "https://centr-krasok.kz"
    },
    "brands": ["Dulux", "Tikkurila", "Hammerite", "Sadolin", "Beckers", "Tex", "Ореол", "Krasfor"],
    "tinting": {
        "available": True,
        "shades": "45 000 оттенков",
        "price": "бесплатно при покупке краски"
    },
    "addresses": {
        "almaty": "просп. Жибек Жолы, 135, Алматы",
        "astana": "ул. Мангилик Ел, 29/2, Астана"
    },
    "hours": {
        "weekdays": "10:00–20:00",
        "saturday": "10:00–14:00",
        "sunday": "выходной"
    },
    "delivery": {
        "schedule": "Пн–Пт: 10:00–20:00, Сб: 10:00–14:00, Вс — выходной",
        "deadline_before_12": "доставка на след. день с 10:00 до 15:00",
        "deadline_after_12": "доставка на след. день с 15:00 до 18:00",
        "phone": "+7 778 061 5000",
        "email": "info.online@abis.kz"
    },
    "contacts": {
        "phone": "+7 (777) 292-84-01",
        "delivery_phone": "+7 778 061 5000",
        "email": "info@centr-krasok.kz",
        "instagram": "https://instagram.com/centr_krasok"
    },
    "products": {
        "categories": [
            "Интерьерные краски",
            "Фасадные краски",
            "Краски по дереву",
            "Краски по металлу",
            "Декоративные покрытия",
            "Грунтовки и шпатлёвки",
            "Лаки и масла"
        ]
    }
}
 
STRUCTURED_KNOWLEDGE = f"""
КОМПАНИЯ: {COMPANY_DATA['requisites']['name']}
ЮР.ЛИЦО: {COMPANY_DATA['requisites']['legal_name']} (БИН {COMPANY_DATA['requisites']['bin']})
САЙТ: {COMPANY_DATA['requisites']['website']}
 
АДРЕСА:
- Алматы: {COMPANY_DATA['addresses']['almaty']}
- Астана: {COMPANY_DATA['addresses']['astana']}
 
ЧАСЫ РАБОТЫ:
- Будни: {COMPANY_DATA['hours']['weekdays']}
- Суббота: {COMPANY_DATA['hours']['saturday']}
- Воскресенье: {COMPANY_DATA['hours']['sunday']}
 
ДОСТАВКА:
- График: {COMPANY_DATA['delivery']['schedule']}
- При заказе до 12:00: {COMPANY_DATA['delivery']['deadline_before_12']}
- При заказе после 12:00: {COMPANY_DATA['delivery']['deadline_after_12']}
- Телефон доставки: {COMPANY_DATA['delivery']['phone']}
- Email доставки: {COMPANY_DATA['delivery']['email']}
 
КОНТАКТЫ:
- Основной: {COMPANY_DATA['contacts']['phone']}
- Email: {COMPANY_DATA['contacts']['email']}
- Instagram: {COMPANY_DATA['contacts']['instagram']}
 
ПРОДУКТЫ: {', '.join(COMPANY_DATA['products']['categories'])}
БРЕНДЫ: {', '.join(COMPANY_DATA['brands'])}
КОЛЕРОВКА: {COMPANY_DATA['tinting']['shades']} оттенков, {COMPANY_DATA['tinting']['price']}
"""
 
SYSTEM_PROMPT = f"""Ты — дружелюбный AI-ассистент магазина «Центр Красок #1».
 
ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе данных ниже.
2. Если не знаешь — скажи: «Уточните у менеджера: {COMPANY_DATA['contacts']['phone']}»
3. Отвечай на языке пользователя.
4. Будь вежливым и лаконичным.
 
ИНФОРМАЦИЯ О КОМПАНИИ:
{STRUCTURED_KNOWLEDGE}
"""
 
user_histories = {}
 
 
async def send_qrcode(chat_id, context):
    try:
        with open("qrcode.png", "rb") as f:
            await context.bot.send_photo(chat_id, f, caption="🔗 QR-код на сайт Центр Красок #1")
    except FileNotFoundError:
        await context.bot.send_message(chat_id, f"🔗 Сайт: {COMPANY_DATA['requisites']['website']}")
 
 
async def send_colors(chat_id, context):
    colors_text = """🎨 Популярные цвета красок:
 
⬜️ MASTER White — чистый белый
◻️ Snow White — тёплый белый
▫️ Arctic White — холодный белый
🟫 Кремовый — нежный, тёплый
🏾 Бежевый — универсальный
⚪ Серый жемчуг — элегантный
⬛ Графит — глубокий тёмный
 
💡 Совет: Приезжайте в шоурум — увидите все оттенки вживую!"""
    await context.bot.send_message(chat_id, colors_text)
 
 
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎨 О компании", callback_data="about")],
        [InlineKeyboardButton("🚚 Доставка", callback_data="delivery")],
        [InlineKeyboardButton("📍 Адреса и контакты", callback_data="contacts")],
        [InlineKeyboardButton("🛒 Продукты и бренды", callback_data="products")],
        [InlineKeyboardButton("🔗 QR-код на сайт", callback_data="qrcode")],
        [InlineKeyboardButton("🎨 Цвета красок", callback_data="colors")],
    ]
    return InlineKeyboardMarkup(keyboard)
 
 
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id
 
    if data == "qrcode":
        await send_qrcode(chat_id, context)
        return
    elif data == "colors":
        await send_colors(chat_id, context)
        return
 
    responses = {
        "about": f"🏢 {COMPANY_DATA['requisites']['name']}\n\n{COMPANY_DATA['requisites']['legal_name']}\nБИН: {COMPANY_DATA['requisites']['bin']}\nОКЭД: {COMPANY_DATA['requisites']['oked']}\n\n🎨 Интернет-магазин лакокрасочных материалов премиум-сегмента. Официальный дистрибьютор европейских брендов в Казахстане.\n\n🌐 {COMPANY_DATA['requisites']['website']}",
        "delivery": f"🚚 Доставка\n\n📅 График: {COMPANY_DATA['delivery']['schedule']}\n\n⏰ Сроки:\n• До 12:00 → {COMPANY_DATA['delivery']['deadline_before_12']}\n• После 12:00 → {COMPANY_DATA['delivery']['deadline_after_12']}\n\n📞 Служба доставки: {COMPANY_DATA['delivery']['phone']}\n✉️ {COMPANY_DATA['delivery']['email']}",
        "contacts": f"📍 Адреса и контакты\n\n🏢 Алматы: {COMPANY_DATA['addresses']['almaty']}\n🏢 Астана: {COMPANY_DATA['addresses']['astana']}\n\n⏰ Часы работы: {COMPANY_DATA['hours']['weekdays']} (будни), {COMPANY_DATA['hours']['saturday']} (сб), {COMPANY_DATA['hours']['sunday']} (вс)\n\n📞 {COMPANY_DATA['contacts']['phone']}\n✉️ {COMPANY_DATA['contacts']['email']}\n📷 {COMPANY_DATA['contacts']['instagram']}",
        "products": f"🛒 Ассортимент\n\nКатегории:\n• " + "\n• ".join(COMPANY_DATA['products']['categories']) + f"\n\n🏷️ Бренды:\n• " + "\n• ".join(COMPANY_DATA['brands']) + f"\n\n🎨 Колеровка: {COMPANY_DATA['tinting']['shades']} оттенков, {COMPANY_DATA['tinting']['price']}",
    }
    text = responses.get(data, "Выберите пункт из меню")
    await query.edit_message_text(text, reply_markup=get_main_keyboard())
 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()
    if not user_text:
        return
 
    if any(word in user_text.lower() for word in ["белый", "цвет краски", "какой цвет", "оттенок", "белая"]):
        await send_colors(chat_id, context)
        return
 
    logger.info(f"User {user_id}: {user_text}")
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
 
    if user_id not in user_histories:
        user_histories[user_id] = []
    user_histories[user_id].append({"role": "user", "content": user_text})
    if len(user_histories[user_id]) > 10:
        user_histories[user_id] = user_histories[user_id][-10:]
 
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_histories[user_id]
 
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
        user_histories[user_id].append({"role": "assistant", "content": reply})
    except Exception as e:
        logger.error(f"Ошибка Groq: {e}")
        reply = f"⚠️ Техническая ошибка. Позвоните: {COMPANY_DATA['contacts']['phone']}"
 
    await update.message.reply_text(reply, reply_markup=get_main_keyboard())
 
 
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    welcome = "🎨 *Центр Красок #1*\n\nПривет! Я AI-помощник. Выбери интересующий раздел:"
    await update.message.reply_text(welcome, parse_mode="Markdown", reply_markup=get_main_keyboard())
 
 
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
 
    logger.info("✅ Бот запущен")
 
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
 
    # Держим бота живым
    while True:
        await asyncio.sleep(3600)
 
 
if __name__ == "__main__":
    asyncio.run(main())