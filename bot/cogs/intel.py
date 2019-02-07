import discord
from discord.ext import commands
import sys, asyncio
from utils.functions import (
    hasAdminPermission,
    getAllianceIds,
    getRoeRules,
    getAlliesInfo,
    getNapInfo,
    getHomeInfo,
    getAllianceName,
    getAllies,
    getKos,
    getNaps,
    getWar,
    getWarInfo,
    getKosInfo,
    hasIntel,
    hasGeneralInfo,
    getROEViolations,
    getFormattedROEViolations,
    isAllianceMember,
    getFieldIntel
)
from utils.data_database import saveIntellegence, saveROE
from utils.constants import GITHUB
import math as m


class IntelCog:
    
    def __init__(self, bot):
        self.bot = bot
        self.next = '\N{BLACK RIGHTWARDS ARROW}'
        self.prev = '\N{LEFTWARDS BLACK ARROW}'
    
    @commands.command()
    async def intel(self, ctx, *args):

        #ERROR CHECK - dm bot commands not allowed
        try:
            ctx.guild.id # if no guild id then this is a dm
        except:
            error = "**You cannot run bot commands in a DM** "
            error += "Please retry your command in a bot friendly channel in your server where I reside."
            await ctx.message.author.send('{}'.format(error))
            return
        
        # ERROR CHECKING
        aIds = getAllianceIds(ctx.guild.id)
        if not len(aIds):
            msg = '{}, your server has not been set up with me. To use this command, a '.format(ctx.message.author.mention)
            msg += 'server administrator must perform the **.setup <AllianceID>** command first.'
            await ctx.send(msg)
            return

        # ERROR CHECK -> Unless only one argument given, and it be ROE, must be a member to use this command
        if not isAllianceMember(ctx.guild.id, ctx.message.author.roles) and (len(args) != 1 or args[0].lower() != 'roe'):
            msg = '{}, For all intel commands other than **.intel ROE**, '.format(ctx.message.author.mention)
            msg += 'you must be a member to use on this server. '
            await ctx.send(msg)
            return


        #variables
        serverId   = ctx.guild.id
        allianceId = aIds[0]
        roles      = ctx.message.author.roles
        isAdmin    = hasAdminPermission(serverId, allianceId, roles)
        if ctx.message.author.guild_permissions.administrator:
            isAdmin = True
        title      = getAllianceName(serverId)
        descDict = {
            "roe": getRoeRules(serverId, allianceId),
            "ally": getAlliesInfo(serverId, allianceId),
            "nap": getNapInfo(serverId, allianceId),
            "home": getHomeInfo(serverId, allianceId),
            "kos": getKosInfo(serverId, allianceId),
            "war": getWarInfo(serverId, allianceId)
        }
        allianceStandingDict = {
            "ally": 0,
            "nap": 0,
            "kos": 0,
            "war": 0
        }
        infoDict = {
            "aoa": getAllies(serverId),
            "nap": getNaps(serverId),
            "kos": getKos(serverId),
            "war": getWar(serverId)
        }
        intro = '[OPENING] Secure connection...\n'
        intro += '*Transmitting sensitive data.. ...*\n\n'
        footerText = 'SECURE CONNECTION: true, CREDENTIALS CONFIRMED: true'
        info = ''
        spacer = '\n--------------------------------------------------\n'

        # General intel command. SHow them everything we have on the alliance
        if not args:
            if not hasIntel(serverId) and not hasGeneralInfo(serverId):
                info = '{}\n**No Current Intel.....**\n{}'.format(spacer, spacer)
            else:
                info = '{}**Home System**\n{}\n\n**Alliance of Alliances**\n{}{}\n\n**Non Aggression Pacts**\n{}{}\n\n**Kill-on-Sight**\n{}{}\n\n**Declarations of War**\n{}{}{}'.format(
                    spacer,
                    descDict["home"]     if descDict["home"] else '*No home system*\n',
                    infoDict["aoa"]+'\n' if infoDict["aoa"] else '*No Allied Alliances*\n',
                    descDict["ally"],
                    infoDict["nap"]+'\n' if infoDict["nap"] else '*No NAPs*\n',
                    descDict["nap"],
                    infoDict["kos"]+'\n' if infoDict["kos"] else '*No KOS Alliances*\n',
                    descDict["kos"],
                    infoDict["war"]+'\n' if infoDict["war"] else '*No Ongoing Wars*\n',
                    descDict["war"],
                    spacer
                )
                embed = discord.Embed(title='Confidential Intel for {}\n'.format(allianceId), description=intro, color=000000)
                embed.set_author(name=title, icon_url=ctx.guild.icon_url)
                embed.add_field(name='**{} Home System**'.format(allianceId), value=descDict["home"]+'\n**{}**'.format(spacer) if descDict["home"] else '*No home system*\n', inline=False)
                embed.add_field(name='**Allies**', value=getFieldIntel(infoDict["aoa"], 5) if infoDict["aoa"] else '*No Allied Alliances*', inline=True)
                embed.add_field(name='**NAPs**', value=getFieldIntel(infoDict["nap"], 5) if infoDict["nap"] else '*No NAPs*', inline=True)
                embed.add_field(name='**KOS List**', value=getFieldIntel(infoDict["kos"], 2) if infoDict["kos"] else '*No KOS Alliances*', inline=True)
                embed.add_field(name='**Decl. of War**', value=getFieldIntel(infoDict["war"], 5) if infoDict["war"] else '*No Ongoing Wars*', inline=True)
                embed.add_field(name=spacer, value='.', inline=False)
                embed.set_footer(text=footerText)
                await ctx.send(embed=embed)
                return



        ################# ROE COMMANDS #####################

        ## just show embed with ROE rules
        elif len(args) == 1 and args[0].lower() == 'roe':
            toShow = descDict["roe"] if descDict["roe"] else '**ROE Rules have not been set on the server.**'
            embed = discord.Embed(title=title, description='**(ROE) Rules of Engagement**\n\n{}{}{}'.format(spacer, toShow, spacer), color=000000)
            embed.set_footer(text=footerText)
            await ctx.send(embed=embed)
            return
        


        ## Check the single argument. Show results which fit the filter query
        elif len(args) == 1:
            if args[0].lower() == 'allies':
                info = '{}**Alliance of Alliances**\n{}{}{}'.format(
                    spacer, infoDict["aoa"]+'\n' if infoDict["aoa"] else '*No Allied Alliances*\n', descDict["ally"], spacer
                )
            elif args[0].lower() == 'kos':
                info = '{}**Kill-on-Sight**\n{}{}{}'.format(
                    spacer, infoDict["kos"]+'\n' if infoDict["kos"] else '*No KOS Alliances*\n', descDict["kos"], spacer
                )
            elif args[0].lower() == 'nap':
                info = '{}**Non Aggression Pacts**\n{}{}{}'.format(
                    spacer, infoDict["nap"]+'\n' if infoDict["nap"] else '*No NAPs*\n', descDict["nap"], spacer
                )
            elif args[0].lower() == 'wars':
                info = '{}**Declarations of War**\n{}{}{}'.format(
                    spacer, infoDict["war"]+'\n' if infoDict["war"] else '*No Ongoing Wars*\n', descDict["war"], spacer
                )
            elif args[0].lower() == 'home':
                info = '{}**Home System**\n{}{}'.format(
                    spacer, descDict["home"]+'\n' if descDict["home"] else '*No Current Home System*\n', spacer
                )
            else:
                msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
                msg += 'When **intel** command with single argument is used, the argument must be **ROE**, **ALLIES**, **KOS**, '
                msg += '**NAP**, **HOME** or **WARS**.\n*example: .intel WARS, .intel ALLIES*'
                await ctx.send(msg)
                return
        


        ## show embed of alliances who have violated ROE
        ## NEED TO PAGE THESE RUSULTS!, Only case of such
        elif len(args) and args[0].lower() == 'roe' and args[1].lower() == 'violations':

            #ERROR CHECK: -> max of 3 arguments allowed here
            if len(args) > 3:
                if len(args) != 3:
                    msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
                    msg += 'When **intel ROE violations** sequence used, you cannot have more '
                    msg += 'than 3 arguments.\n*example: .intel ROE violations* or specify an alliance: *.intel ROE violations TEST*'
                    await ctx.send(msg)
                    return

            # function to check that reaction is from user who called this command
            def checkUser(reaction, user):
                return user == ctx.message.author
            
            # violations is paged, so we need some variables to help do that correctly
            idx = 0
            maxPage = 10
            page = 1
            numPages = 1
            intro = '[OPENING] Secure connection...\n*Transmitting* sensitive data.. ...\n\n'

            # check to see if a specific player or alliance was mentioned, to add to the query
            query = ''
            if len(args) == 3:
                query = args[2].upper()

            # get this servers violations, and determine number of pages
            results = getROEViolations(serverId, query)
            numPages = m.ceil(len(results) / maxPage)
            pageEnd = maxPage if len(results) >= maxPage else len(results)

            msg = ''
            roeList = ''
            try:
                firstPass = True
                while True:
                    roeList = getFormattedROEViolations(results[idx:pageEnd])
                    embed = discord.Embed(title='**ROE Violation Counts**', description=intro, color=000000)
                    embed.set_author(name=title, icon_url=ctx.guild.icon_url)
                    embed = discord.Embed(title=title, description=intro+spacer+roeList+spacer[1::], color=000000)
                    embed.set_footer(text='SECURE CONNECTION: true | {}/{}'.format(page, numPages))
                    if firstPass:
                        msg = await ctx.send(embed=embed)
                        firstPass = False
                    else:
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
                embed = discord.Embed(title='**ROE Violation Counts**', description=intro, color=000000)
                embed.set_author(name=title, icon_url=ctx.guild.icon_url)
                embed.set_footer(text='CONNECTION CLOSED: Session timed out')
                await msg.edit(embed=embed)
                return

            

        ## show embed of alliances who have violated ROE
        elif len(args) and args[0].lower() == 'roe' and args[1].lower() == 'violation':

            # ERROR CHECK: --> with this scenario, we must have no more than 4 arguments, and no less than 3 arguments
            if len(args) < 3 or len(args) > 4:
                msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
                msg += 'When **intel ROE violation** sequence used, you must include a mandatory alliance abrv. '
                msg += 'as the 3rd argument, with an **optional** player as the 4th argument.\n'
                msg += '*example: .intel ROE violation TEST* or *.intel ROE violation TEST testGuy* or *.intel ROE violation n/a testGuy*'
                await ctx.send(msg)
                return

            if len(args[2]) < 2 or len(args[2]) > 4:
                msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
                msg += 'When **intel ROE violation** sequence used, you must include a mandatory alliance abrv. '
                msg+= 'as the 3rd argument. The value **{}** does not fit the criteria for an alliance abrv.'.format(args[2])
                await ctx.send(msg)
                return

            # ERROR CHECK: --> with this scenario, you must have admin role
            if not isAdmin:
                msg = '{}, **You do not have permission to add to the ROE violations**\n'.format(ctx.message.author.mention)
                await ctx.send(msg)
                return 

            violator = args[2].upper()
            if len(args) == 3:
                saveROE(serverId, args[2].upper()) 
            if len(args) == 4:
                violator = '[{}] {}'.format(args[2].upper(), args[3])
                saveROE(serverId, args[2].upper(), args[3])   
            await ctx.send('{},I have saved the ROE violation by {}.'.format(ctx.message.author.mention, violator))  
            return  


        # Intel is being used to add player or alliance to one of the defined lists. Do so here
        elif len(args) and (args[0].lower() == 'ally' or args[0].lower() == 'kos' or args[0].lower() == 'nap' or args[0].lower() == 'war'):
            if len(args) > 3:
                msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
                msg += 'When **intel {}** sequence used, you cannot have more than 3 total arguments. '.format(args[0].upper())
                await ctx.send(msg)
                return   

            # ERROR CHECK: --> With this scenario, add must follow, and then an alliance acronym
            if args[1].lower() != 'add' and args[1].lower() != 'remove':
                msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
                msg += 'When **intel {}** sequence used, you must include **add** as the 2nd parameter, '.format(args[0].upper())
                msg += 'and the Alliance acronym as the 3rd parameter.\n*example: .intel {} add TEST*'.format(args[0].lower())
                await ctx.send(msg)
                return

            # ERROR CHECK: --> with this scenario, you must have admin role
            if not isAdmin:
                msg = '{}, **You do not have permission to add/remove to the {} list**\n'.format(ctx.message.author.mention, args[0].upper())
                await ctx.send(msg)
                return 

            if args[1].lower() == 'add':
                allianceStandingDict[args[0].lower()] = 1
            if args[1].lower() == 'remove':
                allianceStandingDict[args[0].lower()] = 0

            saveIntellegence(serverId, args[2].upper(), allianceStandingDict)
            await ctx.send('{}, **{} entry {} Saved**.'.format(ctx.message.author.mention,args[0].upper(), args[2].upper()))  
            return

        else:
            msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
            msg += 'I did not understand your query. Please try **.help intel** to see valid arguments '
            msg += 'for the command **intel**.'
            await ctx.send(msg)
            return

        embed = discord.Embed(title='Confidential Intel for {}\n'.format(allianceId), description=intro+info, color=000000)
        embed.set_author(name=title, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=footerText)
        await ctx.send(embed=embed)


      
# set the cog up
def setup(bot):
    bot.add_cog(IntelCog(bot))







