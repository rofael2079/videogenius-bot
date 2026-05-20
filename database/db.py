import aiosqlite
import json
from datetime import datetime
from config import DATABASE_URL


async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                joined_at TEXT DEFAULT (datetime('now')),
                total_videos INTEGER DEFAULT 0,
                last_active TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                idea TEXT NOT NULL,
                platform TEXT NOT NULL,
                title TEXT,
                script TEXT,
                description TEXT,
                hashtags TEXT,
                thumbnail_prompt TEXT,
                scenes TEXT,
                music_suggestion TEXT,
                duration_estimate TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now')),
                batch_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS batches (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                total_videos INTEGER DEFAULT 0,
                completed_videos INTEGER DEFAULT 0,
                status TEXT DEFAULT 'processing',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        await db.commit()


async def get_or_create_user(telegram_id, username=None, full_name=None):
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = await cursor.fetchone()
        if not user:
            await db.execute("INSERT INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
                (telegram_id, username, full_name))
            await db.commit()
            cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            user = await cursor.fetchone()
        else:
            await db.execute("UPDATE users SET last_active = datetime('now'), username = ?, full_name = ? WHERE telegram_id = ?",
                (username, full_name, telegram_id))
            await db.commit()
        return dict(user)


async def save_video(user_id, video_data, batch_id=None):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("""
            INSERT INTO videos 
            (user_id, idea, platform, title, script, description, hashtags, 
             thumbnail_prompt, scenes, music_suggestion, duration_estimate, status, batch_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?)
        """, (
            user_id, video_data.get('idea',''), video_data.get('platform',''),
            video_data.get('title',''), video_data.get('script',''),
            video_data.get('description',''), video_data.get('hashtags',''),
            video_data.get('thumbnail_prompt',''),
            json.dumps(video_data.get('scenes',[]), ensure_ascii=False),
            video_data.get('music_suggestion',''), video_data.get('duration_estimate',''),
            batch_id
        ))
        video_id = cursor.lastrowid
        await db.execute("UPDATE users SET total_videos = total_videos + 1 WHERE id = ?", (user_id,))
        await db.commit()
        return video_id


async def get_user_videos(user_id, limit=10, offset=0):
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM videos WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset))
        videos = await cursor.fetchall()
        return [dict(v) for v in videos]


async def get_video_by_id(video_id):
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        video = await cursor.fetchone()
        return dict(video) if video else None


async def delete_video(video_id, user_id):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("DELETE FROM videos WHERE id = ? AND user_id = ?", (video_id, user_id))
        await db.commit()


async def get_user_stats(user_id):
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT COUNT(*) as total FROM videos WHERE user_id = ?", (user_id,))
        total = (await cursor.fetchone())['total']
        cursor = await db.execute("SELECT COUNT(*) as today FROM videos WHERE user_id = ? AND DATE(created_at) = DATE('now')", (user_id,))
        today = (await cursor.fetchone())['today']
        cursor = await db.execute("SELECT platform, COUNT(*) as count FROM videos WHERE user_id = ? GROUP BY platform", (user_id,))
        platforms = await cursor.fetchall()
        cursor = await db.execute("SELECT title, platform, created_at FROM videos WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (user_id,))
        recent = await cursor.fetchall()
        return {'total': total, 'today': today, 'platforms': [dict(p) for p in platforms], 'recent': [dict(r) for r in recent]}


async def create_batch(batch_id, user_id, total):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("INSERT INTO batches (id, user_id, total_videos, status) VALUES (?, ?, ?, 'processing')",
            (batch_id, user_id, total))
        await db.commit()


async def update_batch_progress(batch_id, completed, status='processing'):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("UPDATE batches SET completed_videos = ?, status = ? WHERE id = ?",
            (completed, status, batch_id))
        await db.commit()


async def get_global_stats():
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT COUNT(*) as total FROM users")
        total_users = (await cursor.fetchone())['total']
        cursor = await db.execute("SELECT COUNT(*) as total FROM videos")
        total_videos = (await cursor.fetchone())['total']
        return {'total_users': total_users, 'total_videos': total_videos}
