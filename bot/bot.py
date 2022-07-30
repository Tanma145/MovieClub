"""
Варианты реакций на фильмы:
    👍 - я хочу посмотреть этот фильм
    👎 - я хочу не смотреть этот фильм
    🎞 - фильм посмотрен на киноклубе
    👀 - да, я увидел запись об этом фильме
"""
import hikari
import lightbulb
import re
import os
from dotenv import load_dotenv

import psycopg2

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    # keys
    API_KEY = os.environ.get("API_KEY")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    CHANNEL_ID = os.environ.get("CHANNEL_ID")
    if not API_KEY or not DATABASE_PASSWORD or not CHANNEL_ID:
        print("Some keys are missing")
        os.close(1)


# make sure the port is right (5432 by default)
bot = lightbulb.BotApp(token=API_KEY)
conn = psycopg2.connect(database="postgres", user="postgres",
                        password=DATABASE_PASSWORD, host="localhost",
                        port=5433)


@bot.listen()
async def add_film(event: hikari.GuildMessageCreateEvent):
    if event.is_bot or not event.content:
        return

    if event.channel_id != CHANNEL_ID:
        return

    with conn.cursor() as cur:
        find = re.search(r'(?P<film_name>.+?)\n+(?P<bait>(?:.*\n)+)?(?P<film_url>(?:http|https).*)',
                         event.content)
        name = find.group('film_name')
        url = find.group('film_url')
        if not name or not url:
            print("Non format message")
            return
        name = name.strip()
        url = url.strip()
        bait = find.group('bait')
        bait = bait.strip() if bait else ""
        message_id = event.message.id

        print(f'Film info: {name}, {bait}, {url}, {message_id}')
        cur.execute(
            "INSERT INTO recommendations(message_id, film_name, film_bait, film_url, is_watched) VALUES (%s, %s, %s, %s, False);",
            (message_id, name, bait, url))
        conn.commit()


@bot.listen()
async def suggestion_wall(event: hikari.ReactionAddEvent):
    if event.channel_id != CHANNEL_ID:
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
async def suggestion_wall(event: hikari.ReactionDeleteEvent):
    if event.channel_id != CHANNEL_ID:
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
