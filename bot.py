import discord
from discord.ext import commands
import keys
import words
import tinydb
from operator import itemgetter

# ---=== Start of init ===---

prefix = '$'

bot = commands.Bot(command_prefix=prefix)


db = tinydb.TinyDB('data.json')
query = tinydb.Query()


async def sendMessage(ctx, message):  # Simple function to send a message on a specified context
    await ctx.send(message)


def updatePoints(userId, points):
    curPoints = db.search(query.id == userId)[0]['points']
    db.update({'points': curPoints + points}, query.id == userId)


# ---=== End of init ===---


@bot.event
async def on_ready():  # Init checking
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Товарищ $help"))
    print('Ready to go.')


@bot.event
async def on_message(message):
    messageContent = message.content.lower().split(' ')  # plits the message listened into a list of words for iteration

    ID = message.author.id

    botMessage = True if ID == bot.user.id else False  # Checks if the message was sent by the bot

    if db.search(query.id == ID) == [] and not botMessage:  # If a user is not on the database, add it
        db.insert({'id': ID, 'points': 0})

    points = 0

    for word in messageContent:
        if not botMessage:
            if word in words.goodWords:
                await message.add_reaction('♥')
                points += 1
            if word in words.badWords:
                await message.add_reaction('😡')
                points -= 1

    if not botMessage:
        updatePoints(ID, points)

    newMessage = [words.changeWords[word] if word in words.changeWords else word for word in messageContent]  # changes words if necessary
    if newMessage != messageContent and not botMessage:  # if the message changes, send it
        newMessage = ' '.join(newMessage)
        # await sendMessage(message.channel, "Camarada, seja um bom comunista e use: " + newMessage)
        await sendMessage(message.channel, "{}*".format(newMessage))
    await bot.process_commands(message)  # see if the message contains any commands


@bot.command()
async def ping(ctx):
    ''' Pings the bot, and returns the ping time'''
    latency = bot.latency
    await ctx.send('The latency is {}'.format(latency))


@bot.command()
async def points(ctx, *, member: discord.Member):
    ''' Displays the amount of CommiePoints a specific user has'''
    p = db.search(query.id == member.id)
    await ctx.send("{} tem {} CommiePoints".format(member.mention, p[0]['points']))


@bot.command()
async def ranking(ctx):
    ''' Display users with more CommiePoints'''
    rank = sorted(db.all(), key=itemgetter('points'), reverse=True)
    newMessage = []
    for i in range(len(rank)):
        user = bot.get_user(rank[i]['id'])
        if user is not None and i < 11:
            userPoints = rank[i]['points']
            newMessage.append("{}. {} com {} CommiePoints\n".format(i+1, user.name, userPoints))
    await ctx.send(''.join(newMessage))

bot.run(keys.TOKEN)
