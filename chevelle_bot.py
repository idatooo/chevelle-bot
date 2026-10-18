import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageEnhance, ImageOps
from aiohttp import web

BOT_TOKEN = "8967312774:AAGw3REjmW-BJRHsiRIjNOkim_tf87wCIMA"

def process_for_instagram(input_path, output_path):
    with Image.open(input_path) as img:
        img = ImageOps.exif_transpose(img)
        
        target_ratio = 4 / 5
        target_width = 1080
        target_height = 1350
        
        orig_w, orig_h = img.size
        orig_ratio = orig_w / orig_h
        
        if orig_ratio > target_ratio:
            new_w = int(orig_h * target_ratio)
            offset = (orig_w - new_w) // 2
            img = img.crop((offset, 0, offset + new_w, orig_h))
        else:
            new_h = int(orig_w / target_ratio)
            offset = (orig_h - new_h) // 2
            img = img.crop((0, offset, orig_w, offset + new_h))
            
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.15)
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.10)
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.20)
        
        img.save(output_path, "JPEG", quality=95)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "გამარჯობა! გამომიგზავნე Chevelle-ის ფოტო და მოგიმზადებ ინსტაგრამის პოსტს."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ვამუშავებ ფოტოს...")
    
    photo_file = await update.message.photo[-1].get_file()
    
    raw_path = "temp_input.jpg"
    processed_path = "temp_ready.jpg"
    
    await photo_file.download_to_drive(raw_path)
    
    process_for_instagram(raw_path, processed_path)
    
    caption_text = (
        "Pure American Muscle. 1968 Chevrolet Chevelle SS 🔥\n\n"
        "#Chevelle #ChevelleSS #1968Chevelle #ClassicCar #MuscleCar "
        "#AmericanMuscle #Restomod #V8 #Supercharged #CarCulture #ClassicChevy"
    )
    
    with open(processed_path, "rb") as ready_img:
        await update.message.reply_photo(
            photo=ready_img,
            caption=caption_text
        )
        
    if os.path.exists(raw_path):
        os.remove(raw_path)
    if os.path.exists(processed_path):
        os.remove(processed_path)

async def run_dummy_server():
    """Render-ისთვის საჭირო პატარა ვებ-სერვერი, რომ სერვისი არ გაითიშოს"""
    async def hello(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.router.add_get("/", hello)
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await run_dummy_server()
    
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Chevelle Bot გაშვებულია...")
    async with tg_app:
        await tg_app.start()
        await tg_app.updater.start_polling()
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
