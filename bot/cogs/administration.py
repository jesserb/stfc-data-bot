import discord
from discord.ext import commands
import sys, asyncio
from utils.functions import databaseReset, getSettings, getSetupSummary, isInAlliance


configFile = open('config')
configs = configFile.readlines()
config = {
    'OWNER': {
        'id': (configs[3].split()[1]).split('\n')[0]
    }
}

class AdministrationCog:
    
    def __init__(self, bot):
        self.bot = bot
    



    # Can be used by bot owner only.
    # Command purges the database of all data
    @commands.command()
    async def resetDatabase(self, ctx):
        if (ctx.message.author.id != int(config['OWNER']['id'])):
            return

        databaseReset()
        await ctx.send('{}, database reset'.format(ctx.message.author.mention))


    # Gets the alliance settings associated with this server. The results are made 
    # into an embed, and set privately to the author. Command can only be used by
    # a user with admin perms on the given server

    # PARAMAS
    #  - allianceId: The alliance id the user is getting settings for 
    @commands.command()
    async def settings(self, ctx, allianceId=''):

        #ERROR CHECK - dm bot commands not allowed
        try:
            ctx.guild.id # if no guild id then this is a dm
        except:
            error = "**You cannot run bot commands in a DM** "
            error += "Please retry your command in a bot friendly channel in your server where I reside."
            await ctx.message.author.send('{}'.format(error))
            return
        

        if not allianceId:
            err =  '{}, Missing alliance ID paramater.'.format(ctx.message.author.mention)
            await ctx.send(err)
            return

        if not ctx.message.author.guild_permissions.administrator:
            err =  '{}, You do not have permission to use this command.'.format(ctx.message.author.mention)
            await ctx.send(err)
            return

        if not isInAlliance(ctx.guild.id, allianceId):
            err =  '{}, that allianceId is not registered for your server'.format(ctx.message.author.mention)
            await ctx.send(err)
            return

        title = 'DATA Bot Settings'
        footerText = '*DATA Bot Setup: url-to-code, bot-help-server*'
        settings = getSettings(ctx.guild.id, allianceId.upper(), ctx.guild.roles, ctx.guild.categories) 
        summary = '[DECRYPTING] sensitive data... ...\n\n'
        
        summary += getSetupSummary(
            '{} Settings'.format(ctx.guild.name),
            ctx.guild.id,
            ctx.guild.name,
            allianceId.upper(),
            settings["manualRegister"],
            settings["createChannel"],
            settings["channelCategory"],
            settings["memberRoles"],
            settings["ambassadorRoles"],
            settings["allyRoles"], 
            settings["canRegisterUserRoles"],
            settings["canAccessPrivateChannelRoles"]
        )

        embed = discord.Embed(title=title, description=summary, color=1234123)
        embed.set_footer(text=footerText)
        await ctx.message.author.send(embed=embed)
        await ctx.send('{}, I sent you a private message.'.format(ctx.message.author.mention))



          
    # Function deletes the last 'n' amount of messages
    # in same channel as the command was given in. Must be administrator

    #PARAMS
    # -number - the number of messages to delete, not including this command message
    @commands.command()
    async def clear(self, ctx, number=0):


        #ERROR CHECK - dm bot commands not allowed
        try:
            ctx.guild.id # if no guild id then this is a dm
        except:
            error = "**You cannot run bot commands in a DM** "
            error += "Please retry your command in a bot friendly channel in your server where I reside."
            await ctx.message.author.send('{}'.format(error))
            return
        

        if not ctx.message.author.guild_permissions.administrator:
            err =  '{}, You do not have permission to use this command.'.format(ctx.message.author.mention)
            await ctx.send(err)
            return

        if not number:
            err =  '{}, command requires argument of how many messages to delete.'.format(ctx.message.author.mention)
            await ctx.send(err)
            return
    
        number = int(number) + 1
        counter = 0
        count = 0
        async for x in ctx.channel.history(limit=200):
            count += 1
            if counter < number:
                await x.delete()
                counter += 1


# set the cog up
def setup(bot):
    bot.add_cog(AdministrationCog(bot))







