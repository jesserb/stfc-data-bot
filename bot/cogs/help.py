import discord
from discord.ext import commands
import sys, asyncio
from bot.utils.functions import getAllianceIdFromNick, hasRegisterCommandPermission
from bot.utils.constants import GITHUB



class HelpCog:
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def info(self, ctx, *args):

        title = '**DATA BOT INFORMATION**'
        info  = '*Created by **Bop#1308***\n\n'
        info += '×  **version:** 1.0.0 **BETA**\n'
        info += '×  **prefix:** "."\n'
        info += '×  **github:** {}\n'.format(GITHUB)
        footerText = 'Message me with feedback, questions, or anything else'

        embed = discord.Embed(title=title, description=info, color=1234123)
        embed.set_footer(text=footerText)
        await ctx.send(embed=embed)


    

    @commands.command()
    async def help(self, ctx, *args):
        
        allianceId = getAllianceIdFromNick(ctx.message.author.nick)
        adminCommands = ''

        if hasRegisterCommandPermission(ctx.guild.id, allianceId, ctx.message.author.roles):

            adminCommands = '__**Settings Command**: <alliance id>__\n'
            adminCommands += '*returns the settings for the specified alliance id*\n'
            adminCommands += '```×  alliance id: 2 to 4 letter alliance id.```'
            adminCommands += '**Examples:**\n`.settings TEST`\n\n'

            adminCommands += '__**Setup Command**: <alliance id>__\n'
            adminCommands += '*Allows a server amdinistrator to set me up for your data. Needs to be run before using most '
            adminCommands += 'of the commands. You can setup multiple alliances as sub alliances - differentiated by alliance id.*\n'
            adminCommands += '```×  alliance id: 2 to 4 letter alliance id.```'
            adminCommands += '**Examples:**\n`.setup TEST`\n\n'

            adminCommands += '__**Register Command** *(admin)*: <member> <type> <alliance id>__\n'
            adminCommands += '*Admin version of the register command. Sets up the given member based on type and alliance id, '
            adminCommands += 'as specified in your settings for me. Note the __Setup__ command must have been run before this '
            adminCommands += 'command can be used.*\n'
            adminCommands += '```×  member: The user you wish to register`\n'
            adminCommands += '×  type: value of "member". "ally", or "ambassador".`\n'
            adminCommands += '×  alliance id: 2 to 4 letter alliance id.```'
            adminCommands += '**Examples:**\n`.register @Data member TEST`,\n`.register @Data ambassador WX`\n\n'

            adminCommands += '__**Clear Command**: <number>__\n'
            adminCommands += '*returns the settings for the specified alliance id*\n'
            adminCommands += '```×  number: Number of messages to delete in current channel```'
            adminCommands += '**Examples:**\n`.clear 5`\n\n'

        if not len(args):
            title = '\n**DATA COMMANDS OVERVIEW**'

            intro = '*Below are the commands available with me. Do not include "<" or ">" symbols with command*\n\n**KEY**\n'
            intro += '×  `<param>` required parameter.\n×  `[param]` optional parameter.\n'

            commands = '__**Info Command**:__\n'
            commands += '*General DATA bot info, such as version, code repository, and prefix.\n\n'
            commands += '```no paramaters```'
            commands += '**Examples:**\n`.info`\n\n'

            commands = '__**Register Command** *(manual):*__\n'
            commands += '*Allows a user to self register on your server through an interaction with me. I ask questions, '
            commands += 'user answers, and if successful roles and nickname are given out according to bot settings. '
            commands += 'Note the __Setup__ command must have been run before this, and manual register option allowed.*\n'
            commands += '```no paramaters```'
            commands += '**Examples:**\n`.register`\n\n'
            

            # embed = discord.Embed(title=title, description=intro+commands, color=1234123)
            # embed.set_footer(text=footer)
            await ctx.message.author.send('\n{}\n\n{}\n\n{}'.format(title, intro, adminCommands + commands))
        

# set the cog up
def setup(bot):
    bot.add_cog(HelpCog(bot))







