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
from engine import build, check
from services import storage
from services.i18n import tr
from services.analyzer import analyze, repair

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GIST_TOKEN = os.getenv('GIST_TOKEN', '')
recent_generated = {}
search_cache = {}
ADMIN_IDS = {int(x) for x in os.getenv('ADMIN_IDS', '').replace(' ', '').split(',') if x.isdigit()}
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
        async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=9)) as r:
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


def main_keyboard(uid=0):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔎 ' + tr(uid,'search'), callback_data='mode:search'),
         InlineKeyboardButton(text='✨ ' + tr(uid,'create'), callback_data='mode:create')],
        [InlineKeyboardButton(text='🧰 ' + tr(uid,'fix'), callback_data='mode:fix'),
         InlineKeyboardButton(text='📁 ' + tr(uid,'library'), callback_data='mode:library')],
        [InlineKeyboardButton(text='🌐 ' + tr(uid,'settings'), callback_data='mode:settings')]])


def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang:ru'),
         InlineKeyboardButton(text='🇺🇦 Українська', callback_data='lang:uk'),
         InlineKeyboardButton(text='🇬🇧 English', callback_data='lang:en')]])


async def show_library(message, uid):
    rows = storage.listing(uid)
    if not rows:
        await message.answer('📁 Библиотека пуста. Создай скрипт, чтобы сохранить его.')
        return
    buttons = [[InlineKeyboardButton(text=f'📄 {title[:42]}', callback_data=f'lib:{sid}')] for sid,title,_ in rows]
    await message.answer('📁 <b>Мои скрипты</b> (последние 20)', parse_mode='HTML',
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@dp.callback_query(F.data.startswith('lang:'))
async def change_lang(call: CallbackQuery):
    lang=call.data.split(':',1)[1]
    storage.set_language(call.from_user.id,lang)
    await call.answer('OK')
    await call.message.answer(tr(call.from_user.id,'welcome')+'\n'+tr(call.from_user.id,'choose'),
                              reply_markup=main_keyboard(call.from_user.id))


@dp.callback_query(F.data.startswith('lib:'))
async def download_saved(call: CallbackQuery):
    try: sid=int(call.data.split(':',1)[1])
    except ValueError: return await call.answer('Invalid ID',show_alert=True)
    item=storage.get(call.from_user.id,sid)
    if not item: return await call.answer('Не найдено',show_alert=True)
    await call.answer()
    title,code=item
    await call.message.answer_document(BufferedInputFile(code.encode(),filename=f'ScriptHunt_{sid}.lua'),caption=title[:900])


@dp.message(Command('admin'))
async def admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer('Доступ запрещён.')
    users,scripts=storage.stats()
    await message.answer(f'🛡 Админ-панель\n👥 Пользователи: {users}\n📁 Сохранённые файлы: {scripts}\n🔎 Кеш запросов: {len(search_cache)}')


@dp.message(Command('menu'))
async def menu(message: Message):
    await message.answer(tr(message.from_user.id,'choose'), reply_markup=main_keyboard(message.from_user.id))


@dp.callback_query(F.data.startswith('mode:'))
async def switch_mode(call: CallbackQuery):
    mode = call.data.split(':', 1)[1]
    modes[call.from_user.id] = mode
    await call.answer()
    if mode == 'library':
        await show_library(call.message, call.from_user.id)
        return
    if mode == 'settings':
        await call.message.answer('🌐 Выбери язык / Choose language:', reply_markup=language_keyboard())
        return
    if mode == 'fix':
        await call.message.answer(tr(call.from_user.id,'help_fix'))
        return
    if mode == 'create':
        await call.message.answer(tr(call.from_user.id,'help_create')+'\n⚠️ Работа в конкретной игре не гарантируется.')
    else:
        await call.message.answer(tr(call.from_user.id,'help_search'))


async def create_script(message: Message, prompt: str):
    uid = message.from_user.id
    if uid in active:
        await message.answer('⏳ Предыдущая задача ещё выполняется.')
        return
    active.add(uid)
    status = await message.answer('🛠 Создание: 0% — анализ запроса')
    try:
        code, modules = build(prompt)
        if not code:
            await status.edit_text('⚠️ Пока мой офлайн-движок поддерживает Fly, Speed и ESP/подсветку. Для произвольных запросов понадобится локальная языковая модель.')
            return
        await status.edit_text('🛠 Создание: 40% — сборка модулей: ' + ', '.join(modules))
        ok, detail = check(code)
        if not ok:
            await status.edit_text('❌ Не удалось пройти базовую проверку: ' + detail)
            return
        await status.edit_text('🛠 Создание: 100% — исходник собран; проверка структуры завершена')
        recent_generated[uid] = code
        storage.save(uid, 'Generated: ' + prompt[:80], code)
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔗 Опубликовать Raw-ссылку', callback_data='gist:confirm')]])
        await message.answer_document(BufferedInputFile(code.encode('utf-8'), filename='ScriptHunt_Generated.lua'),
            caption='📜 Lua исходник\n🧩 Модули: ' + ', '.join(modules) +
                '\n🔬 ' + detail + '\n⚠️ Не проверено в Roblox; работа в конкретной игре не гарантируется.',
            reply_markup=buttons)
    except Exception:
        logging.exception('Generation error')
        await status.edit_text('❌ Ошибка создания. Проверь логи сервера.')
    finally:
        active.discard(uid)


@dp.callback_query(F.data == 'gist:confirm')
async def confirm_gist(call: CallbackQuery):
    if not recent_generated.get(call.from_user.id):
        return await call.answer('Сначала создай скрипт.', show_alert=True)
    await call.answer()
    await call.message.answer('⚠️ Код будет опубликован по ссылке. Не публикуй секреты и приватные данные. Подтверждаешь?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Опубликовать', callback_data='gist:create'),
             InlineKeyboardButton(text='❌ Отмена', callback_data='gist:cancel')]]))


