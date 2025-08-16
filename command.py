import json
import asyncio
from pyrogram import filters
from bot import app, scheduler, post_to_channel

# --- Change posting time dynamically ---
@app.on_message(filters.private & filters.command("settime"))
async def set_time(_, message):
    try:
        args = message.text.split()
        if len(args) != 2:
            return await message.reply("⚠️ Usage: `/settime HH:MM` (24hr UTC format)", quote=True)

        hour, minute = map(int, args[1].split(":"))

        # Reset scheduler
        scheduler.remove_all_jobs()
        scheduler.add_job(lambda: asyncio.create_task(post_to_channel()), "cron", hour=hour, minute=minute)

        await message.reply(f"✅ Auto post time updated to **{hour:02d}:{minute:02d} UTC**")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- Update daily post (data.json) ---
@app.on_message(filters.private & filters.command("setpost"))
async def set_post(_, message):
    try:
        text = message.text.replace("/setpost", "").strip()
        if not text:
            return await message.reply("⚠️ Send JSON data with `/setpost { ... }`", quote=True)

        data = json.loads(text)

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        await message.reply("✅ New daily post saved successfully!")
    except Exception as e:
        await message.reply(f"❌ Error in JSON format: {e}")
