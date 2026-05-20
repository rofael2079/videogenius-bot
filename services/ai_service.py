import anthropic
import json
import re
from config import ANTHROPIC_API_KEY, PLATFORMS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


async def generate_video_content(idea, platform, video_number=1):
    platform_info = PLATFORMS.get(platform, PLATFORMS['youtube'])
    prompt = f"""أنت خبير محتوى رقمي متخصص في إنتاج فيديوهات ناجحة.

الفكرة: "{idea}"
المنصة: {platform_info['name']}
الأبعاد: {platform_info['aspect_ratio']}
الهاشتاقات: {platform_info['hashtags_count']}

أنتج JSON فقط بدون أي نص آخر:

{{
  "title": "عنوان جذاب 60 حرف",
  "hook": "جملة افتتاحية صادمة خلال 3 ثوانٍ",
  "duration_estimate": "المدة المقدرة",
  "script": "السكريبت الكامل للفيديو",
  "scenes": [
    {{
      "scene_number": 1,
      "duration": "مدة بالثواني",
      "visual": "وصف المشهد",
      "narration": "ما يقوله المقدم",
      "text_overlay": "النص على الشاشة",
      "transition": "نوع الانتقال"
    }}
  ],
  "thumbnail_prompt": "وصف الثامبنيل لـ AI",
  "description": "وصف محسّن للسيو",
  "hashtags": "الهاشتاقات مفصولة بمسافات",
  "tags": ["كلمات مفتاحية"],
  "music_suggestion": "نوع الموسيقى",
  "color_palette": "لوحة الألوان",
  "call_to_action": "نداء الإجراء",
  "best_posting_time": "أفضل وقت للنشر",
  "target_audience": "الجمهور المستهدف",
  "engagement_tips": ["3 نصائح للتفاعل"]
}}"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    data = json.loads(text.strip())
    data['idea'] = idea
    data['platform'] = platform
    return data


async def generate_batch_ideas(main_topic, count):
    prompt = f"""أنت خبير محتوى رقمي.
الموضوع: "{main_topic}"
المطلوب: {count} فكرة فيديو مختلفة ومتنوعة.

أجب بـ JSON فقط:
{{"ideas": ["الفكرة الأولى", "الفكرة الثانية", ...]}}

القواعد:
- كل فكرة مختلفة تماماً
- متنوعة (تعليمية، ترفيهية، نصائح، مقارنات)
- واضحة وقابلة للتنفيذ"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    data = json.loads(text.strip())
    return data.get('ideas', [])


def format_video_message(video_data, video_num=1, total=1):
    platform_emoji = PLATFORMS.get(video_data.get('platform', 'youtube'), {}).get('emoji', '🎬')
    scenes = video_data.get('scenes', [])
    scenes_text = ""
    for scene in scenes[:3]:
        scenes_text += f"\n  🎬 مشهد {scene.get('scene_number','')}: {scene.get('visual','')[:60]}"
    tips = "\n".join([f"  • {t}" for t in video_data.get('engagement_tips', [])])
    return f"""
{'='*35}
🎬 فيديو {video_num}/{total} {platform_emoji}
{'='*35}

📌 *العنوان:*
{video_data.get('title','')}

⚡ *Hook:*
{video_data.get('hook','')}

⏱️ المدة: {video_data.get('duration_estimate','')}
👥 الجمهور: {video_data.get('target_audience','')}

📝 *السكريبت:*
{video_data.get('script','')[:800]}...

🎥 *المشاهد:*{scenes_text}

🎵 الموسيقى: {video_data.get('music_suggestion','')}
📣 CTA: {video_data.get('call_to_action','')}
⏰ أفضل وقت: {video_data.get('best_posting_time','')}

💡 *نصائح التفاعل:*
{tips}
"""


def format_full_video_file(video_data):
    scenes = video_data.get('scenes', [])
    scenes_text = ""
    for s in scenes:
        scenes_text += f"""
━━ مشهد {s.get('scene_number','')} ({s.get('duration','')}) ━━
📹 البصري: {s.get('visual','')}
🎙️ السرد: {s.get('narration','')}
📝 نص الشاشة: {s.get('text_overlay','')}
➡️ الانتقال: {s.get('transition','')}
"""
    return f"""
🎬 VideoGenius Bot - محتوى الفيديو الكامل
{'='*50}
📌 العنوان: {video_data.get('title','')}
🎯 الفكرة: {video_data.get('idea','')}
📱 المنصة: {video_data.get('platform','')}
⏱️ المدة: {video_data.get('duration_estimate','')}
👥 الجمهور: {video_data.get('target_audience','')}

{'='*50}
⚡ HOOK:
{video_data.get('hook','')}

{'='*50}
📝 السكريبت الكامل:
{video_data.get('script','')}

{'='*50}
🎥 المشاهد:
{scenes_text}

{'='*50}
🖼️ الثامبنيل:
{video_data.get('thumbnail_prompt','')}

🎵 الموسيقى: {video_data.get('music_suggestion','')}
🎨 الألوان: {video_data.get('color_palette','')}

{'='*50}
📢 الوصف:
{video_data.get('description','')}

#️⃣ الهاشتاقات:
{video_data.get('hashtags','')}

📣 CTA: {video_data.get('call_to_action','')}
⏰ أفضل وقت: {video_data.get('best_posting_time','')}

{'='*50}
💡 نصائح التفاعل:
""" + "\n".join([f"• {t}" for t in video_data.get('engagement_tips', [])])
