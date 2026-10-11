import asyncio
import html
import logging
import os
import re
import time
from difflib import SequenceMatcher
from urllib.parse import quote

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BufferedInputFile
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')
modes = {}
if not TOKEN:
    raise RuntimeError('BOT_TOKEN is missing')
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()
queries = {}
active = set()
HEADERS = {'Accept': 'application/vnd.github+json', 'User-Agent': 'ScriptHuntAI/2.0'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'Bearer {GITHUB_TOKEN}'


def norm(value):
    return re.sub(r'[^a-z0-9]+', ' ', str(value).lower()).strip()


def relevant(query, game, title):
    q, g, t = norm(query), norm(game), norm(title)
    if not q:
        return False
    if q in g or q in t:
        return True
    tokens = [x for x in q.split() if len(x) > 2]
    if len(tokens) >= 2 and sum(x in (g + ' ' + t).split() for x in tokens) >= max(2, len(tokens) - 1):
        return True
    return SequenceMatcher(None, q, g).ratio() >= .82 if g else False


def key_status(item):
    text = ' '.join(str(item.get(x) or '') for x in ('title', 'description', 'script'))[:6000].lower()
    if re.search(r'keyless|no[ -]?key|without[ -]?key|без ключа', text):
        return '❌ Не требуется (по описанию)'
    if re.search(r'key[ -]?system|requires? (a )?key|need(s)? (a )?key|ключ обязател', text):
        return '✅ Требуется (по описанию)'
    return '❔ Неизвестно'


def risks(code):
    patterns = [('удалённый загрузчик', r'loadstring\s*\(|HttpGet\s*\('),
                ('сетевые запросы', r'HttpService|http_request|request\s*\('),
                ('обфускация', r'string\.char\s*\(|\\x[0-9a-f]{2}'),
                ('работа с файлами', r'writefile\s*\(|readfile\s*\(')]
    return [name for name, pat in patterns if re.search(pat, code, re.I)]


async def get_json(session, url, params=None, headers=None):
    try:
        async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=18)) as r:
            if r.status != 200:
                logging.warning('HTTP %s %s', r.status, url)
                return {}
            return await r.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
        logging.warning('Fetch failed %s: %s', url, exc)
        return {}


async def scriptblox(session, query, page):
    data = await get_json(session, 'https://scriptblox.com/api/script/search',
                          {'q': query, 'max': 20, 'page': page, 'mode': 'free'})
    entries = (data.get('result') or {}).get('scripts') or []
    output = []
    for item in entries:
        game = item.get('game') or {}
        game_name = game.get('name', '') if isinstance(game, dict) else ''
        title = str(item.get('title') or '')
        if not relevant(query, game_name, title):
            continue
        slug = item.get('slug') or item.get('_id')
        if not slug:
            continue
        output.append({'title': title, 'game': game_name, 'script': str(item.get('script') or ''),
                       'description': str(item.get('description') or ''),
                       'url': 'https://scriptblox.com/script/' + quote(str(slug)), 'source': 'ScriptBlox',
                       'verified': bool(item.get('verified'))})
    return output


async def github_code(session, query):
    # GitHub code search requires authentication; no fabricated results without a token.
    if not GITHUB_TOKEN:
        return []
    data = await get_json(session, 'https://api.github.com/search/code',
                          {'q': f'"{query}" extension:lua', 'per_page': 30}, HEADERS)
    output = []
    for item in data.get('items', []):
        title = item.get('name', '')
        repo = (item.get('repository') or {}).get('full_name', '')
        path = item.get('path', '')
        if not relevant(query, repo + ' ' + path, title):
            continue
        output.append({'title': repo + ' / ' + title, 'game': query, 'script': '',
                       'description': 'Lua-файл на GitHub. Открой ссылку для просмотра.',
                       'url': item.get('html_url', ''), 'source': 'GitHub', 'verified': False})
    return output


def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔎 Поиск скриптов', callback_data='mode:search')],
        [InlineKeyboardButton(text='🛠 Создать скрипт', callback_data='mode:create')]])


@dp.message(Command('menu'))
async def menu(message: Message):
    await message.answer('Выбери действие:', reply_markup=main_keyboard())


