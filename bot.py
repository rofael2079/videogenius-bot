#!/usr/bin/env python3
"""
🎬 VideoGenius Bot - بوت إنتاج المحتوى بالذكاء الاصطناعي
"""

import asyncio
import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ConversationHandler
)
from config import BOT_TOKEN
from handlers.start import start_handler, help_handler
from handlers.video import (
    video_command, receive_idea, receive_count,
    receive_platform, process_videos_handler,
    cancel_handler, WAITING_IDEA, WAITING_COUNT, WAITING_PLATFORM
)
from handlers.library import library_handler, delete_video_handler
from handlers.stats import stats_handler
from handlers.batch import batch_handler, receive_batch_ideas
from database.db import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """تشغيل البوت"""
    # تهيئة قاعدة البيانات
    await init_db()
    logger.info("✅ قاعدة البيانات جاهزة")

    # إنشاء التطبيق
    app = Application.builder().token(BOT_TOKEN).build()

    # المحادثة الرئيسية لإنشاء فيديو
    video_conv = ConversationHandler(
        entry_points=[CommandHandler("video", video_command)],
        states={
            WAITING_IDEA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_idea)],
            WAITING_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_count)],
            WAITING_PLATFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_platform)],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )

    # محادثة الدفعة
    batch_conv = ConversationHandler(
        entry_points=[CommandHandler("batch", batch_handler)],
        states={
            10: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_batch_ideas)],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )

    # تسجيل الأوامر
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("library", library_handler))
    app.add_handler(video_conv)
    app.add_handler(batch_conv)

    # أزرار الإجراءات
    app.add_handler(CallbackQueryHandler(process_videos_handler, pattern="^process_"))
    app.add_handler(CallbackQueryHandler(delete_video_handler, pattern="^delete_"))
    app.add_handler(CallbackQueryHandler(library_handler, pattern="^library"))

    logger.info("🚀 البوت يعمل الآن 24/7...")
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
