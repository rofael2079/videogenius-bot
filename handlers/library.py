from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_or_create_user, get_user_videos, delete_video, get_video_by_id
from services.ai_service import format_full_video_file
from config import PLATFORMS


async def library_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user = update.effective_user
        send_func = query.edit_message_text
    else:
        user = update.effective_user
        send_func = update.message.reply_text
    db_user = await get_or_create_user(telegram_id=user.id)
    videos = await get_user_videos(db_user['id'], limit=10)
    if not videos:
        await send_func("📚 *مكتبتك فارغة*\n\nابدأ بـ /video", parse_mode='Markdown')
        return
    text = f"📚 *مكتبتك* ({len(videos)} فيديو)\n\n"
    keyboard = []
    for i, video in enumerate(videos, 1):
        platform = PLATFORMS.get(video['platform'], {})
        emoji = platform.get('emoji', '🎬')
        title = video['title'][:35] if video['title'] else video['idea'][:35]
        date = video['created_at'][:10]
        text += f"{i}. {emoji} {title}\n   📅 {date}\n\n"
        keyboard.append([
            InlineKeyboard
