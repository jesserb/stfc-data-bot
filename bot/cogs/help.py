import discord
from discord.ext import commands
import sys, asyncio
from utils.functions import getAllianceIdFromNick, hasAdminPermission, isAllianceMember
from utils.constants import GITHUB



class HelpCog:
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def info(self, ctx, *args):

        title = '**DATA BOT INFORMATION**'
        info  = '*Created by **Bop#1308***\n\n'
        info += '×  **version:** 1.0.0 **ALPHA**\n'
        info += '×  **prefix:** "."\n'
        info += '×  **help command:** `.help`\n'
        info += '×  **github:** {}\n'.format(GITHUB)
        footerText = 'Message me with feedback, questions, or anything else'

        embed = discord.Embed(title=title, description=info, color=1234123)
        embed.set_footer(text=footerText)
        await ctx.send(embed=embed)


    

    @commands.command()
    async def help(self, ctx, type=''):

        #ERROR CHECK - dm bot commands not allowed
        if type:
            try:
                test = ctx.guild.id # if no guild id then this is a dm
            except:
                error = "**You cannot run bot commands in a DM** "
                error += "Please retry your command in a bot friendly channel in your server where I reside."
                await ctx.message.author.send('{}'.format(error))
                return
        
        try:
            allianceId = ''
            isAdmin = False
            isMember = False
            if type and type.lower() != 'resources':
                allianceId = getAllianceIdFromNick(ctx.message.author.nick)
                isAdmin = hasAdminPermission(ctx.guild.id, allianceId, ctx.message.author.roles)
                isMember = isAllianceMember(ctx.guild.id, ctx.message.author.roles)


            title = '**DATA COMMANDS OVERVIEW**'
            intro = '***Below are the commands for the `{}` class of commands***\n'.format(type)
            intro += '*Do not include "<" or ">" symbols with command*\n\n**KEY**\n'
            intro += '×  `<param>` required parameter.\n×  `[param]` optional parameter.\n×  `*param` a list of space-seperated parameters.'



            adminSetupCommands = '__**Settings Command**: <alliance id>__\n'
            adminSetupCommands += '*returns the settings for the specified alliance id*\n'
            adminSetupCommands += '```×  alliance id: 2 to 4 letter alliance id.```'
            adminSetupCommands += '**Examples:**\n`.settings TEST`\n\n'

            adminSetupCommands += '__**Setup Command**: <alliance id>__\n'
            adminSetupCommands += '*Allows a server administrator to set me up for your data. Needs to be run before using most '
            adminSetupCommands += 'of the commands. You can setup multiple alliances as sub alliances - differentiated by alliance id.*\n'
            adminSetupCommands += '```×  alliance id: 2 to 4 letter alliance id.```'
            adminSetupCommands += '**Examples:**\n`.setup TEST`\n\n'

            adminSetupCommands += '__**Set Command**: <type> info__\n'
            adminSetupCommands += '*Allows a server administrator to save general info about how the alliance treats Allies, NAP agreements, '
            adminSetupCommands += 'KOS alliances, and alliances at war with, the ROE rules, and info about your alliance home system.*\n'
            adminSetupCommands += '```×  type: value of "ally" "nap" "kos" "war" "roe" or "home"```'
            adminSetupCommands += '**Examples:**\n`.setup TEST`\n\n'

            adminRegisterCommands = '__**Register Command** *(admin)*: <member> <type> <alliance id>__\n'
            adminRegisterCommands += '*Admin version of the register command. Sets up the given member based on type and alliance id, '
            adminRegisterCommands += 'as specified in your settings for me. Note the __Setup__ command must have been run before this '
            adminRegisterCommands += 'command can be used.*\n'
            adminRegisterCommands += '```×  member: The user you wish to register\n'
            adminRegisterCommands += '×  type: value of "member". "ally", or "ambassador".\n'
            adminRegisterCommands += '×  alliance id: 2 to 4 letter alliance id.```'
            adminRegisterCommands += '**Examples:**\n`.register @Data member TEST`,\n`.register @Data ambassador WX`\n\n'

            memberIntelCommands = '__**Intel Command**: [intel category] [intel type] <action> <member/alliance>__\n'
            memberIntelCommands += '*returns intel about the alliance, or can be used to add intel for the alliance. This '
            memberIntelCommands += 'command is "protected", as in only members of your alliance can use it.*\n'
            memberIntelCommands += '**When used to show intel**'
            memberIntelCommands += '```×  intel category: value of "allies", "NAP", "ROE", "ROE violations", "wars"```'
            memberIntelCommands += '**Examples:**\n`.intel allies` or `.intel ROE violations`\n\n'
            adminIntelCommands  = '**When used to add intel** *must be designated admin from setup*'
            adminIntelCommands += '```×  intel type: value of "ally" "nap" "kos" or "war".\n'
            adminIntelCommands += '×  action: "add" or "remove"\n'
            adminIntelCommands += '×  member/alliance: The member or alliance name to be added```'
            adminIntelCommands += '**Examples:**\n`.intel ally add TEST` or `.intel kos ADD thatOneGuy`\n\n'

            adminIntelCommands += '**When used to add ROE violations** *must be designated admin from setup*'
            adminIntelCommands += '```×  intel type: value of "ROE violation".\n'
            adminIntelCommands += '×  member/alliance: The member or alliance name to add violation to```'
            adminIntelCommands += '**Examples:**\n`.intel ROE violation TEST` or `.intel ROE violation thatOneGuy`\n\n'

            adminCommands = '__**Clear Command**: <number>__\n'
            adminCommands += '*returns the settings for the specified alliance id*\n'
            adminCommands += '```×  number: Number of messages to delete in current channel```'
            adminCommands += '**Examples:**\n`.clear 5`\n\n'

            resourceCommands = '__**Resources Command**: [resource] [grade] [region]__\n'
            resourceCommands += '*returns an interactive list of resources. Works better if you have the '
            resourceCommands += 'STFC custom emojis. When running the command, select the **"?"** emoji '
            resourceCommands += 'for more information on how to use it.*\n'
            resourceCommands += '```×  resource: A valid STFC resource: "gas", "ore", "crystal", or "dilithium"\n'
            resourceCommands += '×  grade: A valid STFC resource grade: "2", "3", or "4"\n'
            resourceCommands += '×  region: A valid STFC region: "neutral", "federation", "romulan", or "klingon"```'
            resourceCommands += '**Examples:**\n`.resources` or `.resources klingon 3` or `.resources gas 2 neutral`\n\n'

            resourceCommands += '__**Add Resource Command**__\n'
            resourceCommands += '*Sends the user a private message, where through interacting with me, '
            resourceCommands += 'allows the user to add a resource to the database.* ***NOTE*** a resource must '
            resourceCommands += 'be added at least twice to show up in the public resources command.\n'
            resourceCommands += '```NO PARAMETERS```'
            resourceCommands += '**Examples:**\n`.addresources`\n\n'


            genRegisterCommands = '__**Register Command** *(manual):*__\n'
            genRegisterCommands += '*Allows a user to self register on your server through an interaction with me. I ask questions, '
            genRegisterCommands += 'user answers, and if successful roles and nickname are given out according to bot settings. '
            genRegisterCommands += 'Note the __Setup__ command must have been run before this, and manual register option allowed.*\n'
            genRegisterCommands += '```no paramaters```'
            genRegisterCommands += '**Examples:**\n`.register`\n\n'

            
            if not type:
                title = '**DATA COMMANDS OVERVIEW**'

                intro = '*Below are general commands. To see more sepcific commands, include an argument reresenting the class '
                intro += 'of commands your looking for with the help command.\n**The following help commands are available:**\n'
                intro += '`.help admin`\n`.help intel`\n`.help register`\n`.help setup`\n`.help resources`\n\nDo not include "<" or ">" symbols with command*\n\n**KEY**\n'
                intro += '×  `<param>` required parameter.\n×  `[param]` optional parameter.\n×  `*param` a list of space-seperated parameters.'

                genCommands = '__**Info Command**:__\n'
                genCommands += '*General DATA bot info, such as version, code repository, and prefix.\n\n'
                genCommands += '```no paramaters```'
                genCommands += '**Examples:**\n`.info`\n\n'

                await ctx.message.author.send('.\n{}\n\n{}\n\n{}'.format(title, intro, genCommands+genRegisterCommands))
                await ctx.send('{}, I sent you a DM witth general bot command instructions').format(ctx.message.author.mention)

            if type.lower() != 'resources' and isAdmin and type.lower() == 'admin':
                await ctx.message.author.send('.\n{}\n\n{}\n\n{}'.format(
                    title,
                    intro,
                    adminCommands + adminSetupCommands
                    )
                )
                await ctx.message.author.send('.\n{}'.format(
                    adminRegisterCommands + adminIntelCommands
                    )
                )


            if type.lower() != 'resources' and type.lower() == 'intel':
                toShow = ''
                if isMember:
                    toShow = memberIntelCommands
                if isAdmin:
                    toShow = memberIntelCommands + adminIntelCommands
                if not isMember and not isAdmin:
                    memberIntelCommands = '__**Intel Command**: <ROE>__\n'
                    memberIntelCommands += '*returns the ROE guidelines as they are currently set on this server.*\n'
                    memberIntelCommands += '```×  ROE: must have value ROE```'
                    memberIntelCommands += '**Examples:**\n`.intel ROE`\n\n'
                    toShow = memberIntelCommands
                
                await ctx.message.author.send('.\n{}\n\n{}\n\n{}'.format(title, intro, toShow))
                await ctx.send('{}, I sent you a DM witth intel command instructions').format(ctx.message.author.mention)

            if type.lower() != 'resources' and isAdmin and type.lower() == 'setup':
                await ctx.message.author.send('.\n{}\n\n{}\n\n{}'.format(title, intro, adminSetupCommands))
                await ctx.send('{}, I sent you a DM witth setup command instructions').format(ctx.message.author.mention)

            if type.lower() != 'resources' and type.lower() == 'register':
                toShow = genRegisterCommands
                if isAdmin:
                    toShow = adminRegisterCommands + genRegisterCommands
                await ctx.message.author.send('.\n{}\n\n{}\n\n{}'.format(title, intro, toShow))
                await ctx.send('{}, I sent you a DM witth register command instructions').format(ctx.message.author.mention)

            if type.lower() == 'resources':
                await ctx.message.author.send('.\n{}\n\n{}\n\n{}'.format(title, intro, resourceCommands))
                await ctx.send('{}, I sent you a DM witth resources command instructions').format(ctx.message.author.mention)

        except:
            error = "**[ERROR] something went wrong... ...\n\n Have you run Setup before?\n if you have never run setup "
            error += "you must do so before you can use the help commands."
            await ctx.message.author.send('{}'.format(error))
            

# set the cog up
def setup(bot):
    bot.add_cog(HelpCog(bot))







