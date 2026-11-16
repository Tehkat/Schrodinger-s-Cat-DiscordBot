import asyncio
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
import feedparser
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["DISCORD_TOKEN"]
TZ = ZoneInfo(os.getenv("TIMEZONE", "Africa/Johannesburg"))
DAILY_HOUR = int(os.getenv("DAILY_HOUR", "8"))        # 08:00 local time
WEEKLY_DAY = int(os.getenv("WEEKLY_DAY", "0"))        # 0 = Monday ... 6 = Sunday
DAILY_MAX = int(os.getenv("DAILY_MAX", "15"))
WEEKLY_MAX = int(os.getenv("WEEKLY_MAX", "25"))
FALLBACK_COUNT = int(os.getenv("FALLBACK_COUNT", "5"))  # shown when nothing new

FEED_URL = "https://www.nature.com/subjects/biological-sciences.rss"
STORE = Path(os.getenv("STORE_PATH", "seen.json"))
SUBS = Path(os.getenv("SUBS_PATH", "subscribers.json"))
KEEP_DAYS = 30


# ---------- storage ----------
def load_store() -> dict:
    if STORE.exists():
        return json.loads(STORE.read_text(encoding="utf-8"))
    return {}


def save_store(store: dict) -> None:
    STORE.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")


def load_subs() -> list[int]:
    if SUBS.exists():
        return json.loads(SUBS.read_text(encoding="utf-8"))
    return []


def save_subs(subs: list[int]) -> None:
    SUBS.write_text(json.dumps(subs), encoding="utf-8")


async def broadcast(title: str, days: int, limit: int):
    for channel_id in load_subs():
        try:
            channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
            await post_digest(channel, title, days, limit)
        except Exception as exc:
            print(f"Could not post to {channel_id}:", exc)


# ---------- feed ----------
# Nature's own RSS sits behind a browser check, so we use Crossref (free API for programs).
# Add or remove journals here. Each entry: name -> ISSNs (print and/or online).
JOURNALS = {
    "Nature": ["0028-0836", "1476-4687"],
    "Nature Microbiology": ["2058-5276"],
    "Nature Cell Biology": ["1465-7392", "1476-4679"],
    "Nature Genetics": ["1061-4036", "1546-1718"],
    "Nature Immunology": ["1529-2908", "1529-2916"],
    "Nature Methods": ["1548-7091", "1548-7105"],
    "Nature Neuroscience": ["1097-6256", "1546-1726"],
    "Nature Structural & Molecular Biology": ["1545-9993", "1545-9985"],
    "Nature Ecology & Evolution": ["2397-334X"],
    "Nature Chemical Biology": ["1552-4450", "1552-4469"],
    "Nature Biotechnology": ["1087-0156", "1546-1696"],
}
LOOKBACK_DAYS = 14
CROSSREF_EMAIL = os.getenv("CROSSREF_EMAIL", "")  # optional, gives you faster, friendlier access
SKIP_TITLES = re.compile(r"^(author|publisher) correction|^retraction note", re.I)


def fetch_feed() -> list[dict]:
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    issns = [i for lst in JOURNALS.values() for i in lst]
    filters = ",".join(
        [f"issn:{i}" for i in issns] + ["type:journal-article", f"from-created-date:{since}"]
    )
    params = {
        "filter": filters,
        "sort": "created",
        "order": "desc",
        "rows": "100",
        "select": "DOI,title,container-title,created,URL",
    }
    if CROSSREF_EMAIL:
        params["mailto"] = CROSSREF_EMAIL
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    ua = "nature-discord-bot/1.0 (personal use" + (f"; mailto:{CROSSREF_EMAIL}" if CROSSREF_EMAIL else "") + ")"
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    items = []
    for w in data["message"]["items"]:
        title = re.sub(r"<[^>]+>", "", (w.get("title") or ["Untitled"])[0]).strip()
        if SKIP_TITLES.search(title):
            continue
        created = dt.datetime.fromisoformat(w["created"]["date-time"].replace("Z", "+00:00"))
        items.append(
            {
                "title": title,
                "link": w.get("URL") or f"https://doi.org/{w['DOI']}",
                "published": created.isoformat(),
                "source": (w.get("container-title") or [""])[0],
            }
        )
    print(f"Crossref returned {len(items)} articles")
    return items


async def refresh_store() -> dict:
    store = load_store()
    try:
        items = await asyncio.to_thread(fetch_feed)
    except Exception as exc:
        print("Feed refresh failed:", exc)
        return store
    for it in items:
        if it["link"]:
            store.setdefault(it["link"], it)
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=KEEP_DAYS)
    store = {k: v for k, v in store.items() if dt.datetime.fromisoformat(v["published"]) >= cutoff}
    save_store(store)
    return store


def recent(store: dict, days: int, limit: int) -> tuple[list[dict], int]:
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    hits = [v for v in store.values() if dt.datetime.fromisoformat(v["published"]) >= cutoff]
    hits.sort(key=lambda v: v["published"], reverse=True)
    return hits[:limit], len(hits)


