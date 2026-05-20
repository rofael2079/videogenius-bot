from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_or_create_user, get_global_stats


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    keyboard = [
        [InlineKeyboardButton("🎬 إنشاء فيديو", callback_data="new_video"),
         InlineKeyboardButton("📦 دفعة فيديوهات", callback_data="batch_videos")],
        [InlineKeyboardButton("📚 مكتبتي", callback_data="library"),
         InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")],
    ]
    stats = await get_global_stats()
    text = f"""
🎬 *أهلاً بك في VideoGenius Bot!*

✨ *ما أقدر أعمله لك:*
🎯 سكريبت كامل للفيديو
🎥 تقسيم المشاهد خطوة بخطوة
🖼️ وصف الثامبنيل لـ AI
📝 وصف محسّن للسيو
#️⃣ هاشتاقات احترافية
🎵 اقتراح الموسيقى
⏰ أفضل وقت النشر

📱 *المنصات:* يوتيوب | تيك توك | إنستجرام | فيسبوك

📊 *إحصائيات:* {stats['total_users']:,} مستخدم | {stats['total_videos']:,} فيديو
"""
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
❓ *دليل الاستخدام*

/start - الصفحة الرئيسية
/video - إنشاء فيديو
/batch - دفعة فيديوهات
/library - مكتبتك
/stats - إحصائياتك
/cancel - إلغاء
"""
    await update.message.reply_text(text, parse_mode='Markdown')
