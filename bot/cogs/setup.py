import discord
from discord.ext import commands
import sys, asyncio
from bot.utils.functions import getSelectedRoles, determineFirstTimeSetup, getSettings, getSetupSummary
from bot.utils.test_functions import setAllSetup
from bot.utils.data_database import saveSettings
from bot.utils.constants import ORDERED_REACTIONS, IN_MESSAGE_REACTIONS, GITHUB



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
        footerText = '*DATA Bot Setup: {}, Created by Bop*'.format(GITHUB)

        # settings variables.
        allianceAcronym              = args[0].upper()   # The acronym for the alliance on this server                 
        roles                        = []                # the roles on this server
        memberRoles                  = []                # container for role selection for members
        allyRoles                    = []                # container for role selection for ally ambassadors
        ambassadorRoles              = []                # container for role selection for ambassadors
        registerCommandRoleSelection = []                # container for role selection to use register admin command
        privateChannelRoleSelection  = []                # container for role selection to to have perms. to view private chnl
        allowManualRegister          = False             # allow manual version of register command on this server
        allowPrivateChannelCreation  = False             # allow bot to create private channel for ambassadors
        selectedCategory             = None              # the category to place newly created channels in
        test = False
        newSetup = True

            
        # setup some data, get server roles, and set roleSelection variables to false by default
        for r in ctx.guild.roles:
            if r.name != 'DATA':
                roles.append(r)
                memberRoles.append({'role': r, 'selected': False})
                ambassadorRoles.append({'role': r, 'selected': False})
                allyRoles.append({'role': r, 'selected': False})
                registerCommandRoleSelection.append({'role': r, 'selected': False})
                privateChannelRoleSelection.append({'role': r, 'selected': False})


        # the following 2 functions are used 
        # to check user reaction responses
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == self.next

        def checkUser(reaction, user):
                return user == ctx.message.author


        # BEFORE RUNNING SETUP, we check to see if this server has already
        # registered another alliance. If so, we will offer them the chance
        # to copy those settings and apply them to the new alliance
        existingAllianceID = determineFirstTimeSetup(ctx.guild.id, allianceAcronym)
        if existingAllianceID != None:
            # post explanation to interface to explain how to use this screen
            explanation = 'Initiate setup mode...\n\n'
            explanation += '**Alliance Established: {}**... ...\n\n'.format(allianceAcronym)
            explanation += '**[EXIST**ING AL**LIANCE** DET**ECT**ED]... ...\n\n'
            explanation += 'It appears you have registered a different alliance on this server before. '
            explanation += 'If you desire, we can apply the settings given for {} to this alliance. '.format(existingAllianceID)
            explanation += 'If not, we will run setup for this alliance\n\n **NOTE** By sharing settings, the '
            explanation += '**register** command with the {} or {} parameter will give out rules and permissions '.format(existingAllianceID, allianceAcronym)
            explanation += 'the same exact way.\n\n'

            desc = '**Select 👍 below to share settings with {}**\n'.format(existingAllianceID)
            desc += '**Select 👎 to set up manually**\n\n'

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    EXISTING SETTINGS')
            msg = await ctx.channel.send(embed=embed)
            await msg.add_reaction(emoji='👍')
            await msg.add_reaction(emoji='👎')

            while True:
                #wait for user to react
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

                #Interpret response
                if reaction.emoji == '👍':
                    newSetup = False
                    break
                elif reaction.emoji == '👎':
                    break
                else:
                    msg.remove_reaction(emoji=reaction.emoji, member=user)



        # for testing purposes, does an auto setup of all roles
        if test:
            allowManualRegister = True
            allowPrivateChannelCreation = True
            selectedCategory =  setAllSetup(memberRoles, ambassadorRoles, allyRoles, registerCommandRoleSelection, privateChannelRoleSelection, ctx.guild.categories)

        # If user opted to copy the settings from their other servers alliance settings,
        # simply ask them to confirm the settings, and save to database or cancel.
        if not newSetup:
            settings = getSettings(ctx.guild.id, existingAllianceID.upper(), ctx.guild.roles, ctx.guild.categories)             
            summary = getSetupSummary(
                'Summary of Setup',
                ctx.guild.id,
                ctx.guild.name,
                allianceAcronym.upper(),
                settings["manualRegister"],
                settings["createChannel"],
                settings["channelCategory"],
                settings["memberRoles"],
                settings["ambassadorRoles"],
                settings["allyRoles"], 
                settings["canRegisterUserRoles"],
                settings["canAccessPrivateChannelRoles"]
            )
            summary += '\n**To accept these settings, select** {}\n**To cancel setup, select** {}\n'.format('✅', '❌')

            embed = discord.Embed(title=title, description=summary, color=1234123)
            embed.set_footer(text=footerText)
            msg = await ctx.send(embed=embed)
            await msg.add_reaction(emoji='✅')
            await msg.add_reaction(emoji='❌')

            while True:
        
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)
                
                # if user reacts with 'NEXT', move to next interface
                if reaction.emoji == '✅':
                    saveSettings(
                        ctx.guild.id,
                        ctx.guild.name,
                        allianceAcronym.upper(),
                        settings["manualRegister"],
                        settings["createChannel"],
                        settings["channelCategory"],
                        settings["memberRoles"],
                        settings["ambassadorRoles"],
                        settings["allyRoles"], 
                        settings["canRegisterUserRoles"],
                        settings["canAccessPrivateChannelRoles"]
                    )

                    explanation = '**SETUP COMPLETE**\n\n To review your settings, you can use the command **.settings**. '
                    explanation += 'If at any time you wish to reset the current settings, run **.setup <alliance acronym>** '
                    explanation += 'to do so.\n\n [DESTROYING] Interface...\n[ENCRYPTING] sensitive data...\n\nshutting down... ... ...'

                    # prepare embed interface for post
                    embed = discord.Embed(title=title, description=explanation, color=1234123)
                    embed.set_footer(text=footerText+' |    COMPLETE')
                    await msg.clear_reactions()
                    await msg.edit(embed=embed)
                    return

                elif reaction.emoji == '❌':
                    explanation = '**SETUP CANCELLED**\n\n[DESTROYING] Interface...\n[ENCRYPTING] sensitive data...\n\nshutting down... ... ...'

                    # prepare embed interface for post
                    embed = discord.Embed(title=title, description=explanation, color=1234123)
                    embed.set_footer(text=footerText+' |    CANCELLED')
                    await msg.clear_reactions()
                    await msg.edit(embed=embed) 
                    return   
                else:
                    msg.remove_reaction(emoji=reaction.emoji, member=user)




        ### BEGIN INTERFACE SETUP MODE ###
        #Begin dialog with introduction screen
        desc = 'Initiate setup mode...\n\n'
        desc += '**Alliance Established: {}**... ...\n\n'.format(allianceAcronym)
        desc += 'Hello.\n\nThrough this interface, I shall guide you through setup. '
        desc += 'It is reccommended that you complete the setup entirely. **If you take to long to respond, '
        desc += 'this interface will be destroyed, and you will have to run the setup command again.**\n\n'
        desc += 'All interactions should be through **selecting the attached symbols** at the bottom of the '
        desc += 'interface.\n\n **Note** all changes are not saved until the very end\n\n'
        desc += '**WARNING** Much of my register functionality involves changing user nicknames, and adding '
        desc += 'user roles. In order for my functionality to work, the Role **DATA** must be given **Admin '
        desc += 'permissions**. In addition, be sure that the role **DATA** supercedes any roles for which I '
        desc += 'am expected to interact with in the role hierarchy in **server settings**\n\n.'
        desc += '**Please select the :arrow_right: symbol to continue...**'
        embed = discord.Embed(title=title, description=desc, color=1234123)
        embed.set_footer(text=footerText)
        msg = await ctx.channel.send(embed=embed)
        
        # Add reaction for user to move to next screen
        await msg.add_reaction(self.next)
        
        # Wait for user response, make sure the reaction is the 'NEXT' reaction and from user
        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)



        if not test:

            # STEP 1: Determine new member role
            # determine wwhat role to assign new members on arrival

            # post explanation to interface to explain how to use this screen
            explanation = '**New Member Role**\n\n In order to setup alliance members, I need to know which '
            explanation += 'role(s) will be auto-assigned when using the register command with the argument '
            explanation += '**member**\n\n**Please select the corresponding symbols which represent '
            explanation += 'which role(s) should be granted to members.**\n\n'
            
            
            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 1/9')
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
                memberRoles, desc = getSelectedRoles(roles, reaction, memberRoles)

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 1/9')
                await msg.clear_reactions()
                await msg.edit(embed=embed)

                # add reactions corresponding to each role in list above.
                for i in range(len(roles)):
                    await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

                # add 'next' emoji once there is at least one selected role
                if len(registerCommandRoleSelection) > 0:
                    await msg.add_reaction(self.next)



            # STEP 2: Determine new ambassador role
            # determine what role to assign new ambassadors on arrival

            # post explanation to interface to explain how to use this screen
            explanation = '**New Ambassador Role**\n\n In order to setup non alliance members, I need to know which '
            explanation += 'These roles will be auto-assigned when using the register command with the argument '
            explanation += '**ambassador**\n\n**Please select the corresponding '
            explanation += 'symbols which represent which roles should be granted to ambassadors.**\n\n'
            
            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 2/9')
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
                ambassadorRoles, desc = getSelectedRoles(roles, reaction, ambassadorRoles)

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 2/9')
                await msg.clear_reactions()
                await msg.edit(embed=embed)

                # add reactions corresponding to each role in list above.
                for i in range(len(roles)):
                    await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

                # add 'next' emoji once there is at least one selected role
                if len(ambassadorRoles) > 0:
                    await msg.add_reaction(self.next)






            # STEP 3: Determine new allied ambassador role
            # determine wwhat role to assign new allied ambassadors on arrival

            # post explanation to interface to explain how to use this screen
            explanation = '**Ally Ambassador Role**\n\n Perhaps on your server you like to differentiate '
            explanation += 'between Allied Ambassadors and Non-AlliedAmbassadors. If so, this section will allow '
            explanation += 'to specify which roles to assign allied ambassadors. These roles will be auto-assigned '
            explanation += 'when using the register command with the argument **ally**\n\n. **Please select the '
            explanation += 'corresponding symbols which represent which roles should be granted to allied ambassadors.**\n\n'
            desc = '**select ❌ to not differentiate between Allied and Non-Allied Ambassadors**\n\n'
            
            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 3/9')
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            # add reactions corresponding to each role in list above.
            for i in range(len(roles)):
                await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
            await msg.add_reaction(emoji='❌')
            
            # interpret user interactions. Keep accepting responses until break logic
            while True:
                
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)

                if reaction.emoji == '❌':
                    allyRoles = ambassadorRoles
                    break

                # if user reacts with 'NEXT', move to next interface
                if reaction.emoji == self.next:
                    break

                # need to figure out which role the users reaction corresponds with
                # this will either select or deselect a role depending on role selection state
                allyRoles, desc = getSelectedRoles(roles, reaction, allyRoles)

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 3/9')
                await msg.clear_reactions()
                await msg.edit(embed=embed)

                # add reactions corresponding to each role in list above.
                for i in range(len(roles)):
                    await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

                # add 'next' emoji once there is at least one selected role
                if len(ambassadorRoles) > 0:
                    await msg.add_reaction(self.next)



            # STEP 4
            # Select roles that can use admin version of register

            # post explanation to interface to explain how to use this screen
            explanation = '**Command register**\n\nThe register command allows one to setup a new user to your server. '
            explanation += 'Please select the corresponding symbols which represent which roles you want to allow to use '
            explanation += 'this command.\n\n'

            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 4/9')
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
                registerCommandRoleSelection, desc = getSelectedRoles(roles, reaction, registerCommandRoleSelection)

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 4/9')
                await msg.clear_reactions()
                await msg.edit(embed=embed)

                # add reactions corresponding to each role in list above.
                for i in range(len(roles)):
                    await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

                # add 'next' emoji once there is at least one selected role
                if len(registerCommandRoleSelection) > 0:
                    await msg.add_reaction(self.next)



            # STEP 5
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
            embed.set_footer(text=footerText+' |    step 5/9')
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



            # STEP 6
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
            embed.set_footer(text=footerText+' |    step 6/9')
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



            # STEP 7: if step 3 was thumbs up
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
                embed.set_footer(text=footerText+' |    step 7/9')
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
                    privateChannelRoleSelection, desc = getSelectedRoles(roles, reaction, privateChannelRoleSelection)
                    
                    # prepare embed interface for post
                    embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                    embed.set_footer(text=footerText+' |    step 7/9')
                    await msg.clear_reactions()
                    await msg.edit(embed=embed)
                    for i in range(len(roles)):
                        await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

                    # add 'next' emoji once there is at least one selected role
                    if len(privateChannelRoleSelection) > 0:
                        await msg.add_reaction(self.next)



                # STEP 8: if step 3 was thumbs up
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
                embed.set_footer(text=footerText+' |    step 8/9')
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



        # STEP 9
        # Summarize user settings

        summary = getSetupSummary('Summary of Setup', ctx.guild.id, ctx.guild.name, allianceAcronym, allowManualRegister, allowPrivateChannelCreation, selectedCategory,
                                   memberRoles, ambassadorRoles, allyRoles, registerCommandRoleSelection, privateChannelRoleSelection)
        summary += '\n**To accept these settings, select** {}\n**To cancel setup, select** {}\n'.format('✅', '❌')
        embed = discord.Embed(title=title, description=summary, color=1234123)
        embed.set_footer(text=footerText+' |    step 9/9')
        await msg.clear_reactions()
        await msg.edit(embed=embed)
        await msg.add_reaction(emoji='✅')
        await msg.add_reaction(emoji='❌')

        while True:
        
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkUser)
            
            # if user reacts with 'NEXT', move to next interface
            if reaction.emoji == '✅':
                saveSettings(
                    ctx.guild.id,
                    ctx.guild.name,
                    allianceAcronym,
                    allowManualRegister,
                    allowPrivateChannelCreation,
                    selectedCategory.name, 
                    memberRoles,
                    ambassadorRoles,
                    allyRoles,
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
