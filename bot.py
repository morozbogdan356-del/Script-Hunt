import asyncio
import html
import logging
import os
import re
from urllib.parse import quote

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
if not TOKEN:
    raise RuntimeError('Set BOT_TOKEN in .env')

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()
HEADERS = {'Accept': 'application/vnd.github+json', 'User-Agent': 'ScriptHuntAI/1.0'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'Bearer {GITHUB_TOKEN}'


def risk_notes(code: str) -> list[str]:
    rules = {
        'Загрузка удалённого кода': r'loadstring\s*\(|game\s*:\s*HttpGet\s*\(',
        'Сетевые запросы': r'HttpService|request\s*\(|http_request',
        'Возможная обфускация': r'string\.char\s*\(|\\x[0-9a-fA-F]{2}',
        'Доступ к файлам': r'writefile\s*\(|readfile\s*\(',
    }
    return [label for label, pattern in rules.items() if re.search(pattern, code, re.I)]


async def fetch_json(session, url, headers=None, params=None):
    try:
        async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as r:
            if r.status != 200:
                logging.info('Search HTTP %s: %s', r.status, url)
                return {}
            return await r.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
        logging.info('Search failed: %s', e)
        return {}


async def search_github(session, query):
    data = await fetch_json(session, 'https://api.github.com/search/repositories',
                            headers=HEADERS,
                            params={'q': f'{query} roblox lua', 'sort': 'updated', 'per_page': 15})
    return [{'title': item.get('full_name', 'GitHub'),
             'url': item.get('html_url', ''), 'source': 'GitHub',
             'description': item.get('description') or '', 'code': ''}
            for item in data.get('items', [])]


async def search_scriptblox(session, query):
    data = await fetch_json(session, 'https://scriptblox.com/api/script/search',
                            params={'q': query, 'max': 20, 'mode': 'free'})
    scripts = data.get('result', {}).get('scripts', [])
    result = []
    for item in scripts:
        slug = item.get('slug') or item.get('_id')
        url = f'https://scriptblox.com/script/{quote(str(slug))}' if slug else ''
        result.append({'title': item.get('title') or 'ScriptBlox script',
                       'url': url, 'source': 'ScriptBlox',
                       'description': item.get('game', {}).get('name', '') if isinstance(item.get('game'), dict) else '',
                       'code': item.get('script') or ''})
    return result


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('🔎 <b>Script Hunt AI</b>\nОтправь название Roblox-игры на английском. Я найду открытые публикации со скриптами и покажу источники и возможные риски.', parse_mode='HTML')


@dp.message(F.text)
async def search(message: Message):
    query = message.text.strip()[:100]
    if len(query) < 3 or query.startswith('/'):
        await message.answer('Напиши название игры (не менее 3 символов).')
        return
    status = await message.answer(f'🔎 Поиск: {html.escape(query)}\nПроверяю GitHub и ScriptBlox…', parse_mode='HTML')
    try:
        async with aiohttp.ClientSession() as session:
            found = await asyncio.gather(search_github(session, query), search_scriptblox(session, query))
        results = []
        seen = set()
        for item in [x for group in found for x in group]:
            url = item['url']
            if url and url not in seen:
                seen.add(url)
                results.append(item)
        results = results[:20]
        await status.edit_text(f'✅ Поиск завершён: {html.escape(query)}\nИсточников проверено: 2\nНайдено уникальных результатов: {len(results)}\n⚠️ Работоспособность и безопасность не подтверждены.', parse_mode='HTML')
        if not results:
            return
        for index, item in enumerate(results, 1):
            code = item['code']
            notes = risk_notes(code) if code else []
            risk = ', '.join(notes) if notes else ('Признаки из списка не обнаружены' if code else 'Код не получен для анализа')
            title = html.escape(str(item['title'])[:110])
            link = html.escape(item['url'], quote=True)
            desc = html.escape(str(item['description'])[:180])
            body = (f'<b>{index}. {title}</b> ({item["source"]})\n{desc}\n'
                    f'<a href="{link}">Открыть источник</a>\nПроверка: {html.escape(risk)}')
            if code and len(code) <= 800:
                body += '\n<pre>' + html.escape(code) + '</pre>'
            elif code:
                body += '\nКод длинный — открой источник.'
            await message.answer(body, parse_mode='HTML', disable_web_page_preview=True)
            await asyncio.sleep(0.1)
    except Exception:
        logging.exception('Unexpected search error')
        await status.edit_text('Ошибка поиска. Попробуй ещё раз позже.')


async def main():
    bot = Bot(TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
