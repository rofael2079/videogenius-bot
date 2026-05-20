# ⚙️ إعدادات البوت - قم بتعديل هذه القيم
import os

# 🔑 مفاتيح API (اضبطها في ملف .env أو مباشرة هنا)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY_HERE")

# 🗄️ قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL", "videos.db")

# 🎬 إعدادات الإنتاج
MAX_VIDEOS_PER_BATCH = 100
MAX_VIDEOS_FREE = 10

# 📱 المنصات المدعومة
PLATFORMS = {
    "youtube": {
        "name": "يوتيوب",
        "emoji": "🎥",
        "aspect_ratio": "16:9",
        "max_duration": "10 دقائق",
        "hashtags_count": 15,
        "description_max": 5000,
    },
    "tiktok": {
        "name": "تيك توك",
        "emoji": "🎵",
        "aspect_ratio": "9:16",
        "max_duration": "3 دقائق",
        "hashtags_count": 10,
        "description_max": 2200,
    },
    "instagram": {
        "name": "إنستجرام",
        "emoji": "📸",
        "aspect_ratio": "9:16",
        "max_duration": "90 ثانية",
        "hashtags_count": 30,
        "description_max": 2200,
    },
    "facebook": {
        "name": "فيسبوك",
        "emoji": "👥",
        "aspect_ratio": "16:9",
        "max_duration": "240 دقيقة",
        "hashtags_count": 5,
        "description_max": 63206,
    },
    "all": {
        "name": "جميع المنصات",
        "emoji": "🌐",
        "aspect_ratio": "متعدد",
        "max_duration": "متنوع",
        "hashtags_count": 20,
        "description_max": 2200,
    }
}
