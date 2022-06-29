import hikari
import re

import psycopg2

bot = hikari.GatewayBot(token='')
conn = psycopg2.connect(database="postgres", user="postgres",
                        password="password", host="localhost", port=5432)

@bot.listen(hikari.MessageCreateEvent)
async def suggestion_wall(event: hikari.GuildMessageCreateEvent):

    cur = conn.cursor()
    cur.execute('SELECT * FROM recommendations')
    records = cur.fetchall()
    print(records)

    if event.is_bot or not event.content:
        return

    if event.channel_id != 937176888005263393:
        return

    find = re.search(r'(?P<film_name>.+?)(.)?(?P<film_url>(?:http|https).*)', event.content)
    name = find.group('film_name')
    url = find.group('film_url')
    id = event.message.id

    print('Film info: {0} {1} {2}'.format(name, url, id))


@bot.listen(hikari.ReactionAddEvent)
async def suggestion_wall(event: hikari.ReactionAddEvent):
    print('mark added')


@bot.listen(hikari.ReactionDeleteEvent)
async def suggestion_wall(event: hikari.ReactionDeleteEvent):
    print('mark deleted')
