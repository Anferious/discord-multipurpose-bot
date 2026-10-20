import discord
from discord.ext import commands
import asyncio
import aiohttp # Асинхронные запросы (вместо requests)
import random
import os
import yt_dlp as youtube_dl # Современный форк youtube_dl
from dotenv import load_dotenv
import datetime

# Загрузка переменных окружения (токен)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Базовые настройки
PREFIX = '.'
bot_intents = discord.Intents.default()
bot_intents.message_content = True # Необходимо для чтения содержимого сообщений
bot_intents.members = True # Необходимо для модерации и работы с участниками

bot = commands.Bot(command_prefix=PREFIX, intents=bot_intents, help_command=None)

# --- Списки данных ---
HELLO_WORDS = [
    'Привет', 'Салам', 'Бонжур', 'Хеллоу', 'Хай', 'Прывітанне', 
    'Чао', 'Алоха', 'Аве', 'Гутен таг', 'Коничи ва', 'Привіт', 
    'Намасте', 'Ола', 'Салют', 'Гамарджоба', 'Хола'
]

BALL_PHRASES = [
    'бесспорно', 'предрешено', 'никаких сомнений', 'определённо да', 
    'можешь быть уверен в этом', 'мне кажется — «да»', 'вероятнее всего', 
    'хорошие перспективы', 'знаки говорят — «да»', 'да', 
    'пока не ясно, попробуй снова', 'спроси позже', 'лучше не рассказывать', 
    'сейчас нельзя предсказать', 'сконцентрируйся и спроси опять', 
    'даже не думай', 'мой ответ — «нет»', 'по моим данным — «нет»', 
    'перспективы не очень хорошие', 'весьма сомнительно'
]

ANIMALS_LIST = ['fox', 'cat', 'dog', 'panda', 'birb', 'red_panda', 'koala', 'pikachu']


# --- События ---
@bot.event
async def on_ready():
    print(f'Бот {bot.user} успешно запущен и готов к работе!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Наблюдает за сервером'))

# Единый глобальный обработчик ошибок
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, не хватает аргументов для команды! Попробуй `{PREFIX}help`.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас недостаточно прав для выполнения этой команды!')
    elif isinstance(error, commands.CommandNotFound):
        pass # Игнорируем несуществующие команды
    else:
        print(f"Произошла ошибка: {error}")

# --- Информационные команды ---
@bot.command()
async def help(ctx, category: str = 'none'):
    """Показывает список доступных команд"""
    if category == 'none':
        emb = discord.Embed(
            color=discord.Color.orange(), 
            title=f'Навигация по командам (Используйте {PREFIX}help [категория])',
            description='`moder` - Модерация\n`fun` - Развлечения\n`game` - Игры\n`info` - Информация\n`music` - Музыка'
        )
    elif category == 'moder':
        emb = discord.Embed(
            color=discord.Color.red(), title='👮 Команды модерации:',
            description=f'`{PREFIX}ban [@user]` - Забанить\n`{PREFIX}kick [@user]` - Выгнать\n`{PREFIX}clear [кол-во]` - Очистить чат\n`{PREFIX}say [текст]` - Сказать от лица бота'
        )
    elif category == 'fun':
        emb = discord.Embed(
            color=discord.Color.gold(), title='🎭 Развлечения:',
            description=f'`{PREFIX}hello` - Приветствие\n`{PREFIX}ball [вопрос]` - Шар предсказаний\n`{PREFIX}animal` - Случайное животное\n`{PREFIX}kiss/hug/pat/slap [@user]` - РП команды\n`{PREFIX}meme` - Случайный мем'
        )
    # Можно добавить остальные категории аналогично
    else:
        emb = discord.Embed(color=discord.Color.red(), title='Категория не найдена')

    emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=emb)

@bot.command()
async def time(ctx):
    """Показывает текущее время"""
    now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emb = discord.Embed(title='Текущее время серверной машины', color=discord.Color.green())
    emb.add_field(name='Время:', value=f'`{now_date}`')
    emb.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=emb)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    """Показывает аватар пользователя"""
    member = member or ctx.author
    emb = discord.Embed(title=f'Аватар пользователя {member.display_name}', color=discord.Color.orange())
    emb.set_image(url=member.display_avatar.url)
    await ctx.send(embed=emb)

