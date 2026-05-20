import asyncio
import uuid
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_or_create_user, save_video, create_batch, update_batch_progress
from services.ai_service import generate_video_content, generate_batch_ideas, format_full_video_file
from config import PLATFORMS

WAITING_BATCH_IDEAS = 10


async def batch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📦 *إنتاج دفعة فيديوهات*\n\n"
        "أرسل بالصيغة دي:\n"
        "*الموضوع | العدد | المنصة*\n\n"
        "مثال:\n"
        "`الصحة والرياضة | 20 | youtube`\n"
        "`ريادة الأعمال | 50 | tiktok`\n\n"
        "المنصات: youtube, tiktok, instagram, facebook, all",
        parse_mode='Markdown'
    )
    return WAITING_BATCH_IDEAS


async def receive_batch_ideas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = [p.strip() for p in text.split('|')]
    if len(parts) != 3:
        await update.message.reply_text(
            "❌ اكتب هكذا:\n`الموضوع | العدد | المنصة`",
            parse_mode='Markdown'
        )
        return WAITING_BATCH_IDEAS
    topic = parts[0]
    try:
        count = int(parts[1])
        if count < 1 or count > 100:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("❌ العدد بين 1 و 100")
        return WAITING_BATCH_IDEAS
    platform = parts[2].lower().strip()
    if platform not in PLATFORMS:
        await update.message.reply_text(f"❌ المنصات المتاحة: {', '.join(PLATFORMS.keys())}")
        return WAITING_BATCH_IDEAS
    platform_info = PLATFORMS[platform]
    user = update.effective_user
    db_user = await get_or_create_user(telegram_id=user.id, username=user.username, full_name=user.full_name)
    progress_msg = await update.message.reply_text(
        f"🚀 *بدأ الإنتاج!*\n\n📌 {topic}\n🎬 {count} فيديو\n📱 {platform_info['name']}\n\n⚡ جاري توليد الأفكار...",
        parse_mode='Markdown'
    )
    batch_id = str(uuid.uuid4())[:8]
    await create_batch(batch_id, db_user['id'], count)
    try:
        ideas = await generate_batch_ideas(topic, count)
        while len(ideas) < count:
            ideas.extend(ideas[:count - len(ideas)])
        ideas = ideas[:count]
        await progress_msg.edit_text(
            f"✅ تم توليد {len(ideas)} فكرة!\n\n⚡ جاري الإنتاج...\n{'░' * 20} 0%",
            parse_mode='Markdown'
        )
        success_count = 0
        for i, idea in enumerate(ideas, 1):
            try:
                video_data = await generate_video_content(idea, platform, i)
                await save_video(db_user['id'], video_data, batch_id)
                full_content = format_full_video_file(video_data)
                file_bytes = BytesIO(full_content.encode('utf-8'))
                await context.bot.send_document(
                    chat_id=user.id, document=file_bytes,
                    filename=f"فيديو_{i}.txt",
                    caption=f"✅ {i}/{count} - {idea[:50]}"
                )
                success_count += 1
                await update_batch_progress(batch_id, success_count)
                if i % 5 == 0:
                    progress = int(i / count * 20)
                    bar = '▓' * progress + '░' * (20 - progress)
                    try:
                        await progress_msg.edit_text(
                            f"⚡ *جاري الإنتاج...*\n\n{bar} {int(i/count*100)}%\n{i}/{count} فيديو",
                            parse_mode='Markdown'
                        )
                    except:
                        pass
                await asyncio.sleep(1.5)
            except Exception as e:
                await context.bot.send_message(chat_id=user.id, text=f"⚠️ تخطي {i}: {str(e)[:100]}")
        await update_batch_progress(batch_id, success_count, 'completed')
        await context.bot.send_message(
            chat_id=user.id,
            text=f"🎉 *اكتمل الإنتاج!*\n\n✅ {success_count}/{count} فيديو\n📌 {topic}\n📦 رقم الدفعة: {batch_id}",
            parse_mode='Markdown'
        )
    except Exception as e:
        await context.bot.send_message(chat_id=user.id, text=f"❌ خطأ: {str(e)[:200]}")
    return ConversationHandler.END
