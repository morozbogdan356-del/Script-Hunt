# Script Hunt AI
Telegram bot for searching publicly indexed Roblox Lua scripts. Results are **not executed** and safety/compatibility cannot be guaranteed.

## Run locally or on an always-on Linux VPS
1. Install Python 3.11+.
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`, set `BOT_TOKEN` from @BotFather. Optional: set `GITHUB_TOKEN` for higher GitHub API limits.
5. `python bot.py`

## Run as a systemd service (Oracle Cloud Ubuntu VM)
Replace `ubuntu` and `/home/ubuntu/script_hunt` with your actual username and directory:
```
sudo cp script-hunt.service /etc/systemd/system/script-hunt.service
sudo systemctl daemon-reload
sudo systemctl enable --now script-hunt
sudo systemctl status script-hunt
```
Do not commit `.env` or publish tokens. An Oracle Always Free VM may require payment-card verification, may be unavailable due to capacity, and is not guaranteed 24/7. The bot uses Telegram long polling, so no inbound port is needed.

## Sources
GitHub repository search API and ScriptBlox public search API. Other search providers require separate API integrations. Script safety is a heuristic static scan, not an antivirus verdict; no live Roblox execution or working-status verification occurs.