@dp.callback_query(F.data.startswith('mode:'))
async def switch_mode(call: CallbackQuery):
    mode = call.data.split(':', 1)[1]
    modes[call.from_user.id] = mode
    await call.answer()
    if mode == 'create':
        await call.message.answer('🛠 Опиши Lua-скрипт, который нужно создать. Укажи функции и ограничения. Я отправлю исходный .lua файл.\n⚠️ Совместимость с executors и играми не гарантируется.')
    else:
        await call.message.answer('🎮 Напиши точное название Roblox-игры на английском.')


async def generate_code(prompt: str):
    if not OPENAI_API_KEY:
        raise RuntimeError('OPENAI_API_KEY не задан на сервере')
    system = ('You are a careful Luau code assistant. Return ONLY valid Lua/Luau source code, '
              'no markdown fences. Produce readable, well-commented code. Avoid credential theft, '
              'exfiltration, evasion, persistence, or claims of universal compatibility. '
              'Do not use loadstring or hidden remote dependencies. '
              'Do not claim code was tested in a live Roblox game.')
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'},
            json={'model': OPENAI_MODEL, 'messages': [{'role':'system','content':system},
                  {'role':'user','content':prompt[:2500]}], 'temperature':0.2, 'max_tokens':3000},
            timeout=aiohttp.ClientTimeout(total=110)) as response:
            payload = await response.json(content_type=None)
            if response.status != 200:
                raise RuntimeError('Ошибка AI API: ' + str(payload.get('error',{}).get('message','HTTP '+str(response.status)))[:180])
            code = payload['choices'][0]['message']['content'].strip()
            if code.startswith('```'):
                code = re.sub(r'^```(?:lua|luau)?\s*|\s*```$', '', code, flags=re.I).strip()
            if not code:
                raise RuntimeError('AI вернул пустой код')
            return code


async def create_script(message: Message, prompt: str):
    uid = message.from_user.id
    if uid in active:
        await message.answer('⏳ Предыдущая задача ещё выполняется.')
        return
    active.add(uid)
    status = await message.answer('🛠 Создание: 0% — подготовка запроса')
    try:
        await status.edit_text('🛠 Создание: 20% — запрос к AI')
        code = await generate_code(prompt)
        await status.edit_text('🛠 Создание: 75% — статическая проверка')
        flags = risks(code)
        await status.edit_text('🛠 Создание: 100% — файл подготовлен')
        await message.answer_document(BufferedInputFile(code.encode('utf-8'), filename='ScriptHunt_Generated.lua'),
             caption=('📜 Исходный Lua-код\n🔬 Статический анализ: ' +
                 (', '.join(flags) if flags else 'известных признаков риска не найдено') +
                 '\n⚠️ Не проверено в Roblox. Статическая проверка не гарантирует работоспособность.'))
    except Exception as exc:
        logging.exception('Generation error')
        await status.edit_text('❌ Не удалось создать скрипт: ' + html.escape(str(exc)[:220]))
    finally:
        active.discard(uid)


