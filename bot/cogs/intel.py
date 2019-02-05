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
    isAllianceMember
)
from utils.data_database import saveIntellegence, saveROE
from utils.constants import GITHUB



class IntelCog:
    
    def __init__(self, bot):
        self.bot = bot
    
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
        if not isAllianceMember(ctx.guild.id, ctx.guild.roles) and len(args) != 1 and args[0].lower() != 'roe':
            msg = '{}, For all intel commands other than **.intel ROE**, '.format(ctx.message.author.mention)
            msg += 'you must be a member to use on this server. '
            await ctx.send(msg) 


        #variables
        serverId   = ctx.guild.id
        allianceId = aIds[0]
        roles      = ctx.guild.roles
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
        intro = '[OPENING] Secure connection...\n[CREDENTIALS] confirmed...\n'
        intro += '*Transmitting* sensitive data.. ...\n\n**Below is the confidential intel for {}.**\n'.format(allianceId)
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



        ################# ROE COMMANDS #####################

        ## just show embed with ROE rules
        if len(args) == 1 and args[0].lower() == 'roe':
            embed = discord.Embed(title=title, description='**(ROE) Rules of Engagement**\n\n{}{}{}'.format(spacer, descDict["roe"], spacer), color=000000)
            embed.set_footer(text=footerText)
            await ctx.send(embed=embed)
            return
        


        ## jCheck the single argument. Show results which fit the filter query
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
        elif len(args) and args[0].lower() == 'roe' and args[1].lower() == 'violations':

            #ERROR CHECK: -> max of 3 arguments allowed here
            if len(args) > 3:
                if len(args) != 3:
                    msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
                    msg += 'When **intel ROE violations** sequence used, you cannot have more '
                    msg += 'than 3 arguments.\n*example: .intel ROE violations* or specify an alliance: *.intel ROE violations TEST*'
                    await ctx.send(msg)
                    return

            # check to see if a specific player or alliance was mentioned, to add to the query
            query = ''
            if len(args) == 3:
                query = args[2].upper()
            info = '{}{}{}'.format(spacer, getROEViolations(serverId, query), spacer[2::])

            

        ## show embed of alliances who have violated ROE
        elif len(args) and args[0].lower() == 'roe' and args[1].lower() == 'violation':

            # ERROR CHECK: --> with this scenario, we must have exactly 3 arguments
            if len(args) != 3:
                msg = '{}, **Improper use of command!**\n'.format(ctx.message.author.mention)
                msg += 'When **intel ROE violation** sequence used, you must include and ONLY include '
                msg += 'the accused Allaince ID.\n*example: .intel ROE violation TEST*'
                await ctx.send(msg)
                return

            # ERROR CHECK: --> with this scenario, you must have admin role
            if not isAdmin:
                msg = '{}, **You do not have permission to add to the ROE violations**\n'.format(ctx.message.author.mention)
                await ctx.send(msg)
                return 

            saveROE(serverId, args[2].upper()) 
            await ctx.send('{},I have saved the ROE violation by {}.'.format(ctx.message.author.mention, args[2].upper()))  
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

        embed = discord.Embed(title=title, description=intro+info, color=000000)
        embed.set_thumbnail(url = ctx.guild.icon_url)
        embed.set_footer(text=footerText)
        await ctx.send(embed=embed)


      
# set the cog up
def setup(bot):
    bot.add_cog(IntelCog(bot))







