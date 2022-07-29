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

# make sure the port is right (5432 by default)

bot = hikari.GatewayBot(token=API_KEY)
conn = psycopg2.connect(database="postgres", user="postgres",
                        password=DATABASE_PASSWORD, host="localhost",
                        port=5433)


@bot.listen()
async def suggestion_wall(event: hikari.GuildMessageCreateEvent):
    if event.is_bot or not event.content:
        return

    if event.channel_id != 937_176_888_005_263_393:
        return

    cur = conn.cursor()
    cur.execute('SELECT * FROM recommendations')
    records = cur.fetchall()
    print(records)

    find = re.search(r'(?P<film_name>.+?)\n+(?P<bait>(?:.*\n)+)?(?P<film_url>(?:http|https).*)',
                     event.content)
    name = find.group('film_name').strip()
    url = find.group('film_url').strip()
    bait = find.group('bait')
    bait = bait.strip() if bait else ""
    message_id = event.message.id

    print(f'Film info: {name}, {bait}, {url}, {message_id}')
    cur.execute(
        "INSERT INTO recommendations(message_id, film_name, film_bait, film_url, is_watched) VALUES (%s, %s, %s, %s, False);",
        (message_id, name, bait, url))

    conn.commit()
    cur.close()


@bot.listen()
async def suggestion_wall(event: hikari.ReactionAddEvent):
    if event.channel_id != 937_176_888_005_263_393:
        return

    with conn.cursor() as cur:
        emoji = event.emoji_name
        "INSERT INTO person_watchlist(message_id, person_id) VALUES ($1, $2);"
        if emoji == "👍":
            cur.execute(
                "INSERT INTO person_watchlist(message_id, person_id) VALUES ($1, $2);",
                (event.message_id, event.user_id))
            return
        elif emoji == "🎞️":
            cur.execute(
                "UPDATE recommendations SET is_watched=$1 WHERE message_id=$2;",
                (True, event.message_id))
            return
        else:
            print(f'Unknown emoji ({emoji}) added by {event.user_id}')
    conn.commit()
    cur.close()

@bot.listen()
async def suggestion_wall(event: hikari.ReactionAddEvent):
    print('mark added')
