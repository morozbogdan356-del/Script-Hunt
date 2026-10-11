# Script Hunt AI v5 — modular Telegram bot

## Features
- Premium-style inline menu: search, generate, check/fix, library, language settings
- ScriptBlox search (5 pages) and optional authenticated GitHub code search
- Search deduplication, relevance filtering, 5-minute in-memory cache
- Offline Lua module composer: Fly, Speed, ESP/Highlight
- Conservative static analysis and whitespace normalization for `.lua` / `.txt` files
- Private SQLite library: each Telegram user can only retrieve their own saved files
- Russian, Ukrainian, English menu labels and prompts
- Admin statistics using `ADMIN_IDS`
- GitHub Gist publication **only after confirmation** using optional `GIST_TOKEN`

## Important limitations
This is **not a trained AI model** and cannot generate arbitrary Lua code. The "fixer" does not rewrite broken Lua semantics or validate Luau syntax; it normalizes whitespace and flags suspicious constructs. It does **not** run unknown code or test scripts inside Roblox. Generated code is **not guaranteed** to work in all games. Source code from third-party search results is untrusted.

## Deployment
1. Put **all files and directories** in your GitHub repository root. Do not upload only the ZIP.
2. Set `BOT_TOKEN` in the hosting service's secret environment variables.
3. Optional: `GITHUB_TOKEN` for GitHub code search, `GIST_TOKEN` for publishing Gists, `ADMIN_IDS` as comma-separated Telegram numeric IDs.
4. Install: `pip install -r requirements.txt`.
5. Start: `python bot.py`.
6. Run checks: `python -m unittest discover -s tests -v`.

### Render and persistence
This version uses **Telegram long polling**. Render Free Web Services may sleep and may require an HTTP listener, so they are **not reliable for a 24/7 polling bot**. Use a persistent worker host, or implement a webhook HTTP service separately. The default database `data/scripthunt.sqlite3` is **not durable on ephemeral disks**: use a persistent volume or a managed database before relying on saved scripts. Do not commit the `data/` directory or `.env`.

### Files
`bot.py` main bot; `engine.py` offline composer; `services/` storage, language, static analysis; `locales/` translations; `tests/` unit tests.

### Privacy & security
Never share Telegram/GitHub API tokens. A public Gist can expose code to anyone with its URL. This bot does not run arbitrary uploaded Lua. Avoid publishing private code or secrets.
