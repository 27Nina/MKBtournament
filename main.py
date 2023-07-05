import discord
from discord.ext import commands, tasks
import json
import logging
import aiofiles
import asyncio
import os
from dotenv import load_dotenv
import dill as pickle
from os import path
from lounge_api import get_player
from typing import Optional







# .envファイルの内容を読み込見込む
load_dotenv()

logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

initial_extensions = ['cogs.TournamentManager', 'cogs.Tables',
                      'cogs.Registration', 
                      'cogs.TeamManagement']



if path.exists('tournament_data.pkl'):
    with open('tournament_data.pkl', 'rb') as backupFile:
        bot.tournaments = pickle.load(backupFile)
        print("loaded backup file successfully")
else:
    bot.tournaments = {}

@tasks.loop(minutes=1)
async def backup_tournament_data():
    if len(bot.tournaments) == 0:
        return
    async with aiofiles.open('tournament_data.pkl', 'wb') as backupFile:
        await backupFile.write(pickle.dumps(bot.tournaments, pickle.HIGHEST_PROTOCOL))
#backup_tournament_data.start()
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await(await ctx.send("Your command is missing an argument: `%s`" %
                       str(error.param))).delete(delay=10)
        return
    if isinstance(error, commands.CommandOnCooldown):
        await(await ctx.send("This command is on cooldown; try again in %.0fs"
                       % error.retry_after)).delete(delay=5)
        return
    if isinstance(error, commands.MissingAnyRole):
        missing_roles = [str(role) for role in error.missing_roles]
        await(await ctx.send("You need one of the following roles to use this command: `%s`"
                             % (", ".join(missing_roles)))
              ).delete(delay=10)
        return
    if isinstance(error, commands.BadArgument):
        await(await ctx.send("BadArgument Error: `%s`" % error.args)).delete(delay=10)
        return
    if isinstance(error, commands.BotMissingPermissions):
        await(await ctx.send("I need the following permissions to use this command: %s"
                       % ", ".join(error.missing_perms))).delete(delay=10)
        return
    if isinstance(error, commands.NoPrivateMessage):
        await(await ctx.send("You can't use this command in DMs!")).delete(delay=5)
        return
    if isinstance(error, commands.MissingPermissions):
        await(await ctx.send(f"You need the following permissions to use this command: {', '.join(error.missing_permissions)}")).delete(delay=10)
        return
    raise error

##if __name__ == '__main__':
##    for extension in initial_extensions:
##        bot.load_extension(extension)

@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

@bot.command()
async def ping(ctx):
    await ctx.send(f"{fc}")
    

# メッセージの検索コマンド※個人杯
@bot.command()
async def search1(ctx, name):
    tournament_channel_id =   # 組分け情報が記載されているチャンネルのIDを設定してください
    tournament_channel = bot.get_channel(tournament_channel_id)

    message_list = []
    async for message in tournament_channel.history(limit=None):
        message_list.append(message.content)

    message_content = "\n".join(message_list)

    if name in message_content:
        lines = message_content.splitlines()
        for i, line in enumerate(lines):
            if name in line:
                result = lines[i - (i % 14)]
                break
        else:
            result = None
    else:
        result = None

    if result:
        message = f"{name}さんは{result}です。"
    else:
        message = f"{name}さんは組分けされていません。"

    await ctx.send(message)


# メッセージの検索コマンド※タッグ杯
@bot.command()
async def search2(ctx, name):
    tournament_channel_id =   # 組分け情報が記載されているチャンネルのIDを設定してください
    tournament_channel = bot.get_channel(tournament_channel_id)

    message_list = []
    async for message in tournament_channel.history(limit=None):
        message_list.append(message.content)

    message_content = "\n".join(message_list)

    if name in message_content:
        lines = message_content.splitlines()
        for i, line in enumerate(lines):
            if name in line:
                result = lines[i - (i % 8)] # ここの数字を変える
                break
        else:
            result = None
    else:
        result = None

    if result:
        message = f"{name}さんは{result}です。"
    else:
        message = f"{name}さんは組分けされていません。"

    await ctx.send(message)

# メッセージの検索コマンド※プルス
@bot.command()
async def search3(ctx, name):
    tournament_channel_id =   # 組分け情報が記載されているチャンネルのIDを設定してください
    tournament_channel = bot.get_channel(tournament_channel_id)

    message_list = []
    async for message in tournament_channel.history(limit=None):
        message_list.append(message.content)

    message_content = "\n".join(message_list)

    if name in message_content:
        lines = message_content.splitlines()
        for i, line in enumerate(lines):
            if name in line:
                result = lines[i - (i %  6)]
                break
        else:
            result = None
    else:
        result = None

    if result:
        message = f"{name}さんは{result}です。"
    else:
        message = f"{name}さんは組分けされていません。"

    await ctx.send(message)

# メッセージの検索コマンド※フォーマン
@bot.command()
async def search4(ctx, name):
    tournament_channel_id =   # 組分け情報が記載されているチャンネルのIDを設定してください
    tournament_channel = bot.get_channel(tournament_channel_id)

    message_list = []
    async for message in tournament_channel.history(limit=None):
        message_list.append(message.content)

    message_content = "\n".join(message_list)

    if name in message_content:
        lines = message_content.splitlines()
        for i, line in enumerate(lines):
            if name in line:
                result = lines[i - (i %  5)]
                break
        else:
            result = None
    else:
        result = None

    if result:
        message = f"{name}さんは{result}です。"
    else:
        message = f"{name}さんは組分けされていません。"

    await ctx.send(message)

# MKBサイトからインポート機能(仮)これはスクレイピングだけ
@bot.command()
async def get_participants(ctx, cup_number: int):
    url = f"http://japan-mk.blog.jp/mk8dx.cup-{cup_number}"  # 参加者情報が含まれているウェブサイトのURL

    # HTMLを取得
    response = requests.get(url)
    html = response.text

    participant_data = extract_participant_data(html)
    if participant_data:
        formatted_data = format_participant_data(participant_data)
        await ctx.send('参加者情報を取得しました:')
        for data in formatted_data:
            await ctx.send(data)
    else:
        await ctx.send('参加者情報が見つかりませんでした。')

def extract_participant_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    entries = soup.find_all('tr', id='entry')
    participant_data = []
    for entry in entries:
        fc_list = entry.find('span', id='fcList').text.strip()
        participant_data.append(fc_list.split('▣'))

    return participant_data

def format_participant_data(participant_data):
    formatted_data = []
    for data in participant_data:
        name1 = data[0]
        code1 = data[2]
        name2 = data[1]
        code2 = data[3]
        formatted_data.append(f'{name1}（{code1}）{name2}（{code2}）')
    return formatted_data
    
    



    
        
    
##bot.run(bot.config["token"])

async def main():
    async with bot:
        for extension in initial_extensions:
            await bot.load_extension(extension)
        backup_tournament_data.start()
        await bot.start(os.environ['token'])

asyncio.run(main())
