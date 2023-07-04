import discord
from discord.ext import commands, tasks
#from Tournament import Tournament
from objects import Tournament
#import parsing
from algorithms import parsing
from common import yes_no_check, basic_check

class Registration(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.msg_queue = {}
        self._msgqueue_task = self.send_queued_messages.start()

    async def queue(self, ctx, msg):
        if ctx.channel.id not in self.msg_queue.keys():
            self.msg_queue[ctx.channel.id] = []
        self.msg_queue[ctx.channel.id].append(msg)

    @tasks.loop(seconds=2)
    async def send_queued_messages(self):
        for channelid in self.msg_queue.keys():
            channel = self.bot.get_channel(channelid)
            if channel is None:
                continue
            queue = self.msg_queue[channelid]
            if len(queue) > 0:
                sentmsgs = []
                sentmsg = ""
                for i in range(len(queue)-1, -1, -1):
                    sentmsg = queue.pop(i) + "\n" + sentmsg
                    if len(sentmsg) > 1500:
                        sentmsgs.append(sentmsg)
                        sentmsg = ""
                if len(sentmsg) > 0:
                    sentmsgs.append(sentmsg)
                for i in range(len(sentmsgs)-1, -1, -1):
                    await channel.send(sentmsgs[i])

    @commands.command(aliases=['open'])
    async def openRegistrations(self, ctx):
        if ctx.guild.id not in ctx.bot.tournaments:
            await ctx.send("まだ大会は開始されていません")
            return
        tournament = ctx.bot.tournaments[ctx.guild.id]

        tag = False
        miiName = False
        fc = False
        host = False
        
        if tournament.size > 1:
            tagQuestion = await ctx.send("チームの登録にタグを必要としますか？(yes/no)")
            try:
                response = await yes_no_check(ctx)
            except asyncio.TimeoutError:
                await ctx.send("タイムアウトしました。")
                return
            if response.content.lower() == "yes":
                tag = True

        miiQuestion = await ctx.send("登録に登録名を必要としますか？ (yes/no)")
        try:
            response = await yes_no_check(ctx)
        except asyncio.TimeoutError:
            await ctx.send("タイムアウトしました")
            return
        if response.content.lower() == "yes":
            miiName = True
            
        fcQuestion = await ctx.send("登録にFCを必要としますか？(yes/no)")
        try:
            response = await yes_no_check(ctx)
        except asyncio.TimeoutError:
            await ctx.send("タイムアウトしました")
            return
        if response.content.lower() == "yes":
            fc = True

##        hostQuestion = await ctx.send("Do you want to enabled the `!ch` command for players to say if they can host? (yes/no)")
##        try:
##            response = await yes_no_check(ctx)
##        except asyncio.TimeoutError:
##            await ctx.send("Timed out: Cancelled opening registrations")
##            return
##        if response.content.lower() == "yes":
##            host = True
##        else:
##            host = False
            

        e = discord.Embed(title="確認！")
        settings = f"タグが必要か？(チーム形式のみ): **{tag}**\n登録名は必要か？: **{miiName}**\nFCは必要か？: **{fc}**"
        e.add_field(name="設定", value=settings)
        content = "以下の設定で登録を開始したいことを確認してください。 (yes/no):"
        confirmEmbed = await ctx.send(content=content, embed=e)

        try:
            response = await yes_no_check(ctx)
        except asyncio.TimeoutError:
            await ctx.send("タイムアウトしました")
            return
        
        if response.content.lower() == "no":
            try:
                await confirmEmbed.delete()
                await ctx.message.delete()
            except Exception as e:
                pass
            return
        
        tournament.signups = True
        tournament.required_tag = tag
        tournament.required_miiName = miiName
        tournament.required_fc = fc
        tournament.can_channel = ctx.channel.id
        
        await ctx.send("Discordでの登録受付を開始します")

    @commands.command(aliases=['close'])
    async def closeRegistrations(self, ctx):
        if ctx.guild.id not in ctx.bot.tournaments:
            await ctx.send("まだ大会は開始していません")
            return
        tournament = ctx.bot.tournaments[ctx.guild.id]
        tournament.signups = False
        await ctx.send("登録〆切！")
                
    

async def setup(bot):
    await bot.add_cog(Registration(bot))
