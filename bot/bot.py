"""
Варианты реакций на фильмы:
    👍 - я хочу посмотреть этот фильм
    👎 - я хочу не смотреть этот фильм
    👀 - да, я увидел запись об этом фильме
    🎞 - фильм посмотрен на киноклубе
"""
import hikari
import lightbulb
import re
import os
from dotenv import load_dotenv
import psycopg2

users_online = list()

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    # keys
    API_KEY = os.environ.get("API_KEY")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    GUILD_ID = int(os.environ.get("GUILD_ID"))
    SUGGESTION_WALL_ID = int(os.environ.get("SUGGESTION_WALL_ID"))
    if not API_KEY or not DATABASE_PASSWORD or not GUILD_ID or not SUGGESTION_WALL_ID:
        print("Some keys are missing")
        os.close(1)


# make sure the port is right (5432 by default)
bot = lightbulb.BotApp(token=API_KEY,
                       default_enabled_guilds=GUILD_ID)
conn = psycopg2.connect(database="postgres",
                        user="postgres",
                        password=DATABASE_PASSWORD,
                        host="localhost",
                        port=5433)


@bot.command
@lightbulb.command('hello', 'Greet your friendly bot')
@lightbulb.implements(lightbulb.SlashCommand)
async def hello(ctx):
    await ctx.respond("I have to return some videotapes")


@bot.command
@lightbulb.command('update_table', 'Adds all suggestions from current chat into the database')
@lightbulb.implements(lightbulb.SlashCommand)
async def update_table(ctx):
    chat = await bot.rest.fetch_messages(ctx.channel_id, after=ctx.channel_id)
    print(type(chat[1]))
    for message in chat:
        if not message.content:
            continue
        add_film_base(message)


def add_film_base(message):
    print("started")
    # parsing
    find = re.search(
        r'(?P<film_name>.+?)\n+(?P<bait>(?:.*\n)+)?(?P<film_url>(?:http|https).*)',
        message.content)
    if not find:
        print("Couldn't find anything")
        return
    name = find.group('film_name')
    url = find.group('film_url')
    if not name or not url:
        print("Non format message")
        return
    name = name.strip()
    url = url.strip()
    bait = find.group('bait')
    bait = bait.strip() if bait else ""
    message_id = message.id
    print(f'Film info: {name}, {bait}, {url}, {message_id}')

    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO recommendations(message_id, film_name, film_bait, film_url, is_watched) VALUES (%s, %s, %s, %s, False);",
                (message_id, name, bait, url))
        except psycopg2.errors.UniqueViolation:
            print("Film already added")
        conn.commit()


def add_emoji_base(message, reaction):
    pass


@bot.listen()
async def add_film(event: hikari.GuildMessageCreateEvent):
    print("debug 1")
    if event.is_bot or not event.content:
        print("empty or not bot")
        return

    if event.channel_id != SUGGESTION_WALL_ID:
        print(f"Wrong channel\n Expected: {SUGGESTION_WALL_ID}\n Received: {event.channel_id}")
        return

    add_film_base(event.message)


@bot.listen()
async def add_emoji(event: hikari.ReactionAddEvent):
    if event.channel_id != SUGGESTION_WALL_ID:
        return
    with conn.cursor() as cur:
        emoji = event.emoji_name
        if emoji == "👍":
            cur.execute(
                "INSERT INTO person_watchlist(message_id, person_id) VALUES (%s, %s);",
                (event.message_id, event.user_id))
            return
        elif emoji == "🎞":
            cur.execute(
                "UPDATE recommendations SET is_watched=%s WHERE message_id=%s;",
                (True, event.message_id))
            return
        else:
            print(f'Unknown emoji ({emoji}) added by {event.user_id}')
        conn.commit()


@bot.listen()
async def delete_emoji(event: hikari.ReactionDeleteEvent):
    if event.channel_id != SUGGESTION_WALL_ID:
        return
    with conn.cursor() as cur:
        emoji = event.emoji_name
        if emoji == "👍":
            cur.execute(
                "DELETE FROM person_watchlist WHERE message_id=%s AND person_id=%s;",
                (event.message_id, event.user_id))
            return
        elif emoji == "🎞":
            cur.execute(
                "UPDATE recommendations SET is_watched=%s WHERE message_id=%s;",
                (False, event.message_id))
            return
        else:
            print(f'Unknown emoji ({emoji}) added by {event.user_id}')
        conn.commit()


@bot.listen()
async def suggestion_wall(event: hikari.VoiceStateUpdateEvent):
    # ивент на подключение к серверу

    if event.old_state.channel_id == event.state.channel_id:
        return

    # кто-то только подключился или отключился
    # кто-то присоединился
    if event.old_state.channel_id is None:
        users_online.append(event.state.user_id)
    # кто-то ушел
    if event.state.channel_id is None:
        users_online.remove(event.state.user_id)