@dp.callback_query(F.data == 'gist:cancel')
async def cancel_gist(call: CallbackQuery):
    await call.answer('Отменено')
    await call.message.edit_text('Публикация отменена.')


@dp.callback_query(F.data == 'gist:create')
async def create_gist(call: CallbackQuery):
    code = recent_generated.get(call.from_user.id)
    if not code:
        await call.answer('Сначала создай скрипт.', show_alert=True)
        return
    if not GIST_TOKEN:
        await call.answer('GIST_TOKEN не настроен. Lua-файл уже доступен выше.', show_alert=True)
        return
    await call.answer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.github.com/gists',
                headers={'Authorization': 'Bearer ' + GIST_TOKEN, 'Accept': 'application/vnd.github+json'},
                json={'description': 'Script Hunt AI generated Lua', 'public': True,
                      'files': {'ScriptHunt_Generated.lua': {'content': code}}},
                timeout=aiohttp.ClientTimeout(total=15)) as response:
                data = await response.json(content_type=None)
                if response.status != 201:
                    raise RuntimeError('GitHub Gist API HTTP ' + str(response.status))
                raw = data['files']['ScriptHunt_Generated.lua']['raw_url']
        await call.message.answer('🔗 Публичная Raw-ссылка:\n' + html.escape(raw) +
            '\n\n⚠️ Ссылка публичная. Публикуй только код, которым можно делиться.')
    except Exception:
        logging.exception('Gist creation failed')
        await call.message.answer('❌ Не удалось создать Gist. Проверь GIST_TOKEN и разрешения токена.')


def choose_keyboard():
    rows = []
    for start in (1, 6, 11, 16, 21, 26):
        rows.append([InlineKeyboardButton(text=str(n), callback_data=f'count:{n}') for n in range(start, start + 5)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('⚡ <b>Script Hunt AI v5</b>\n\n'+html.escape(tr(message.from_user.id,'welcome'))+'\n'+html.escape(tr(message.from_user.id,'choose')), parse_mode='HTML', reply_markup=main_keyboard(message.from_user.id))


async def fix_code(message, code):
    if len(code)>200_000:
        return await message.answer('Файл слишком большой (максимум 200 КБ).')
    status=await message.answer('🧰 Проверяю структуру и известные риски…')
    fixed=repair(code)
    flags=analyze(fixed)
    notes='; '.join(flags) if flags else 'Известные признаки риска не обнаружены'
    await status.edit_text('🔬 Статический анализ завершён.\n⚠️ '+notes+'\nПроведена нормализация пробелов; полноценная проверка Luau и запуск в Roblox не выполнялись.')
    storage.save(message.from_user.id,'Analyzed Lua',fixed)
    await message.answer_document(BufferedInputFile(fixed.encode(),filename='ScriptHunt_Checked.lua'),caption='📄 Исходник после базовой нормализации')


@dp.message(F.document)
async def document_handler(message: Message, bot: Bot):
    if modes.get(message.from_user.id) != 'fix':
        return await message.answer('Для анализа файла выбери «Проверить / исправить» в меню.')
    doc=message.document
    if not doc.file_name.lower().endswith(('.lua','.txt')) or doc.file_size>200_000:
        return await message.answer('Пришли .lua или .txt до 200 КБ.')
    from io import BytesIO
    output=BytesIO()
    await bot.download(doc, destination=output)
    try: code=output.getvalue().decode('utf-8-sig')
    except UnicodeDecodeError: return await message.answer('Файл должен быть в UTF-8.')
    await fix_code(message,code)


@dp.message(F.text)
async def set_game(message: Message):
    if modes.get(message.from_user.id) == 'fix':
        await fix_code(message, message.text)
        return
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
    cache_key = norm(query)
    try:
        async with aiohttp.ClientSession() as session:
            cached = search_cache.get(cache_key)
            tasks = [] if cached and time.monotonic()-cached[0]<300 else [scriptblox(session, query, page) for page in (1, 2, 3, 4, 5)] + [github_code(session, query)]
            if not tasks:
                results = list(cached[1])
            completed = 0
            await progress(status, query, 0, 0, 'Подключение к источникам')
            for future in asyncio.as_completed(tasks, timeout=11):
                try:
                    group = await future
                except asyncio.TimeoutError:
                    break
                for item in group:
                    url = item.get('url', '')
                    if url and url not in seen:
                        seen.add(url)
                        results.append(item)
                completed += 1
                await progress(status, query, min(90, completed * 15), len(results), 'Проверяю результаты')
            # Prefer entries with inline code and a relevant game name.
            results.sort(key=lambda x: (bool(x['script']), norm(query) in norm(x['game']), x['verified']), reverse=True)
            if tasks:
                search_cache[cache_key]=(time.monotonic(), list(results))
                if len(search_cache)>100: search_cache.clear()
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
    await bot.set_my_commands([BotCommand(command='start', description='Главное меню'), BotCommand(command='menu', description='Все инструменты'), BotCommand(command='admin', description='Панель владельца')])
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
