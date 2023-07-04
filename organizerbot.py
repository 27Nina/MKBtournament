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
    

# !fc コマンドの実装
@bot.command()
async def fc(ctx, fc: str):
    # get_player 関数を呼び出してプレイヤー情報を取得
    player = await get_player(fc=fc)
    if player is not None:
        name = player.name
        await ctx.send(f"The name for FC {fc} is {name}.")
    else:
        await ctx.send("Player not found.")



# get_mmr_from_name 関数の定義
def get_mmr_from_name(name: str) -> Optional[int]:
    # プレイヤー情報を取得
    player = get_player(name=name)
    if player is not None:
        mmr = player.mmr
        return mmr
    else:
        return None


# !name コマンドの実装
@bot.command()
async def name(ctx, name: str):
    # get_mmr_from_name 関数を呼び出してMMRを取得
    player = await get_player(name=name)
    if player is not None:
        mmr = player.mmr
        await ctx.send(f"The MMR for player {name} is {mmr}.")
    else:
        await ctx.send(f"MMR for player {name} not found.")


# !fcmmr コマンドの実装
@bot.command()
async def fcmmr(ctx, *, fcs: str):
    fc_list = fcs.split(",")
    mmr_results = []
    for fc in fc_list:
        # get_player 関数を呼び出してプレイヤー情報を取得
        player = await get_player(fc=fc.strip())
        if player is not None and player.mmr is not None:
            mmr_results.append(f"{player.name} is {player.mmr}.")
        else:
            mmr_results.append(f"MMR for FC {fc.strip()} not found.")

    await ctx.send("\n".join(mmr_results))
        
    
##bot.run(bot.config["token"])

async def main():
    async with bot:
        for extension in initial_extensions:
            await bot.load_extension(extension)
        backup_tournament_data.start()
        await bot.start(os.environ['token'])

asyncio.run(main())