# --- Команды модерации ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 2):
    """Очищает указанное количество сообщений"""
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f'Очищено {amount} сообщений.')
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Не указана"):
    """Выгоняет пользователя с сервера"""
    await member.kick(reason=reason) 
    await ctx.send(f'Участник {member.mention} был выгнан. Причина: {reason}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Не указана"):
    """Банит пользователя на сервере"""
    await member.ban(reason=reason)
    emb = discord.Embed(title='Блокировка', colour=discord.Color.red())
    emb.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    emb.add_field(name='Забанен пользователь', value=f'{member.mention}')
    emb.set_footer(text=f'Модератор: {ctx.author.display_name}', icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=emb)

# --- Развлечения и API ---
# Вспомогательная функция для API запросов
async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command()
async def animal(ctx):
    """Случайное фото животного"""
    animal_type = random.choice(ANIMALS_LIST)
    data = await fetch_json(f'https://some-random-api.com/animal/{animal_type}')
    
    embed = discord.Embed(color=discord.Color.orange(), title=f'Вот твоя случайная картинка ({animal_type})!')
    embed.set_image(url=data.get('image'))
    await ctx.send(embed=embed)

@bot.command()
async def meme(ctx):
    """Случайный мем"""
    data = await fetch_json('https://some-random-api.com/meme')
    embed = discord.Embed(title='Случайный мем', color=discord.Color.purple())
    embed.set_image(url=data.get('image'))
    embed.set_footer(text=f"Категория: {data.get('category')}")
    await ctx.send(embed=embed)

@bot.command()
async def hello(ctx):
    """Бот здоровается"""
    greeting = random.choice(HELLO_WORDS)
    await ctx.send(f'{greeting}, {ctx.author.mention}!')

@bot.command()
async def ball(ctx, *, question: str = None):
    """Магический шар предсказаний"""
    if not question:
        return await ctx.send(f'{ctx.author.mention}, задай вопрос!')
    answer = random.choice(BALL_PHRASES)
    emb = discord.Embed(color=discord.Color.purple(), description=f'**Вопрос:** {question}\n**Ответ:** {answer}')
    await ctx.send(embed=emb)

# РП команды
@bot.command()
async def hug(ctx, member: discord.Member):
    data = await fetch_json('https://some-random-api.com/animu/hug')
    embed = discord.Embed(color=discord.Color.green(), description=f'*{member.mention}, Вас обнял(а) {ctx.author.mention}*')
    embed.set_image(url=data.get('link'))
    await ctx.send(embed=embed)

@bot.command()
async def pat(ctx, member: discord.Member):
    data = await fetch_json('https://some-random-api.com/animu/pat')
    embed = discord.Embed(color=discord.Color.green(), description=f'*{member.mention}, Вас погладил(а) {ctx.author.mention}*')
    embed.set_image(url=data.get('link'))
    await ctx.send(embed=embed)

# --- Игры ---
@bot.command()
async def coin(ctx):
    """Орел или решка"""
    result = random.choice(['Орёл', 'Решка'])
    emb = discord.Embed(color=discord.Color.gold(), title='Подбрасывание монетки:', description=f'Выпало: **{result}**')
    await ctx.send(embed=emb)

@bot.command()
async def dice(ctx, min_val: int = 1, max_val: int = 6):
    """Кинуть кубики (игра с ботом)"""
    user_roll = random.randint(min_val, max_val)
    bot_roll = random.randint(min_val, max_val)

    if user_roll > bot_roll:
        title = "Ты выиграл!"
    elif user_roll < bot_roll:
        title = "Ты проиграл!"
    else:
        title = "Ничья!"

    emb = discord.Embed(color=discord.Color.blurple(), title=title, description=f'Тебе выпало **{user_roll}**, а боту **{bot_roll}**.')
    await ctx.send(embed=emb)

# --- Музыка (Упрощенная и обновленная версия yt-dlp) ---
@bot.command()
async def join(ctx):
    """Подключить бота к голосовому каналу"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await channel.connect()
            await ctx.send(f'Подключился к {channel}')
    else:
        await ctx.send("Вы не находитесь в голосовом канале!")

@bot.command()
async def leave(ctx):
    """Отключить бота от голосового канала"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send('Бот отключился от канала.')
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")

@bot.command(aliases=['pl'])
async def play(ctx, *, url: str):
    """Включить музыку с YouTube"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    if not voice or not voice.is_connected():
        if ctx.author.voice:
            voice = await ctx.author.voice.channel.connect()
        else:
            return await ctx.send("Сначала зайдите в голосовой канал!")

    if voice.is_playing():
        voice.stop()

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.%(ext)s',
        'quiet': True
    }

    msg = await ctx.send("Загрузка трека...")

    # Блокирующие функции (как загрузка видео) нужно выполнять в executor, 
    # чтобы не вешать бота, но для простоты пет-проекта оставим базовый вариант
    try:
        if os.path.exists("song.mp3"):
            os.remove("song.mp3")
            
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        voice.play(discord.FFmpegPCMAudio("song.mp3"))
        await msg.edit(content="🎵 Воспроизведение началось!")
    except Exception as e:
        await msg.edit(content=f"Произошла ошибка при загрузке: {e}")

# Запуск бота
if __name__ == "__main__":
    if not TOKEN:
        print("ОШИБКА: Токен не найден! Проверьте файл .env")
    else:
        bot.run(TOKEN)