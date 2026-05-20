from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_or_create_user, get_user_stats
from config import PLATFORMS


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = await get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    stats = await get_user_stats(db_user['id'])
    platforms_text = ""
    for p in stats['platforms']:
        info = PLATFORMS.get(p['platform'], {})
        emoji = info.get('emoji', '')
        name = info.get('name', p['platform'])
        platforms_text += f"  {emoji} {name}: {p['count']}\n"
    if not platforms_text:
        platforms_text = "  لا توجد بيانات"
    recent_text = ""
    for r in stats['recent']:
        info = PLATFORMS.get(r['platform'], {})
        emoji = info.get('emoji', '')
        title = r['title'][:40] if r['title'] else 'بدون عنوان'
        recent_text += f"  {emoji} {title}\n"
    if not recent_text:
        recent_text = "  لا توجد فيديوهات"
    total = stats['total']
    today = stats['today']
    joined = db_user.get('joined_at', '')[:10]
    text = (
        "📊 احصائياتك\n\n"
        f"👤 الاسم: {user.full_name}\n"
        f"📅 عضو منذ: {joined}\n\n"
        f"🎬 الاجمالي: {total}\n"
        f"📅 اليوم: {today}\n\n"
        f"📱 المنصات:\n{platforms_text}\n"
        f"🕐 الاخيرة:\n{recent_text}"
    )
    await update.message.reply_text(text)
