# Schrodinger's Cat

A Discord bot that posts daily and weekly digests of newly published biology research from the Nature Portfolio of journals. Article data comes from the free [Crossref API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), because Nature's own RSS feeds sit behind a browser check that blocks bots.

Built with [discord.py](https://github.com/Rapptz/discord.py). Lightweight enough to run on a Raspberry Pi or an old Android phone.

## Features

- Automatic **daily** and **weekly** digests, posted to any channel that subscribes
- On-demand commands for the latest articles
- Covers *Nature* and ten sister journals (microbiology, cell biology, genetics, immunology, methods, neuroscience, structural biology, ecology & evolution, chemical biology, biotechnology)
- Skips corrections and retraction notices
- Falls back to the latest articles when nothing new was published in the window
- Local JSON storage, with no database to set up
- Configurable through environment variables

## Commands

| Command | Description | Permission |
|---|---|---|
| `/subscribe` | Send the daily and weekly digests to this channel | Manage Channels |
| `/unsubscribe` | Stop digests in this channel | Manage Channels |
| `/today` | Articles from the last 24 hours | Everyone |
| `/week` | Articles from the last 7 days | Everyone |
| `/top [count]` | The latest articles (1-10, default 3) | Everyone |

The bot also replies "Meow" to any message that starts with "meow".

## How it works

1. Every 30 minutes the bot queries Crossref for articles from the configured journals and merges them into a local cache (`seen.json`), keeping 30 days of history.
2. At the configured hour it posts the daily digest to every subscribed channel. A few minutes later, on the configured weekday, it posts the weekly digest.
3. Subscribed channels are stored in `subscribers.json`.

## Requirements

- Python 3.9 or newer
- A Discord bot token

Python packages (`requirements.txt`):

```
discord.py>=2.4
python-dotenv>=1.0
tzdata
```

`tzdata` is needed on systems without a system timezone database, such as Windows and Android/Termux.

## Setup

### 1. Create the Discord application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. Open the **Bot** tab, reset and copy the token, and turn on the **Message Content Intent** (needed for the "meow" reply).
3. Open **OAuth2 → URL Generator**, tick the scopes `bot` and `applications.commands`, and tick the permissions **View Channels**, **Send Messages**, **Embed Links** and **Read Message History**.
4. Open the generated URL to add the bot to your server.

### 2. Install

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

Create a `.env` file in the project folder:

```env
DISCORD_TOKEN=your_bot_token_here
CROSSREF_EMAIL=you@example.com
```

**Never commit your `.env` file or share your token.** If a token leaks, reset it in the Developer Portal straight away.

### 4. Run

```bash
python bot.py
```

You should see `Logged in as ...`. Then run `/subscribe` in a channel to start receiving digests.

## Configuration

All settings are optional except `DISCORD_TOKEN`.

| Variable | Default | Description |
|---|---|---|
| `DISCORD_TOKEN` | *(required)* | Your bot token |
| `TIMEZONE` | `Africa/Johannesburg` | Timezone for the schedule ([list of names](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)) |
| `DAILY_HOUR` | `8` | Hour (0-23) the daily digest is posted |
| `WEEKLY_DAY` | `0` | Day of the weekly digest (0 = Monday ... 6 = Sunday) |
| `DAILY_MAX` | `15` | Maximum articles in a daily digest |
| `WEEKLY_MAX` | `25` | Maximum articles in a weekly digest |
| `FALLBACK_COUNT` | `5` | Articles shown when nothing new was published |
| `CROSSREF_EMAIL` | *(empty)* | Your email, sent to Crossref for faster, friendlier API access |
| `STORE_PATH` | `seen.json` | Location of the article cache |
| `SUBS_PATH` | `subscribers.json` | Location of the subscribed-channel list |

To add or remove journals, edit the `JOURNALS` dictionary in `bot.py` (journal name → ISSNs).

## Running 24/7

The bot needs to stay online to post on schedule. Some options:

- **A VPS or home server** with a `systemd` service. Use `Restart=always` so it restarts after crashes and reboots.
- **A Raspberry Pi or old PC** at home.
- **An old Android phone** using [Termux](https://f-droid.org/packages/com.termux/) (install from F-Droid), `tmux`, and Termux:Boot to start it on reboot. Disable battery optimisation for Termux and use a wake lock.

Free PaaS tiers that sleep when idle (such as Render or Replit free plans) don't suit Discord bots, because they drop the gateway connection.

Run only **one** copy of the bot per token. Two running copies would post every digest twice.

## Files created at runtime

| File | Purpose |
|---|---|
| `seen.json` | Cache of recent article metadata (about 30 days) |
| `subscribers.json` | IDs of subscribed channels |

Add both to `.gitignore`.

## Known limitations

- If the bot is offline at the scheduled time, that digest is skipped rather than sent late.
- The main *Nature* journal covers all sciences, so some non-biology papers can appear.
- Crossref requests are capped at 100 articles per refresh.
- Crossref data can be delayed or incomplete.

## Recommended `.gitignore`

```gitignore
.env
venv/
__pycache__/
seen.json
subscribers.json
```

## Legal

- [Terms of Service](TERMS.md)
- [Privacy Policy](PRIVACY.md)

This project is not affiliated with or endorsed by Nature, Springer Nature, Crossref or Discord. Article titles and links belong to their respective publishers and authors.
