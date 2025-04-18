import os
import json
import logging
from pyrogram import Client
from plugins.filmibeat_scraper import fetch_filmibeat_ott_releases
from apscheduler.schedulers.blocking import BlockingScheduler

# Initialize Telegram bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL = os.getenv("LOG_CHANNEL")
CACHE_FILE = "seen_movies.json"

bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

def load_seen():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(seen), f)

def format_caption(movie):
    return f"**{movie['title']}**\\n\\nRelease Date: {movie['release_date']}\\nPlatform: {movie['platform']}"

def send_new_releases():
    seen = load_seen()
    new_movies = []

    for movie in fetch_filmibeat_ott_releases():
        if movie['title'] not in seen:
            try:
                caption = format_caption(movie)
                bot.send_photo(chat_id=LOG_CHANNEL, photo=movie['poster_url'], caption=caption, parse_mode="Markdown")
                logging.info(f"Sent: {movie['title']}")
                new_movies.append(movie['title'])
            except Exception as e:
                logging.error(f"Failed to send {movie['title']}: {e}")

    seen.update(new_movies)
    save_seen(seen)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(send_new_releases, 'interval', hours=12)
    logging.info("Scheduler started. Checking for new OTT releases every 12 hours.")
    scheduler.start()
