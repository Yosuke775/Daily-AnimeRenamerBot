import json
import asyncio
from pyrogram import Client, filters
from config import Config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web
import os

# --- Telegram Bot Setup ---
app = Client(
    "daily_anime_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# --- Function to build post ---
def build_post(data):
    header = f"⟣━━━━━━━━━━━━━━━━━━━⟢\n" \
             f"      📅 {data['date']}\n" \
             f"  『 {data['title']} 』\n" \
             f"⟣━━━━━━━━━━━━━━━━━━━⟢\n\n"

    anime_blocks = []
    for a in data["anime"]:
        block = f"⫷ {a['name']} ⫸\n" \
                f"┃🕒 Time: {a['time']}\n" \
                f"┃🎬 Episode: {a['episode']}\n" \
                f"┃📺 Platform: {a['platform']}\n"
        if "extra" in a:
            block += f"{a['extra']}\n"
        block += "┗━━━━━━━━━━━━━━━\n"
        anime_blocks.append(block)

    footer = f"\n{data['footer']}\n\n" \
             f"━━━━━━━━━━━━━━━━━━━\n" \
             f"{data['hashtags']}\n\n" \
             f"━━━━━━━━━━━━━━━━━━━"

    return header + "\n".join(anime_blocks) + footer

# --- Function to post to channel ---
async def post_to_channel():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        text = build_post(data)
        await app.send_message(Config.CHANNEL_ID, text)
        print("✅ Post sent successfully!")
    except Exception as e:
        print(f"❌ Error posting: {e}")

# --- Manual Trigger (/post) ---
@app.on_message(filters.private & filters.command("post"))
async def manual_post(_, message):
    await post_to_channel()
    await message.reply("✅ Posted successfully!")

# --- Scheduler Setup ---
scheduler = AsyncIOScheduler()
# Default: 10:00 UTC
scheduler.add_job(lambda: asyncio.create_task(post_to_channel()), "cron", hour=10, minute=0)

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply(
        "👋 Hello! I post daily anime release guides.\n\n"
        "🔹 `/post` → Manual post\n"
        "🔹 `/settime HH:MM` → Change auto-post time (UTC)\n"
        "🔹 `/setpost {json}` → Update daily post\n\n"
        "⏰ Auto posts daily at 10:00 AM UTC."
    )

@app.on_start()
async def start_scheduler(_, __):
    scheduler.start()
    print("⏰ Scheduler started!")

# --- Aiohttp Web Server (for Render ping/healthcheck) ---
async def handle(request):
    return web.Response(text="🚀 Daily Anime Bot is alive!")

async def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web = web.Application()
    app_web.router.add_get("/", handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server started on port {port}")

# --- Main Run ---
async def main():
    import command  # ✅ register command handlers
    await asyncio.gather(
        app.start(),
        run_web()
    )
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
