import asyncio
import uuid
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_or_create_user, save_video, create_batch, update_batch_progress
from services.ai_service import generate_video_content, format_video_message, format_full_video_file
from config import PLATFORMS

WAITING_IDEA = 1
WAITING_COUNT = 2
WAITING_PLATFORM = 3


async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *إنشاء فيديو جديد*\n\n✏️ أرسل فكرة فيديوك:\n\nمثال:\n• _5 أسرار لزيادة الإنتاجية_\n• _كيف تربح من الإنترنت_",
        parse_mode='Markdown'
    )
    return WAITING_IDEA


async def receive_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idea = update.message.text.strip()
    if len(idea) < 5:
        await update.message.reply_text("❌ الفكرة قصيرة! اكتب فكرة أوضح.")
        return WAITING_IDEA
    context.user_data['idea'] = idea
    await update.message.reply_text(
        f"✅ فكرتك:\n*{idea}*\n\n📊 كم فيديو تريد؟ (1-100)",
        parse_mode='Markdown'
    )
    return WAITING_COUNT


async def receive_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text.strip())
        if count < 1 or count > 100:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("❌ اكتب رقماً بين 1 و 100")
        return WAITING_COUNT
    context.user_data['count'] = count
    keyboard = [
        [InlineKeyboardButton("🎥 يوتيوب", callback_data="plat_youtube"),
         InlineKeyboardButton("🎵 تيك توك", callback_data="plat_tiktok")],
        [InlineKeyboardButton("📸 إنستجرام", callback_data="plat_instagram"),
         InlineKeyboardButton("👥 فيسبوك", callback_data="plat_facebook")],
        [InlineKeyboardButton("🌐 جميع المنصات", callback_data="plat_all")],
    ]
    await update.message.reply_text(
        f"✅ {count} فيديو\n\n📱 اختر المنصة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAITING_PLATFORM


async def receive_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ اختر المنصة من الأزرار أعلاه")
    return WAITING_PLATFORM


async def process_videos_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data.startswith("plat_"):
        return
    platform = query.data.replace("plat_", "")
    user = update.effective_user
    idea = context.user_data.get('idea', '')
    count = context.user_data.get('count', 1)
    if not idea:
        await query.edit_message_text("❌ حدث خطأ! ابدأ من جديد /video")
        return ConversationHandler.END
    platf
async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ تم الإلغاء\n\n/video للبدء من جديد")
    return ConversationHandler.END
