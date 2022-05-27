import hikari
import re

bot = hikari.GatewayBot(token='')


@bot.listen(hikari.MessageCreateEvent)
async def suggestion_wall(event: hikari.GuildMessageCreateEvent):
    if event.is_bot or not event.content:
        return

    if event.channel_id != 937176888005263393:
        return

    find = re.search(r'(?P<film_name>.+?)(.)?(?P<film_url>(?:http|https).*)', event.content)
    name = find.group('film_name')
    url = find.group('film_url')

    print('Film info: {0} {1}'.format(name, url))
