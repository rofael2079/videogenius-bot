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
        platform_info = PLATFORMS.get(p['platform'], {})
        emoji = platform_info.get('emoji', '🎬')
        platforms_text += f"  {emoji} {platform_info.get('name', p['platform'])}: {p['count']} فيديو\n"
    if not platforms_text:
        platforms_text = "  لا توجد بيانات بعد"
    recent_text = ""
    for r in stats['recent']:
        platform_info = PLATFORMS.get(r['platform'], {})
        emoji = platform_info.get('emoji', '🎬')
        title = r['title'][:40] if r['title'] else 'بدون عنوان'
        recent_text += f"  {emoji} {title}\n"
    if not recent_text:
        recent_text = "  لا توجد فيديوهات بعد"
    text = f"""
📊 *إحصائياتك*

👤 *معلوماتك:*
• الاسم: {user.full_name}
• عضو منذ: {db_user.get('joined_at', '')[:10]}

🎬 *الفيديوهات:*
• الإجمالي: {stats['total
