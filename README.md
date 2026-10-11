# Script Hunt AI v3

Telegram bot with two modes: search for Roblox Lua scripts and AI-assisted generation of Lua source files.

## Setup

1. Install Python 3.11+ and `pip install -r requirements.txt`.
2. Set `BOT_TOKEN` in hosting environment variables. Never commit actual secrets.
3. Optional: `GITHUB_TOKEN` enables GitHub Code Search; `OPENAI_API_KEY` enables generation. API usage is billed separately.
4. Run `python bot.py`.
5. In Telegram use `/start` or `/menu`.

Search uses ScriptBlox and optionally GitHub. AI-generated code is NOT runtime-tested. Progress indicates completed stages, not measured model progress. The bot uses polling, requiring a continuously running background process; Render Free Web Service is not a reliable 24/7 polling host and expects an HTTP listener.