def latest(store: dict, n: int) -> list[dict]:
    items = sorted(store.values(), key=lambda v: v["published"], reverse=True)
    return items[:n]


# ---------- formatting ----------
def build_embeds(title: str, items: list[dict], total: int, note: str = "") -> list[discord.Embed]:
    if not items:
        return [discord.Embed(title=title, description="Couldn't load any articles from the feed right now.", colour=0x2E7D32)]
    lines = [f"*{note}*\n"] if note else []
    for it in items:
        src = f" — *{it['source']}*" if it["source"] else ""
        lines.append(f"• [{it['title']}]({it['link']}){src}")

    embeds, chunk = [], ""
    for line in lines:
        if len(chunk) + len(line) + 1 > 3900:
            embeds.append(chunk)
            chunk = ""
        chunk += line + "\n"
    embeds.append(chunk)

    out = []
    for i, text in enumerate(embeds):
        out.append(
            discord.Embed(
                title=title if i == 0 else None,
                description=text,
                colour=0x2E7D32,
                url="https://www.nature.com/subjects/biological-sciences" if i == 0 else None,
            )
        )
    footer = f"Showing {len(items)} of {total}" if total > len(items) else f"{len(items)} articles"
    out[-1].set_footer(text=f"{footer} • Nature Portfolio via Crossref")
    return out


async def send_embeds(target, embeds):
    for i in range(0, len(embeds), 10):
        await target.send(embeds=embeds[i : i + 10])


async def post_digest(target, title: str, days: int, limit: int):
    store = await refresh_store()
    items, total = recent(store, days, limit)
    note = ""
    if not items:
        items = latest(store, FALLBACK_COUNT)
        total = len(items)
        window = "24 hours" if days == 1 else f"{days} days"
        note = f"Nothing new in the last {window}, so here are the latest articles instead."
    await send_embeds(target, build_embeds(title, items, total, note))


# ---------- bot ----------
class NatureBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # needed to read "meow"
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        poll_feed.start()
        daily_digest.start()
        weekly_digest.start()

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.lower().startswith("meow"):
            await message.channel.send("Meow")


bot = NatureBot()


@tasks.loop(minutes=30)
async def poll_feed():
    try:
        await refresh_store()
    except Exception as exc:
        print("Feed refresh failed:", exc)


@tasks.loop(time=dt.time(hour=DAILY_HOUR, minute=0, tzinfo=TZ))
async def daily_digest():
    today = dt.datetime.now(TZ).strftime("%a %d %b")
    await broadcast(f"🧬 Daily biology digest — {today}", 1, DAILY_MAX)


@tasks.loop(time=dt.time(hour=DAILY_HOUR, minute=5, tzinfo=TZ))
async def weekly_digest():
    if dt.datetime.now(TZ).weekday() != WEEKLY_DAY:
        return
    await broadcast("🧬 Weekly biology digest — last 7 days", 7, WEEKLY_MAX)


@poll_feed.before_loop
@daily_digest.before_loop
@weekly_digest.before_loop
async def _wait():
    await bot.wait_until_ready()


@bot.tree.command(name="subscribe", description="Send the daily and weekly digests to this channel")
@app_commands.default_permissions(manage_channels=True)
async def subscribe(interaction: discord.Interaction):
    subs = load_subs()
    if interaction.channel_id in subs:
        await interaction.response.send_message("This channel is already subscribed.", ephemeral=True)
        return
    subs.append(interaction.channel_id)
    save_subs(subs)
    await interaction.response.send_message(
        f"✅ Subscribed. Daily digest at {DAILY_HOUR:02d}:00, weekly digest on "
        f"{['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][WEEKLY_DAY]} ({TZ.key})."
    )


@bot.tree.command(name="unsubscribe", description="Stop digests in this channel")
@app_commands.default_permissions(manage_channels=True)
async def unsubscribe(interaction: discord.Interaction):
    subs = load_subs()
    if interaction.channel_id not in subs:
        await interaction.response.send_message("This channel isn't subscribed.", ephemeral=True)
        return
    subs.remove(interaction.channel_id)
    save_subs(subs)
    await interaction.response.send_message("🛑 Unsubscribed this channel.")


@bot.tree.command(name="today", description="Biology articles from the last 24 hours")
async def today(interaction: discord.Interaction):
    await interaction.response.defer()
    await post_digest(interaction.followup, "🧬 Last 24 hours", 1, DAILY_MAX)


@bot.tree.command(name="week", description="Biology articles from the last 7 days")
async def week(interaction: discord.Interaction):
    await interaction.response.defer()
    await post_digest(interaction.followup, "🧬 Last 7 days", 7, WEEKLY_MAX)


@bot.tree.command(name="top", description="Show the latest articles (default 3)")
@app_commands.describe(count="How many articles to show (1-10)")
async def top(interaction: discord.Interaction, count: app_commands.Range[int, 1, 10] = 3):
    await interaction.response.defer()
    store = await refresh_store()
    items = latest(store, count)
    await send_embeds(interaction.followup, build_embeds(f"🧬 Latest {count} articles", items, len(items)))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)