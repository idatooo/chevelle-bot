import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageEnhance, ImageOps

BOT_TOKEN = "8967312774:AAFykI-Ir0_PM4VWMiVkf3ICdwinY6I3VlQ"

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

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Chevelle Bot გაშვებულია...")
    app.run_polling()
