import discord
from discord.ext import commands
import sys, asyncio
from concurrent.futures import FIRST_COMPLETED
from contextlib import suppress
from utils.functions import (
    getResourceReliability,
    getSearchQuerys,
    getResourceResults,
    prepareResourceResults,
    getEmoji,
    checkForSTFCEmoji,
    removeSearchParam,
    hasSTFCEmojis
)
import math as m
from utils.data_database import saveResource


class ResourcesCog:
    
    def __init__(self, bot):
        self.bot = bot
        self.next = '\N{BLACK RIGHTWARDS ARROW}'
        self.prev = '\N{LEFTWARDS BLACK ARROW}'



    # This command allows any user of the bot to add a new resource to the Resources database
    # The command works by sending the user a series of questions through a DM. Once the user has completed
    # answer the questions, the results are shown for them to confirm. If the users confirms the data, the info
    # is committed to the resources database

    # PARAMAS
    #  -  NONE. 
    @commands.command()
    async def addresource(self, ctx):

        #ERROR CHECK - dm bot commands not allowed
        try:
            test = ctx.guild.id # if no guild id then this is a dm
        except:
            error = "**You cannot run bot commands in a DM** "
            error += "Please retry your command in a bot friendly channel in your server where I reside."
            await ctx.message.author.send('{}'.format(error))
            return
        

        # Variables
        user = ctx.message.author
        resource = ''
        tier     = 0
        system   = ''
        lvl      = 0
        region   = ''
        step     = 1

        # introduction
        await ctx.send('{}, I sent you a private message about adding your resource.'.format(user.mention))
        msg = 'Hello {}.\n**Through this interface we will add your resource to the current database.**\n'.format(user.mention)
        msg += 'I will ask you a a few questions, and you will have to respond with specific information.\n'
        msg += '**Note** this channel has been made secure, but only temporarily! Take too long to answer, '
        msg += 'and this connection will be closed.\n\n SO. Lets begin...\n **What resource do you wish to add?**\n'
        msg += '*a valid answer would be* **gas**, **ore**, **crystal**, or **dilithium**\n'
        dm = await user.send(msg)


        def checkUser(message):
            return (message.author == ctx.message.author) and (dm.channel.id == message.channel.id)

        try:
            # STEP 1: GET RESOURCE NAME
            ans = await self.bot.wait_for('message', timeout=180, check=checkUser)
            while step < 2:
                if ans.content.lower() == 'gas' or ans.content.lower() == 'ore' or ans.content.lower() == 'crystal' or ans.content.lower() == 'dilithium':
                    if ans.content.lower() == 'dilithium':
                        step = 3
                    else:
                        step = 2
                    resource = ans.content.lower()
                else:
                    msg = '**That response is not recognized.**\n*A valid answer would be* **gas**, **ore**, **crystal**, or **dilithium**\n\n'
                    msg += '**Please respond again with a valid answer.**'
                    await user.send(msg)
                    ans = await self.bot.wait_for('message', timeout=120, check=checkUser)


            # STEP 2: GET RESOURCE GRADE
            if step == 2:
                msg = 'Response recorded.\n**Now, what grade is this resource?**\n'
                msg += '*a valid answer would be* **1**, **2**, **3**, or **4**\n'
                await user.send(msg)
                ans = await self.bot.wait_for('message', timeout=180, check=checkUser)
                while step < 3:
                    if ans.content == '1' or ans.content == '2' or ans.content == '3' or ans.content == '4':
                        step = 3
                        tier = int(ans.content)
                    else:
                        msg = '**That response is not recognized.**\n*A valid answer would be* **1**, **2**, **3**, or **4**\n\n'
                        msg += '**Please respond again with a valid answer.**'
                        await user.send(msg)
                        ans = await self.bot.wait_for('message', timeout=120, check=checkUser)


            # STEP 3: GET SYSTEM NAME
            if step == 3:
                msg = 'Response recorded.\n**Now tell me, what is the name of the system you found this resource in?**\n'
                await user.send(msg)
                ans = await self.bot.wait_for('message', timeout=180, check=checkUser)
                step = 4
                system = ans.content


            # STEP 4: GET SYSTEM LEVEL
            if step == 4:
                msg = 'Response recorded.\n**What level is the above system?**\n*Please provide a number only*\n'
                await user.send(msg)
                ans = await self.bot.wait_for('message', timeout=180, check=checkUser)
                while step < 5:
                    try:
                        lvl = int(ans.content)
                        step = 5
                    except:
                        msg = '**That response is not recognized.**\n*A valid answer is a number, such as* **13**, or **26**\n\n'
                        msg += '**Please respond again with a valid answer.**'
                        await user.send(msg)
                        ans = await self.bot.wait_for('message', timeout=120, check=checkUser)


            # STEP 5: GET REGION NAME
            if step == 5:
                msg = 'Response recorded.\n**Finally, what region is this resource in?**\n'
                msg += '*a valid answer would be* **federation**, **romulan**, **klingon**, or **neutral**\n'
                await user.send(msg)
                ans = await self.bot.wait_for('message', timeout=180, check=checkUser)
                while step < 6:
                    if ans.content.lower() == 'federation' or ans.content.lower() == 'klingon' or ans.content.lower() == 'romulan' or ans.content.lower() == 'neutral':
                        step = 6
                        region = ans.content.lower()
                    else:
                        msg = '**That response is not recognized.**\n*A valid answer would be* **federation**, **romulan**, **klingon**, or **neutral**\n\n'
                        msg += '**Please respond again with a valid answer.**'
                        await user.send(msg)
                        ans = await self.bot.wait_for('message', timeout=120, check=checkUser)


            # STEP 6: CONFIRM RESULTS
            if step == 6:
                msg = 'Response recorded.\nBelow is the resource information, which will be added to the resource database\n'
                msg += '*Please confirm the data below is correct. To do so, respond with **confirm**. Any other response will '
                msg += 'close this channel, and the resource information will not be added:\n\n'
                msg += '**RESOURCE INTELLEGENCE**\n---------------------------\n× Resource: {}\n'.format(resource.title())
                if resource != 'dilithium':
                    msg += '× Grade: {}\n'.format(tier)
                msg += '× System: {} ({})\n'.format(system.title(), lvl)
                msg += '× Region: {}\n---------------------------\n\n'.format(region.title())
                msg += 'Respond with **confirm** to commit above results.\nRespond with **cancel** to cancel this transmission.' 
                await user.send(msg)

                ans = await self.bot.wait_for('message', timeout=180, check=checkUser)
                if ans.content.lower() == 'confirm':
                    msg = '**Committing resource... ...**\n.'
                    await user.send(msg)
                    saveResource(system, lvl, region, resource, tier)
                    reliabilityScore = getResourceReliability(resource, tier, system)
                    if reliabilityScore > 1:
                        msg = '**Resource **[SAVED].\n[RESOURCE] **exists, and is confirmed... ...** This resource will appear '
                        msg += 'with **.resource** command results. Thank you for this information... ... **goodbye**\n[CLOSED]\n'
                        await user.send(msg)
                    else:
                        msg = '**Resource **[SAVED].\n[RESOURCE] **newly discovered... ...** The resource has been saved, but '
                        msg += 'will not appear in the **.resource** command results. **Another user must confirm this '
                        msg += 'information first, to prove it is a legitimate find.**\nThank you for this information... ... **goodbye**\n[CLOSED]\n'
                        await user.send(msg)
                else:
                    msg = '*Transmission cancelled. Cutting secure connection... ... ...* **goodbye**\n[CLOSED]\n'
                    await user.send(msg) 
        # TIME RAN OUT        
        except asyncio.TimeoutError:
            msg = '**[EXCEEDED TIME LIMIT] I cannot maintain a secure line of communication...**\n '
            msg += 'Closing this channel. Information was not saved... **Please try again** ... **goodbye**\n[CLOSED]\n'
            await user.send(msg)          




    # Command presents a list of resources from the database that match the users search parameters. In addition,
    # the results are shown in an imbed, with reactions that represent the current filters. The user can add additional
    # filters by adding more data-stfc-emojis to the embed, and can remove filters by removing data-stfc-emojis from
    # the embed. Results are also paged to make it easier for the user to read.

    # PARAMAS
    #  -  *args: a list of string search parameters, representing desired filters to place on the resources results.
    @commands.command()
    async def resources(self, ctx, *args):


        #ERROR CHECK - dm bot commands not allowed
        try:
            test = ctx.guild.id # if no guild id then this is a dm
        except:
            error = "**You cannot run bot commands in a DM** "
            error += "Please retry your command in a bot friendly channel in your server where I reside."
            await ctx.message.author.send('{}'.format(error))
            return
        

        if len(args) == 2 and args[0].lower() == 'get' and args[1].lower() == 'emojis':
            emojiFile = discord.File('img/data_stfc_emojis.zip')
            await ctx.send('Here they are!', file=emojiFile)
            return

        # function to check that reaction is from user who called this command
        def checkUser(reaction, user):
            return user == ctx.message.author

        # VARIABLES
        footer      = 'FILTERS:'   # embed footer text
        page        = 1            # current page user is on
        pages       = 1            # total pages returned from query
        pageMax     = 15
        idx         = 0            # keep track of where we are at in the results list
        resource    = ''           # filter by resource name
        tier        = ''           # filter by resource tier number
        region      = ''           # filter by region name
        hasEmojis   = hasSTFCEmojis(ctx.guild.emojis)

        # Information at the top of the resources list. Dependent on a few things
        if hasEmojis:
            information = '\n[DECRYPTING] Resource Intel... ...\n\n'
            information += '***Select the "?" emoji at the bottom for\nadditional info on how to use this interface.***\n\n\n'
        else:
            information = '\n[DECRYPTING] Resource Intel... ...\n\n *Select the arrow emojis to page the results.*\n\n'
            information += '⚠️ **NO STFC EMOJIS DETECTED**\n *Loading basic resource table...*\n '
            information += '**Resources works better with the STFC emojis...**\nRun the command **.resources '
            information += 'get emojis** to get the emoji files.\n\n'

        # loop through search parameters, and set resource, region, and tier variable
        footer, resource, region, tier = getSearchQuerys(args, footer, resource, region, tier)

        # THE MAIN GAME! send in the search paramaters and query the database for a list of results!
        results = getResourceResults(resource.title(), tier, region.title())

        # now that you have results, determine the actual number of pages we need to show (MAX PER PAGE = pageMax)
        pages = m.ceil(len(results) / pageMax)

        # finally, determine how many results to show on the upcoming embed page
        pageEnd = pageMax if len(results) >= pageMax else len(results)


        firstPass = True
        try:
            while True:

                # loop through results and format them in a user friendly way. 
                # Check for custom-emoji representations of the results, and show
                # them if they exist on this server
                resourceList = ''
                for i in range(idx, pageEnd):
                    resourceList += prepareResourceResults(ctx.guild.emojis, results[i])


                # prepare the embed
                embed = discord.Embed(title='**STFC Resources**', description=information+resourceList, color=000000)
                embed.set_footer(text=footer + ' | page: {}/{}'.format(page, pages))
                if firstPass:
                    msg = await ctx.send(embed=embed)
                else:
                    await msg.edit(embed=embed)

                firstPass = False

                if hasEmojis:
                    await msg.add_reaction(emoji='❓')

                # determine which emojis to add to interface, based on page number and current filters
                if page > 1:
                    await msg.add_reaction(emoji=self.prev)
                if page * pageMax < len(results):
                    await msg.add_reaction(emoji=self.next)
                if hasEmojis and resource:
                    await msg.add_reaction(emoji=getEmoji(ctx.guild.emojis, resource))
                if hasEmojis and tier:
                    await msg.add_reaction(emoji=getEmoji(ctx.guild.emojis, '{}star'.format(tier)))
                if hasEmojis and region:
                    await msg.add_reaction(emoji=getEmoji(ctx.guild.emojis, region))

                task_1 = asyncio.ensure_future(self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser))
                task_2 = asyncio.ensure_future(self.bot.wait_for('reaction_remove', timeout=60.0, check=checkUser))

                # Wait first of them done:
                tasks = (task_1, task_2)
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                reaction, user = done.pop().result()

                # Cancel others since they're still running, 
                # but we don't need them to be finished:
                for task in pending:
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task


                args = list(args)
                paramaterRemoved = False

                # Need to determine if this was a remove action, by checking which type of filter was interacted with
                if hasEmojis and checkForSTFCEmoji(reaction) and (region.lower() == reaction.emoji.name.lower()):
                    paramaterRemoved = True
                    args = removeSearchParam(args, region) 
                if hasEmojis and checkForSTFCEmoji(reaction) and (resource.lower() == reaction.emoji.name.lower()):
                    paramaterRemoved = True
                    args = removeSearchParam(args, resource) 
                if hasEmojis and checkForSTFCEmoji(reaction) and (tier.lower() == reaction.emoji.name[0]):
                    paramaterRemoved = True
                    args = removeSearchParam(args, '{}star'.format(tier)) 

                if hasEmojis and paramaterRemoved:
                    # loop through search parameters, and set resource, region, and tier variable
                    footer, resource, region, tier = getSearchQuerys(args, footer, resource, region, tier)
                    
                    # THE MAIN GAME! send in the search paramaters and query the database for a list of results!
                    results = getResourceResults(resource.title(), tier, region.title())

                    # now that you have results, determine the actual number of pages we need to show (MAX PER PAGE = pageMax)
                    pages = m.ceil(len(results) / pageMax)

                    # finally, determine how many results to show on the upcoming embed page
                    pageEnd = pageMax if len(results) >= pageMax else len(results)

                # page the results forward, reset page number, page end, and the index
                elif reaction.emoji == self.next:
                    page += 1
                    idx = pageEnd
                    pageEnd = (page * pageMax) if len(results) >= (page * pageMax) else len(results)

                # page the results backwards, reset page number, page end, and the index
                elif reaction.emoji == self.prev:
                    page -= 1
                    pageEnd = idx
                    idx = pageEnd - pageMax

                # HELP EMOJI SELECTED
                # Show a new custom emoji with directions on how to use the interface. Stay on page until
                # the return emoji is selected
                elif reaction.emoji == '❓':
                    # prepare the embed
                    await msg.clear_reactions()
                    help = '**RESOURCES COMMAND HELP**\n\n The results of the resources command are shown on this '
                    help += 'inteface, and is fully interactive. Below are some notes on how to use this interface:\n\n'
                    help += '**1)** The presented results are *"paged"*. The footer of the information tells you '
                    help += 'which page you are on.\n**If there are additional pages:**\n× The {} emoji will appear. '.format(self.next)
                    help += 'Selecting it will page forward.\n**If their are previous pages:**\n× the {} will appear. '.format(self.prev)
                    help += 'Selecting it will page backwards.\n\n**2)** The results can be filtered by **resource**, **resource grade**, '
                    help += 'and **region**. When a filter is active, it will show in the footer under **FILTERS:**, and a corresponding '
                    help += 'emoji representing the filter will be at the bottom of the interface.\nSome things to note:\n\n**× REMOVE FILTER** '
                    help += '- Selecting an active emoji removes both the emoji and the filter from the results.\n\n**× ADD FILTER** - Reacting '
                    help += 'to the interface with a valid STFC emoji adds a new filter to the interface, which is reflected in the results.\n'
                    help += '\n**Valid STFC emojis are:**\n|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|\n'.format(
                        getEmoji(ctx.guild.emojis, 'gas'),
                        getEmoji(ctx.guild.emojis, 'crystal'),
                        getEmoji(ctx.guild.emojis, 'ore'),
                        getEmoji(ctx.guild.emojis, 'dilithium'),
                        getEmoji(ctx.guild.emojis, '2star'),
                        getEmoji(ctx.guild.emojis, '3star'),
                        getEmoji(ctx.guild.emojis, '4star'),
                        getEmoji(ctx.guild.emojis, 'federation'),
                        getEmoji(ctx.guild.emojis, 'klingon'),
                        getEmoji(ctx.guild.emojis, 'romulan'),
                        getEmoji(ctx.guild.emojis, 'neutral'),
                    )
                    embed = discord.Embed(title='**STFC Resources**', description=help, color=000000)
                    embed.set_footer(text='RESOURCES HELP MENU | Select {} to return'.format('❌'))
                    await msg.edit(embed=embed)
                    await msg.add_reaction(emoji='❌')
                    while True:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)
                        if reaction.emoji == '❌':
                            break
                        else:
                            await msg.remove_reaction(emoji=reaction.emoji, member=user)

                # In this block, check if STFC reaction was added, and requery results, and if not, remove the reaction
                else:
                    if hasEmojis and checkForSTFCEmoji(reaction):
                        newSearchParam = getEmoji(ctx.guild.emojis, reaction.emoji.name)
                        args = list(args)
                        args.append(newSearchParam.name) 

                        # loop through search parameters, and set resource, region, and tier variable
                        footer, resource, region, tier = getSearchQuerys(args, footer, resource, region, tier)

                        # THE MAIN GAME! send in the search paramaters and query the database for a list of results!
                        results = getResourceResults(resource.title(), tier, region.title())

                        # now that you have results, determine the actual number of pages we need to show (MAX PER PAGE = pageMax)
                        pages = m.ceil(len(results) / pageMax)

                        # finally, determine how many results to show on the upcoming embed page
                        idx = 0
                        page = 1
                        pageEnd = pageMax if len(results) >= pageMax else len(results)
                    else:
                        await msg.remove_reaction(emoji=reaction.emoji, member=user)
                
                # clear ALL reactions, reset state of interface.
                await msg.clear_reactions()

        # TIMES UP. Avoid error and clear all reactions. Give message in footer to rep state
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            footer = 'TRANSMISSION CLOSED -- SESSION ENDED'
            embed = discord.Embed(title='**STFC Resources**', description=information+resourceList, color=000000)
            embed.set_footer(text=footer + ' | page: {}/{}'.format(page, pages))
            await msg.edit(embed=embed)




# set the cog up
def setup(bot):
    bot.add_cog(ResourcesCog(bot))
