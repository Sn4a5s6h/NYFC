import logging
import asyncio
import aiohttp
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from serpapi import GoogleSearch
import wikipediaapi

# إعدادات البوت
BOT_TOKEN = "7195841693:AAEGsZXGnGKZrxoRKsnRjgp9yD78y6k4hCo"
SERP_API_KEY = "d4b1933615cfb7ce0d34ba0fb5b156ed708342ad2c875919df9c60ffcea31592"

# إعداد ويكيبيديا
wiki_wiki = wikipediaapi.Wikipedia(user_agent="MyWikipediaBot/1.0 (fodxwwf@telegmail.com)", language="ar")

# إعداد سجل الأخطاء
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def start(update: Update, context: CallbackContext) -> None:
    """الرد على أمر /start"""
    await update.message.reply_text("👋 مرحبًا! أرسل لي كلمة وسأبحث عنها في جوجل وويكيبيديا، مع إمكانية تنزيل الصور! 📷")


async def search_google(query: str) -> tuple:
    """البحث في جوجل عبر SerpAPI"""
    params = {
        "q": query,
        "location": "Saudi Arabia",
        "hl": "ar",
        "gl": "sa",
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    if "organic_results" in results:
        response = "\n".join([f"{r['title']}: {r['link']}" for r in results["organic_results"][:5]])
    else:
        response = "❌ لم أجد نتائج في جوجل."

    # البحث عن الصور
    image_url = None
    if "inline_images" in results:
        image_url = results["inline_images"][0]["original"]  # استخراج أول صورة

    return response, image_url


async def search_wikipedia(query: str) -> str:
    """البحث في ويكيبيديا"""
    page = wiki_wiki.page(query)
    return page.summary[:1000] if page.exists() else "❌ لم أجد معلومات في ويكيبيديا."


async def download_image(url: str, filename: str) -> str:
    """تنزيل الصورة من الرابط وحفظها"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, "wb") as f:
                    f.write(await resp.read())
                return filename
    return None


async def handle_message(update: Update, context: CallbackContext) -> None:
    """معالجة الرسائل العادية"""
    query = update.message.text
    await update.message.reply_text(f"🔍 جاري البحث عن: {query}...")

    google_results, image_url = await search_google(query)
    wiki_results = await search_wikipedia(query)

    response = f"🔍 **نتائج البحث في جوجل:**\n{google_results}\n\n📖 **ملخص ويكيبيديا:**\n{wiki_results}"
    await update.message.reply_text(response, parse_mode="Markdown")

    # تنزيل وإرسال الصورة إذا وجدت
    if image_url:
        image_path = f"{query}.jpg"
        downloaded = await download_image(image_url, image_path)
        if downloaded:
            await update.message.reply_photo(photo=open(image_path, "rb"))
            os.remove(image_path)  # حذف الصورة بعد إرسالها


def main():
    """تشغيل البوت"""
    app = Application.builder().token(BOT_TOKEN).build()

    # أوامر البوت
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تشغيل البوت
    print("✅ البوت يعمل الآن!")
    app.run_polling()


if __name__ == "__main__":
    main()
