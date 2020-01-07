import discord
from discord.ext import commands
import sys, asyncio
from utils.functions import (
    getMemberKillCounts,
    getFormattedMemberKillCounts,
    getAllianceName,
    getKillCount,
    getWarPointsChannel,
    getTotalKillCounts
)
from utils.db import incrementMemberKillCount, setWarPointsChannel
import math as m


class WarCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.next = '\N{BLACK RIGHTWARDS ARROW}'
        self.prev = '\N{LEFTWARDS BLACK ARROW}'
    
    @commands.Cog.listener()
    async def on_message(self, message):

        channel = getWarPointsChannel(message.guild.id)
        if message.channel.name == channel and not message.author.bot and message.attachments:

            allianceId = ''
            name = ''
            test = ''
            try: #[] RULE
                print('lvl 1')
                # first assume nickname with [TAG] name
                test = allianceId = message.author.nick.split(']')[1]
                allianceId = message.author.nick.split(']')[0][1::]
                name = message.author.nick.split(' ')[1]
            except:
                try:
                    # If failed assume name with [TAG] name
                    test = allianceId = message.author.name.split(']')[1]
                    allianceId = message.author.name.split(']')[0][1::]
                    name = message.author.name.split(' ')[1]
                except:
                    try:
                        # If failed assume name with [TAG]name
                        test = allianceId = message.author.name.split(']')[1]
                        allianceId = message.author.name.split(']')[0][1::]
                        name = message.author.name.split(']')[1]
                    except:
                        try: #() RULE
                            # first assume nickname with (TAG) name
                            test = allianceId = message.author.nick.split(')')[1]
                            allianceId = message.author.nick.split(')')[0][1::]
                            name = message.author.nick.split(' ')[1]
                        except:
                            try:
                                # If failed assume name with (TAG) name
                                test = allianceId = message.author.name.split(')')[1]
                                allianceId = message.author.name.split(')')[0][1::]
                                name = message.author.name.split(' ')[1]
                            except:
                                try:
                                    # If failed assume name with (TAG)name
                                    test = allianceId = message.author.name.split(')')[1]
                                    allianceId = message.author.name.split(')')[0][1::]
                                    name = message.author.name.split(')')[1]
                                except:
                                    try: #< RULE
                                        # first assume nickname with <TAG> name
                                        test = allianceId = message.author.nick.split('>')[1]
                                        allianceId = message.author.nick.split('>')[0][1::]
                                        name = message.author.nick.split(' ')[1]
                                    except:
                                        try:
                                            # If failed assume name with <TAG> name
                                            test = allianceId = message.author.name.split('>')[1]
                                            allianceId = message.author.name.split('>')[0][1::]
                                            name = message.author.name.split(' ')[1]
                                        except:
                                            # If failed assume name with <TAG>name
                                            test = allianceId = message.author.name.split('>')[1]
                                            allianceId = message.author.name.split('>')[0][1::]
                                            name = message.author.name.split('>')[1]


            incrementMemberKillCount(message.guild.id, message.author.id, name, allianceId)
            killCount = getKillCount(message.author.id)
            msg = '.\n{}, your **kill** has been recorded :smiling_imp:'.format(message.author.mention)
            msg += '\n```Kill Count: {}```'.format(killCount)
            await message.channel.send(msg)

            await self.bot.process_commands(message)



    @commands.command()
    async def warpointoverride(self, ctx):
        if ctx.message.author.name.lower() != 'bop':
            return

        if len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]

            allianceId = ''
            name = ''
            try: 
                allianceId = member.nick.split(']')[0][1::]
                name = member.nick.split(' ')[1]
            except:
                allianceId = member.name.split(']')[0][1::]
                try:
                    name = member.name.split(' ')[1]
                except:
                    name = member.name.split(']')[1]

            incrementMemberKillCount(ctx.guild.id, member.id, name, allianceId)
            killCount = getKillCount(member.id)
            msg = ".\n{}, {}'s **kill** has been recorded :smiling_imp:".format(ctx.message.author.mention, member.name)
            msg += '\n```{} Kill Count: {}```'.format(member.name, killCount)
            await ctx.message.channel.send(msg)


    @commands.command()
    async def mywarpoints(self, ctx):
        if ctx.guild.id != 524400503967187011:
            return

        killCount = getKillCount(ctx.message.author.id)
        msg = '.\n{}, your **kill** count is below :smiling_imp:'.format(ctx.message.author.mention)
        msg += '\n```Kill Count: {}```'.format(killCount)
        await ctx.message.channel.send(msg)


    @commands.command()
    async def warpoints(self, ctx, allianceId=''):

        if allianceId.lower() == 'begin':
            setWarPointsChannel(ctx.guild.id, ctx.channel.name)
            msg = '.\n{}, This channel **({})** has been set up for warpoints.'.format(ctx.message.author.mention, ctx.channel.name)
            msg += '\n`**Screenshots of kills will now be recorded here** :smiling_imp:'
            await ctx.message.channel.send(msg)
            return

        title = getAllianceName(ctx.guild.id)
        spacer = '\n--------------------------------------------------\n'

        # function to check that reaction is from user who called this command
        def checkUser(reaction, user):
            return user == ctx.message.author
        
        # violations is paged, so we need some variables to help do that correctly
        idx = 0
        maxPage = 15
        page = 1
        numPages = 1
        intro = '[OPENING] Secure connection...\n*Transmitting* sensitive data.. ...\n\n'

        # check to see if a specific player or alliance was mentioned, to add to the query
        alliance = ''
        if (allianceId):
            alliance = allianceId.upper()

        # get this servers violations, and determine number of pages
        results = getMemberKillCounts(ctx.guild.id, alliance)
        allianceTotal = getTotalKillCounts(ctx.guild.id)
        numPages = m.ceil(len(results) / maxPage)
        pageEnd = maxPage if len(results) >= maxPage else len(results)


        killList = getFormattedMemberKillCounts(results[idx:pageEnd])
        embed = discord.Embed(title='**Member Kill Counts**', description=intro+spacer+killList+spacer[1::], color=000000)
        embed.set_author(name=title, icon_url=ctx.guild.icon_url)
        embed.set_footer(text='SECURE CONNECTION: true | Total Kills:{} | pg {}/{}'.format(allianceTotal, page, numPages))
        msg = await ctx.send(embed=embed)

        try:
            while True:
                killList = getFormattedMemberKillCounts(results[idx:pageEnd])
                embed = discord.Embed(title='**Member Kill Counts**', description=intro+spacer+killList+spacer[1::], color=000000)
                embed.set_author(name=title, icon_url=ctx.guild.icon_url)
                embed.set_footer(text='SECURE CONNECTION: true | Total Kills:{} | pg {}/{}'.format(allianceTotal, page, numPages))
                await msg.edit(embed=embed)


                if page > 1:
                    await msg.add_reaction(emoji=self.prev)
                if page * maxPage < len(results):
                    await msg.add_reaction(emoji=self.next)

                reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkUser)

                # page the results forward, reset page number, page end, and the index
                if reaction.emoji == self.next:
                    page += 1
                    idx = pageEnd
                    pageEnd = (page * maxPage) if len(results) >= (page * maxPage) else len(results)

                # page the results backwards, reset page number, page end, and the index
                if reaction.emoji == self.prev:
                    page -= 1
                    pageEnd = idx
                    idx = pageEnd - maxPage

                # clear ALL reactions, reset state of interface.
                await msg.clear_reactions()
            return

        # UH OH TIMED OUT
        except asyncio.TimeoutError:
            embed = discord.Embed(title='**Member Kill Counts**', description=intro+spacer+killList+spacer[1::], color=000000)
            embed.set_author(name=title, icon_url=ctx.guild.icon_url)
            embed.set_footer(text='CONNECTION CLOSED: Session timed out')
            msg = await msg.edit(embed=embed)
            await msg.clear_reactions()
            return





# set the cog up
def setup(bot):
    bot.add_cog(WarCog(bot))
