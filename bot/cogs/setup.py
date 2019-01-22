import discord
from discord.ext import commands
import sys, asyncio, perms
sys.path.append('../utils')
import functions as f
import data_database as db
from constants import ORDERED_REACTIONS, IN_MESSAGE_REACTIONS



class SetupCog:
    
    def __init__(self, bot):
        self.bot = bot
        self.next = '\N{BLACK RIGHTWARDS ARROW}'
    

    @commands.command()
    async def setup(self, ctx, *args):

        # Some quick error checking
        if not ctx.message.author.guild_permissions.administrator:
            err =  '{}, You do not have permission to use this command.\n**must be Administrator**'.format(ctx.message.author.mention)
            await ctx.send(err)
            return

        if len(args) != 1:
            err =  '{}, command requires single argument: **4 letter Alliance acronym**.'.format(ctx.message.author.mention)
            await ctx.send(err)
            return



        ### DEFINE CONSTANTS ###

        # for embed interface
        title = 'DATA Bot Setup'
        footerText = '*DATA Bot Setup: url-to-code, bot-help-server*'

        # settings variables.
        allianceAcronym              = args[0].upper()   # The acronym for the alliance on this server                 
        roles                        = []                # the roles on this server
        registerCommandRoleSelection = []                # container for role selection to use register admin command
        privateChannelRoleSelection  = []                # container for role selection to to have perms. to view private chnl
        allowManualRegister          = False             # allow manual version of register command on this server
        allowPrivateChannelCreation  = False             # allow bot to create private channel for ambassadors
        selectedCategory             = None              # the category to place newly created channels in
        memberRole                   = None
        ambassadorRole               = None
        
        # setup some data, get server roles, and set roleSelection variables to false by default
        for r in ctx.guild.roles:
            if r.name != 'DATA':
                roles.append(r)
                registerCommandRoleSelection.append({'role': r, 'selected': False})
                privateChannelRoleSelection.append({'role': r, 'selected': False})



        ### BEGIN INTERFACE SETUP MODE ###
        #Begin dialog with introduction screen
        desc = 'Initiate setup mode...\n\n'
        desc += '**Alliance Established: {}**... ...\n\n'.format(allianceAcronym)
        desc += 'Hello.\n\nThrough this interface, I shall guide you through setup. '
        desc += 'It is reccommended that you complete the setup entirely. **If you take to long to respond, '
        desc += 'this interface will be destroyed, and you will have to run the setup command again.**\n\n'
        desc += 'All interactions should be through **selecting the attached symbols** at the bottom of '
        desc += 'interface.\n\n**Please select the :arrow_right: symbol to continue...**'
        embed = discord.Embed(title=title, description=desc, color=1234123)
        embed.set_footer(text=footerText)
        msg = await ctx.channel.send(embed=embed)
        
        # Add reaction for user to move to next screen
        await msg.add_reaction(self.next)
        
        # the following 2 functions are used to check user reaction responses
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == self.next

        def checkUser(reaction, user):
                return user == ctx.message.author

        # Wait for user response, make sure the reaction is the 'NEXT' reaction and from user
        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)





        # STEP 1: Determine new member role
        # determine wwhat role to assign new members on arrival

        # post explanation to interface to explain how to use this screen
        explanation = '**New Member Role**\n\n In order to setup alliance members, I need to know which '
        explanation += 'role will be auto-assigned when using the register command with the argument '
        explanation += '**member**\n\n'
        explanation += '**Please select the corresponding symbols which represent which role should be granted to members.**\n\n'
        
        
        # set up a list of roles on this server
        desc = ''
        for i in range(len(roles)):
            desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

        # prepare embed interface for post
        embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
        embed.set_footer(text=footerText+' |    step 1/8')
        await msg.clear_reactions()
        await msg.edit(embed=embed)

        # add reactions corresponding to each role in list above.
        for i in range(len(roles)):
            await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
        
        # interpret user interactions. Keep accepting responses until break logic
        while True:
        
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

            # need to figure out which role the users reaction corresponds with
            # this will either select or deselect a role depending on role selection state
            for i in range(len(roles)):
                if reaction.emoji == ORDERED_REACTIONS[i]:
                    memberRole = roles[i]
                    break

            if memberRole != None:
                break

            # if we are still in loop, then reaction is invalid
            msg.remove_reaction(emoji=reaction.emoji, member=user)







        # STEP 2: Determine new ambassador role
        # determine wwhat role to assign new ambassadors on arrival

        # post explanation to interface to explain how to use this screen
        explanation = '**New Ambassador Role**\n\n In order to setup non alliance members, I need to know which '
        explanation += 'This role will be auto-assigned when using the register command with the argument '
        explanation += '**ambassador**\n\n**Please select the corresponding '
        explanation += 'symbols which represent which role should be granted to ambassadors.**\n\n'
        
        # set up a list of roles on this server
        desc = ''
        for i in range(len(roles)):
            desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

        # prepare embed interface for post
        embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
        embed.set_footer(text=footerText+' |    step 2/8')
        await msg.clear_reactions()
        await msg.edit(embed=embed)

        # add reactions corresponding to each role in list above.
        for i in range(len(roles)):
            await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
        
        # interpret user interactions. Keep accepting responses until break logic
        while True:
        
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

            # need to figure out which role the users reaction corresponds with
            # this will either select or deselect a role depending on role selection state
            for i in range(len(roles)):
                if reaction.emoji == ORDERED_REACTIONS[i]:
                    ambassadorRole = roles[i]
                    break

            if ambassadorRole != None:
                break

            # if we are still in loop, then reaction is invalid
            msg.remove_reaction(emoji=reaction.emoji, member=user)





        # STEP 3
        # Select roles that can use admin version of register

        # post explanation to interface to explain how to use this screen
        explanation = '**Command register**\n\nThe register command allows one to setup a new user to your server. '
        explanation += 'Please select the corresponding symbols which represent which roles you want allow to use '
        explanation += 'this command.\n\n'

        # set up a list of roles on this server
        desc = ''
        for i in range(len(roles)):
            desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

        # prepare embed interface for post
        embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
        embed.set_footer(text=footerText+' |    step 3/8')
        await msg.clear_reactions()
        await msg.edit(embed=embed)

        # add reactions corresponding to each role in list above.
        for i in range(len(roles)):
            await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
        
        # interpret user interactions. Keep accepting responses until break logic
        while True:
        
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

            # if user reacts with 'NEXT', move to next interface
            if reaction.emoji == self.next:
                break

            # need to figure out which role the users reaction corresponds with
            # this will either select or deselect a role depending on role selection state
            desc = ''
            for i in range(len(roles)):

                # in first block, handle selected emoji and its role
                if reaction.emoji == ORDERED_REACTIONS[i]:

                    #if role is currently not selected, select it - otherwise deselect it
                    if not f.selectedRole(registerCommandRoleSelection, roles[i]):
                        registerCommandRoleSelection[i]['selected'] = True
                        desc +='{} {}  {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name, '✅')
                    else:
                        f.deselectRole(registerCommandRoleSelection, roles[i])
                        desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

                # for all other roles, show based on state in registerCommandRoleSelection state
                else:
                    if registerCommandRoleSelection[i]['selected']:
                        desc +='{} {}  {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name, '✅')
                    else:
                        desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # once user has at least one selected role, explain how to move on to next step
            if len(registerCommandRoleSelection) > 0:
                desc += '\n**When you have selected all your roles, please select the :arrow_right: symbol to continue...**'

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 3/8')
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            # add reactions corresponding to each role in list above.
            for i in range(len(roles)):
                await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

            # add 'next' emoji once there is at least one selected role
            if len(registerCommandRoleSelection) > 0:
                await msg.add_reaction(self.next)



        # STEP 4
        # Determine if new users will be able to use manual version of register

        # post explanation to interface to explain how to use this screen
        explanation = '**Command register** *manual mode*\n\nThe register command comes with a manual mode, which allows '
        explanation += 'new users to set up themselves through an interactive private conversation with me. '
        explanation += 'this is useful for when no one with permission is around to register the user.\n\n'
        explanation += 'In manual mode, I send the user a series of questions to determine if they are an alliance '
        explanation += 'member, or an ambassador to your server. I also determine their alliance acronym, and set their '
        explanation += 'nickname for them.\n\n'
        desc = '**Would you like to allow new users to use the manual version of the register command?**'

        # prepare embed interface for post
        embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
        embed.set_footer(text=footerText+' |    step 4/8')
        await msg.clear_reactions()
        await msg.edit(embed=embed)
        await msg.add_reaction(emoji='👍')
        await msg.add_reaction(emoji='👎')

        while True:
            #wait for user to react
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

            #Interpret response
            if reaction.emoji == '👍':
                allowManualRegister = True
                break
            elif reaction.emoji == '👎':
                allowManualRegister = False
                break
            else:
                msg.remove_reaction(emoji=reaction.emoji, member=user)



        # STEP 5
        # Determine if bot should create private channel for non alliance users

        # post explanation to interface to explain how to use this screen
        explanation = '**Command register** *create private channel*\n\nAfter setting up a new user from another '
        explanation += 'alliance, either through the admin or manual process, I have the ability to setup a private  '
        explanation += 'channel between members of said alliance your alliance. These channels are useful for private '
        explanation += 'conversations between the leaders of both alliances, in order to settle feuds or work out treaties.\n\n'
        explanation += '**New ambassadors for a previously created private channel will simply be given permission to access '
        explanation += 'to acces the already established private alliance channel. Additionally, if you choose this feature, on '
        explanation += 'next screen we will determine which roles on your server should have access to this new channel.**\n\n'
        desc = '**Would you like me to create a private channel between your alliance leaders and new alliance ambassadors '
        desc += 'after user setup?**'

        # prepare embed interface for post
        embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
        embed.set_footer(text=footerText+' |    step 5/8')
        await msg.clear_reactions()
        await msg.edit(embed=embed)
        await msg.add_reaction(emoji='👍')
        await msg.add_reaction(emoji='👎')

        while True:
            #wait for user to react
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)
            
            #Interpret response
            if reaction.emoji == '👍':
                allowPrivateChannelCreation = True
                break
            elif reaction.emoji == '👎':
                allowPrivateChannelCreation = False
                break
            else:
                msg.remove_reaction(emoji=reaction.emoji, member=user)



        # STEP 6: if step 3 was thumbs up
        # determine which alliance roles will have access to new private channel
        if allowPrivateChannelCreation:

            # post explanation to interface to explain how to use this screen
            explanation = '**Please select the corresponding symbol which represents the role(s) you wish '
            explanation += 'to have access to newly created private channels with other alliances**\n\n'

            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 6/8')
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            # add reactions corresponding to each role in list above.
            for i in range(len(roles)):
                await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

            # interpret user interactions. Keep accepting responses until break logic
            while True:
            
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

                # if user reacts with 'NEXT', move to next interface
                if reaction.emoji == self.next:
                    break

                # need to figure out which role the users reaction corresponds with
                # this will either select or deselect a role depending on role selection state
                desc = ''
                for i in range(len(roles)):

                    # in first block, handle selected emoji and its role
                    if reaction.emoji == ORDERED_REACTIONS[i]:

                        #if role is currently not selected, select it - otherwise deselect it
                        if not f.selectedRole(privateChannelRoleSelection, roles[i]):
                            privateChannelRoleSelection[i]['selected'] = True
                            desc +='{} {}  {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name, '✅')
                        else:
                            f.deselectRole(privateChannelRoleSelection, roles[i])
                            desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

                    # for all other roles, show based on state in privateChannelRoleSelection state
                    else:
                        if privateChannelRoleSelection[i]['selected']:
                            desc +='{} {}  {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name, '✅')
                        else:
                            desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

                # once user has at least one selected role, explain how to move on to next step
                if len(privateChannelRoleSelection) > 0:
                    desc += '\n**When you have selected all your roles, please select the :arrow_right: symbol to continue...**'

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 6/8')
                await msg.clear_reactions()
                await msg.edit(embed=embed)
                for i in range(len(roles)):
                    await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

                # add 'next' emoji once there is at least one selected role
                if len(privateChannelRoleSelection) > 0:
                    await msg.add_reaction(self.next)




            # STEP 7: if step 3 was thumbs up
            # determine which category to place new channel in

            # post explanation to interface to explain how to use this screen
            explanation = '**Private Channel Location**\n\n I have the ability to move the newly created channel into a specific '
            explanation += 'category for organization if you would like. Otherwise, the channel will be placed at the top of the  '
            explanation += 'channels list on your server.\n\n**Please select which category you wish to have the newly created channels placed. '
            explanation += 'select :arrow_right:* to place channel in the default position - at the top of the channels list.**\n\n'
            
            # set up a list of categories for post
            desc = ''
            categories = ctx.guild.categories
            for i in range(len(categories)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], categories[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 7/8')
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            # add reactions corresponding to each category on the server.
            for i in range(len(categories)):
                await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
            
            # this step is optional, so add next reaction for them to skip
            await msg.add_reaction(self.next)

            while True:
            
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

                if reaction.emoji == self.next:
                    break

                for i in range(len(categories)):
                    if reaction.emoji == ORDERED_REACTIONS[i]:
                        selectedCategory = categories[i]
                        break

                if selectedCategory != None:
                    break

                # if we are still in loop, then reaction is invalid
                msg.remove_reaction(emoji=reaction.emoji, member=user)




        # STEP 8
        # Summarize user settings

        explanation = '**Summary of Setup**\n\nBelow is your server settings.\n\n'
        summary = '**ALLIANCE:** {}\n\n'.format(allianceAcronym)

        if allowManualRegister:
            summary += '**[YES]** [NO] Users can self register\n'
        else:
            summary += '[YES] **[NO]** Users can self register\n'

        if allowPrivateChannelCreation:
            summary += '**[YES]** [NO] Create private channel\n\n'
        else:
            summary += '[YES] **[NO]** Create private channel\n\n'

        summary += '**New Member Role:** {}\n'.format(memberRole.name)
        summary += '**New Ambassador Role:** {}\n'.format(ambassadorRole.name)
        if selectedCategory != None:
            summary += '**Private Channel Category:** {}\n'.format(selectedCategory.name)

        summary += '\n**REGISTER COMMAND**\n*Roles that can set up other users:*\n'
        for r in registerCommandRoleSelection:
            if r['selected']:
                summary += '× {}\n'.format(r['role'].name)
        summary += '\n'

        summary += '**PRIVATE CHANNEL PERMS**\n*Roles that can set up other users:*\n'
        for r in privateChannelRoleSelection:
            if r['selected']:
                summary += '× {}\n'.format(r['role'].name)

        summary += '\n**To accept these settings, select** {}\n**To cancel setup, select** {}\n'.format('✅', '❌')



        embed = discord.Embed(title=title, description=explanation+summary, color=1234123)
        embed.set_footer(text=footerText+' |    step 8/8')
        await msg.clear_reactions()
        await msg.edit(embed=embed)
        await msg.add_reaction(emoji='✅')
        await msg.add_reaction(emoji='❌')

        settingsAccepted = False
        while True:
        
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

            # if user reacts with 'NEXT', move to next interface
            if reaction.emoji == '✅':
                db.saveSettings(
                    ctx.guild.id,
                    allianceAcronym,
                    allowManualRegister,
                    allowPrivateChannelCreation,
                    selectedCategory.name, 
                    memberRole.name,
                    ambassadorRole.name,
                    registerCommandRoleSelection,
                    privateChannelRoleSelection
                )

                explanation = '**SETUP COMPLETE**\n\n To review your settings, you can use the command **.settings**. '
                explanation += 'If at any time you wish to reset the current settings, run **.setup <alliance acronym>** '
                explanation += 'to do so.\n\n [DESTROYING] Interface...\n[ENCRYPTING] sensitive data...\n\nshutting down... ... ...'

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation, color=1234123)
                embed.set_footer(text=footerText+' |    COMPLETE')
                await msg.clear_reactions()
                await msg.edit(embed=embed)

                # FINALLY, exit
                return

            elif reaction.emoji == '❌':
                
                explanation = '**SETUP CANCELLED**\n\n[DESTROYING] Interface...\n[ENCRYPTING] sensitive data...\n\nshutting down... ... ...'

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation, color=1234123)
                embed.set_footer(text=footerText+' |    CANCELLED')
                await msg.clear_reactions()
                await msg.edit(embed=embed) 

                # FINALLY, exit
                return   

            else:
                msg.remove_reaction(emoji=reaction.emoji, member=user)



# set the cog up
def setup(bot):
    bot.add_cog(SetupCog(bot))
