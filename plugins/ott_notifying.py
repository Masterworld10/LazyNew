import os
import json
import logging
from pyrogram import Client
from plugins.filmibeat_scraper import fetch_filmibeat_ott_releases
from apscheduler.schedulers.background import BackgroundScheduler

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
LOG_CHANNEL = os.getenv("LOG_CHANNEL")
CACHE_FILE = "seen_movies.json"

# Log config info
logging.info(f"BOT_TOKEN present: {BOT_TOKEN is not None}")
logging.info(f"API_ID present: {API_ID is not None}")
logging.info(f"API_HASH present: {API_HASH is not None}")
logging.info(f"LOG_CHANNEL: {LOG_CHANNEL}")

# Pyrogram bot client
bot = Client("ott_sender", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

def load_seen():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(seen), f)

def format_caption(movie):
    return f"**{movie['title']}**\n\nRelease Date: {movie['release_date']}\nPlatform: {movie['platform']}"

def send_new_releases():
    logging.info("Checking for new OTT releases...")

    seen = load_seen()
    new_movies = []

    releases = fetch_filmibeat_ott_releases()
    logging.info(f"Fetched {len(releases)} movie(s) from Filmibeat")

    with bot:
        # Test message to verify connection
        try:
            bot.send_message(chat_id=LOG_CHANNEL, text="Bot is live and connected to the log channel!")
        except Exception as e:
            logging.error(f"Test message failed: {e}")

        for movie in releases:
            logging.info(f"Found movie: {movie['title']}")
            if movie['title'] not in seen:
                try:
                    caption = format_caption(movie)
                    bot.send_photo(chat_id=LOG_CHANNEL, photo=movie['poster_url'], caption=caption, parse_mode="markdown")
                    logging.info(f"Sent: {movie['title']}")
                    new_movies.append(movie['title'])
                except Exception as e:
                    logging.error(f"Failed to send {movie['title']}: {e}")
            else:
                logging.info(f"Already sent: {movie['title']}")

    seen.update(new_movies)
    save_seen(seen)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_new_releases, 'interval', hours=12)
    logging.info("Scheduler started. Checking every 12 hours.")
    scheduler.start()

    # Run once immediately
    send_new_releases()

    import time
    while True:
        time.sleep(60)