def choose_keyboard():
    rows = []
    for start in (1, 6, 11, 16, 21, 26):
        rows.append([InlineKeyboardButton(text=str(n), callback_data=f'count:{n}') for n in range(start, start + 5)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('👋 <b>Добро пожаловать в Script Hunt AI!</b>\n\n'
                         '🔎 Ищу Lua-скрипты по Roblox-играм в открытых каталогах.\n'
                         '📊 Показываю прогресс, источник, код и информацию о ключах.\n'
                         '🛡️ Проверяю известные признаки риска без запуска кода.\n\n'
                         '🎮 Выбери действие в меню ниже.', parse_mode='HTML', reply_markup=main_keyboard())


@dp.message(F.text)
async def set_game(message: Message):
    if modes.get(message.from_user.id) == 'create':
        await create_script(message, message.text.strip())
        return
    query = message.text.strip()[:100]
    if query.startswith('/') or len(query) < 3:
        await message.answer('Напиши название Roblox-игры (минимум 3 символа).')
        return
    queries[message.from_user.id] = query
    await message.answer(f'🎮 <b>{html.escape(query)}</b>\n\nСколько скриптов прислать? Выбери от 1 до 30:',
                         reply_markup=choose_keyboard(), parse_mode='HTML')


async def progress(message, query, pct, found, stage):
    bar = '█' * (pct // 10) + '░' * (10 - pct // 10)
    await message.edit_text(f'🔎 <b>Script Hunt AI</b>\n🎮 {html.escape(query)}\n'
                            f'[{bar}] <b>{pct}%</b>\n📦 Найдено: {found}\n🔍 {stage}', parse_mode='HTML')


@dp.callback_query(F.data.startswith('count:'))
async def run_search(call: CallbackQuery):
    query = queries.get(call.from_user.id)
    if not query:
        await call.answer('Сначала отправь название игры.', show_alert=True)
        return
    if call.from_user.id in active:
        await call.answer('Поиск уже выполняется.', show_alert=True)
        return
    count = int(call.data.split(':')[1])
    if not 1 <= count <= 30:
        await call.answer('Неверное количество.', show_alert=True)
        return
    active.add(call.from_user.id)
    await call.answer()
    status = await call.message.answer('🔎 Запускаю поиск…')
    results, seen = [], set()
    try:
        async with aiohttp.ClientSession() as session:
            tasks = [scriptblox(session, query, page) for page in (1, 2, 3)]
            tasks.append(github_code(session, query))
            completed = 0
            await progress(status, query, 0, 0, 'Подключение к источникам')
            for future in asyncio.as_completed(tasks):
                group = await future
                for item in group:
                    url = item.get('url', '')
                    if url and url not in seen:
                        seen.add(url)
                        results.append(item)
                completed += 1
                await progress(status, query, min(90, completed * 22), len(results), 'Проверяю результаты')
            # Prefer entries with inline code and a relevant game name.
            results.sort(key=lambda x: (bool(x['script']), norm(query) in norm(x['game']), x['verified']), reverse=True)
            await progress(status, query, 100, len(results), 'Готово')
        selected = results[:count]
        await status.edit_text(f'✅ <b>Поиск завершён: {html.escape(query)}</b>\n'
                               f'Найдено: {len(results)}\nОтправляю: {len(selected)} из {count} запрошенных.\n'
                               '⚠️ Исполнение и безопасность не подтверждены.', parse_mode='HTML')
        if not selected:
            await call.message.answer('Ничего подходящего не найдено. Попробуй полное английское название игры.')
            return
        for idx, item in enumerate(selected, 1):
            code = item['script'].strip()
            flags = risks(code) if code else []
            label = ('⚠️ Обнаружены признаки риска: ' + ', '.join(flags)) if flags else ('🔍 Статический анализ: явных признаков из списка не найдено' if code else '❔ Код недоступен для анализа')
            heading = (f'📦 <b>Скрипт {idx}/{len(selected)}</b>\n'
                       f'🎮 <b>Игра:</b> {html.escape(item["game"] or query)}\n'
                       f'🏷️ <b>Хаб:</b> {html.escape(item["title"][:130])}\n'
                       f'🔑 <b>Ключ:</b> {key_status(item)}\n'
                       f'🛡️ <b>Статус:</b> Не проверен в игре\n'
                       f'🔬 {html.escape(label)}\n'
                       f'🌐 <a href="{html.escape(item["url"], quote=True)}">Источник: {item["source"]}</a>\n\n'
                       f'📜 <b>Скрипт:</b>\n')
            if code and len(heading) + len(html.escape(code)) < 3900:
                await call.message.answer(heading + '<pre>' + html.escape(code) + '</pre>', parse_mode='HTML', disable_web_page_preview=True)
            elif code:
                await call.message.answer(heading + 'Код длинный, отправляю отдельным файлом.', parse_mode='HTML', disable_web_page_preview=True)
                from aiogram.types import BufferedInputFile
                await call.message.answer_document(BufferedInputFile(code.encode('utf-8'), filename=f'script_{idx}.lua'))
            else:
                await call.message.answer(heading + 'Код не опубликован в доступном API — смотри источник.', parse_mode='HTML', disable_web_page_preview=True)
            await asyncio.sleep(.1)
    except Exception:
        logging.exception('Search error')
        await status.edit_text('❌ Ошибка поиска. Попробуй позже.')
    finally:
        active.discard(call.from_user.id)


async def main():
    bot = Bot(TOKEN)
    await bot.set_my_commands([BotCommand(command='start', description='Главное меню'), BotCommand(command='menu', description='Поиск или создание')])
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
