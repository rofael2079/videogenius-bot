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
            InlineKeyboardButton(f"📥 #{video['id']}", callback_data=f"download_{video['id']}"),
            InlineKeyboardButton(f"🗑️ #{video['id']}", callback_data=f"delete_{video['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔄 تحديث", callback_data="library")])
    try:
        await send_func(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except Exception:
        await update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def delete_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    video_id = int(query.data.replace("delete_", ""))
    keyboard = [[
        InlineKeyboardButton("✅ نعم", callback_data=f"confirm_delete_{video_id}"),
        InlineKeyboardButton("❌ لا", callback_data="library")
    ]]
    await query.edit_message_text(
        f"⚠️ حذف الفيديو #{video_id}؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def download_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    video_id = int(query.data.replace("download_", ""))
    video = await get_video_by_id(video_id)
    if not video:
        await query.edit_message_text("❌ الفيديو غير موجود!")
        return
    full_content = format_full_video_file(video)
    file_bytes = BytesIO(full_content.encode('utf-8'))
    await context.bot.send_document(
        chat_id=update.effective_user.id,
        document=file_bytes,
        filename=f"فيديو_{video_id}.txt",
        caption=f"📁 فيديو #{video_id} ✅"
    )
