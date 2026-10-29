import discord
import os
import re
import csv
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # baca DISCORD_TOKEN dari file .env

TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_IDS = [
    1029716623977873501, 1140403131193233548  # ganti sesuai channel
]

# Semua hasil scrape disimpan di folder data/ (sudah di-ignore oleh git)
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

RAW_FILE = DATA_DIR / "scraped_messages.txt"
CSV_FILE = DATA_DIR / "scraped_messages.csv"
PARSED_FILE = DATA_DIR / "parsed_messages.txt"

client = discord.Client()

# Regex cleaning
EMOJI_PATTERN = re.compile(r"<a?:\w+:\d+>")   # hapus <:emoji:123456>
MARKDOWN_PATTERN = re.compile(r"(\*{1,2}|__|~~)")  # hapus **, __, ~~
WHITESPACE_PATTERN = re.compile(r"\s+")

# Regex parsing harga
BUY_PATTERN = re.compile(r"BUY.*?(\d[\d.,]*)", re.IGNORECASE)
SELL_PATTERN = re.compile(r"SELL.*?(\d[\d.,]*)", re.IGNORECASE)

def clean_message(content: str) -> str:
    content = EMOJI_PATTERN.sub("", content)
    content = MARKDOWN_PATTERN.sub("", content)
    content = WHITESPACE_PATTERN.sub(" ", content)
    return content.strip()

def save_raw(author, content):
    cleaned = clean_message(content)
    with open(RAW_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {author} | {cleaned}\n")

def save_csv(author, content):
    cleaned = clean_message(content)
    buy_match = BUY_PATTERN.search(cleaned)
    sell_match = SELL_PATTERN.search(cleaned)

    buy_price = buy_match.group(1) if buy_match else ""
    sell_price = sell_match.group(1) if sell_match else ""

    if buy_price or sell_price:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                author,
                buy_price,
                sell_price,
                cleaned
            ])
        with open(PARSED_FILE, "a", encoding="utf-8") as f:
            f.write(f"💾 Disimpan: {author} | {cleaned}\n")

@client.event
async def on_ready():
    print(f"✅ Login sebagai {client.user}")
    print(f"Monitoring channels: {CHANNEL_IDS}")

    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Author", "Buy Price", "Sell Price", "Full Message"])

@client.event
async def on_message(message):
    if message.channel.id in CHANNEL_IDS and not message.author.bot:
        save_raw(str(message.author), message.content)
        save_csv(str(message.author), message.content)
        print(f"💾 Disimpan: {message.author} | {clean_message(message.content)}")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN tidak ditemukan. Cek file .env kamu!")

client.run(TOKEN)
