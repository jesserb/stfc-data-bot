import discord
from discord.ext import commands
import sys, asyncio, perms
sys.path.append('../utils')
import functions as f
import data_database as db




class AdministrationCog:
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def test(self, ctx):
        settings = f.getSettings(ctx.guild.id);



    @commands.command()
    async def settings(self, ctx):

        if not ctx.message.author.guild_permissions.administrator:
            err =  '{}, You do not have permission to use this command.'.format(ctx.message.author.mention)
            await ctx.send(err)
            return


        title = 'DATA Bot Settings'
        footerText = '*DATA Bot Setup: url-to-code, bot-help-server*'
        settings = f.getSettings(ctx.guild.id); 

        print(settings)
        summary = '[DECRYPTING] sensitive data... ...\n\n'
        summary += '**ALLIANCE:** {}\n\n'.format(settings['alliance'])

        if settings['manualRegister']:
            summary += '**[YES]** [NO] Users can self register\n'
        else:
            summary += '[YES] **[NO]** Users can self register\n'

        if settings['createChannel']:
            summary += '**[YES]** [NO] Create private channel\n\n'
        else:
            summary += '[YES] **[NO]** Create private channel\n\n'

        summary += '**New Member Role:** {}\n'.format(settings['memberRole'])
        summary += '**New Ambassador Role:** {}\n'.format(settings['ambassadorRole'])
        if settings['channelCategory'] != None:
            summary += '**Private Channel Category:** {}\n'.format(settings['channelCategory'])

        summary += '\n**REGISTER COMMAND**\n*Roles that can set up other users:*\n'
        for r in settings['canRegisterUserRoles']:
            summary += '× {}\n'.format(r)
        summary += '\n'

        summary += '**PRIVATE CHANNEL PERMS**\n*Roles that can set up other users:*\n'
        for r in settings['canAccessPrivateChannelRoles']:
            summary += '× {}\n'.format(r)

        embed = discord.Embed(title=title, description=summary, color=1234123)
        embed.set_footer(text=footerText)
        await ctx.message.author.send(embed=embed)
        await ctx.send('{}, I sent you a private message.'.format(ctx.message.author.mention))



          
    # Function deletes the last 'n' amount of messages
    # in same channel as the command was given in.
    @commands.command()
    async def clear(self, ctx, number=0):

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







