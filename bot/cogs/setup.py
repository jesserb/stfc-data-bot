import discord
from discord.ext import commands
import sys, asyncio
from utils.functions import (
    getSelectedRoles,
    determineFirstTimeSetup,
    getSettings,
    getSetupSummary,
    hasAdminPermission,
    getAllianceIds,
    getRoeRules,
    getNapInfo,
    getAlliesInfo,
    getHomeInfo,
    getKosInfo,
    getWarInfo,
    getMasterAllianceId
)
from utils.test_functions import setAllSetup
from utils.db import saveSettings, saveGeneralInfo, saveAlliance, setNewMaster
from utils.constants import ORDERED_REACTIONS, IN_MESSAGE_REACTIONS, GITHUB



class SetupCog:
    
    def __init__(self, bot):
        self.bot = bot
        self.next = '\N{BLACK RIGHTWARDS ARROW}'
    


    @commands.command()
    async def set(self, ctx, *args):

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

        if len(args) == 3 and args[0].lower() == 'new' and args[1].lower() == 'master' and len(args[3]) < 5:
            title = 'DATA Bot Setup'
            footerText = '*DATA Bot Setup: {}, Created by Bop*'.format(GITHUB)
            # post explanation to interface to explain how to use this screen
            explanation = '**You are requesting to change the master alliance ID to {}.**\n\n'.format(args[3].upper())
            explanation += '***NOTE:*** This will result in any sub alliances for this server being deleted.\n\n'


            desc = '**Select 👍 below to confirm {} as new Master**\n\n'.format(args[3].upper())
            desc += '**Select 👎 to cancel request forr {}**\n\n'.format(args[3].upper())

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    EXISTING SETTINGS')
            msg = await ctx.channel.send(embed=embed)
            await msg.add_reaction(emoji='👍')
            await msg.add_reaction(emoji='👎')

            try:
                while True:
                    #wait for user to react
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

                    #Interpret response
                    if reaction.emoji == '👍':
                        setNewMaster(ctx.guild.id, args[3].upper())
                        explanation = '**SREQUEST COMPLETE**\n\n**{}** Has been set as this servers Master Alliance.'.format(args[3].upper())
                        # prepare embed interface for post
                        embed = discord.Embed(title=title, description=explanation, color=1234123)
                        embed.set_footer(text=footerText+' |    COMPLETE')
                        await msg.clear_reactions()
                        await msg.edit(embed=embed)
                        return

                    elif reaction.emoji == '👎':
                        explanation = '**REQUEST CANCELLED**\n\n[DESTROYING] Interface...\n[ENCRYPTING] sensitive data...\n\nshutting down... ... ...'
                        # prepare embed interface for post
                        embed = discord.Embed(title=title, description=explanation, color=1234123)
                        embed.set_footer(text=footerText+' |    CANCELLED')
                        await msg.clear_reactions()
                        await msg.edit(embed=embed) 
                        return   
                    else:
                        msg.remove_reaction(emoji=reaction.emoji, member=user)
    
            except asyncio.TimeoutError:
                error = '**[ERROR] - Cannot keep line secure**\n\n You took too long to respond... '
                error += 'Information NOT Saved...\n**Please try again**'
                embed = discord.Embed(title=title, description=error, color=1234123)
                embed.set_footer(text='TRANSMISSION CLOSED | PLEASE TRY AGAIN')
                await msg.edit(embed=embed)
                return



        # ERROR CHECKING
        if not len(args) or not (args[0].lower() == 'ally' or args[0].lower() == 'nap' or args[0].lower() == 'kos' or args[0].lower() == 'war' or args[0].lower() == 'roe' or args[0].lower() == 'home'):
            msg = '{}, this argument must contain an argument of either **ally**, **nap**, **ROE**, or **home**'.format(ctx.message.author.mention)
            await ctx.send(msg)
            return

        #variables
        serverId   = ctx.guild.id
        allianceId = getMasterAllianceId(serverId)
        isAdmin    = hasAdminPermission(serverId, ctx.message.author.roles)
        if ctx.message.author.guild_permissions.administrator:
            isAdmin = True
        user       = ctx.message.author
        infoDict = {
            "roe": getRoeRules(serverId),
            "ally": getAlliesInfo(serverId),
            "nap": getNapInfo(serverId),
            "kos": getKosInfo(serverId),
            "war": getWarInfo(serverId),
            "home": getHomeInfo(serverId)
        }
        dm = ''
        
        # ERROR CHECKING
        if not isAdmin:
            msg = '{}, you do not have permission to use this command'.format(ctx.message.author.mention)
            await ctx.send(msg)
            return

        def checkUser(message):
            return (message.author == ctx.message.author) and dm and (dm.channel.id == message.channel.id)


        # SETTINGS THE ALY DESCRIPTION
        msg = '{}, I sent you a private message. Speak with me there to set your **{} Info**'.format(user.mention, args[0].title())
        await ctx.send(msg)

        msg = ''
        if args[0] == 'roe':
            msg += 'Hello {}.\n Please write out a brief discription of the ROE guidelines.'.format(user.mention)
        if args[0] == 'ally':
            msg += 'Hello {}.\n Please write out a brief discription of how your alliance is to treat allies.'.format(user.mention)
        if args[0] == 'nap':
            msg += 'Hello {}.\n Please write out a brief discription of how your alliance is to treat alliances in an NAP agreement'.format(user.mention)
        if args[0] == 'home':
            msg += 'Hello {}.\n Please write out a brief discription, describing your home system, and anything your members should know about it.'.format(user.mention)
        if args[0] == 'kos':
            msg += 'Hello {}.\n Please write out a brief discription, describing how your alliance is to treat KOS Alliances.'.format(user.mention)
        if args[0] == 'war':
            msg += 'Hello {}.\n Please write out a brief discription, describing how your alliance is to treat waring alliances.'.format(user.mention)
        dm = await user.send(msg)

        try:
            newContent = await self.bot.wait_for('message', timeout=320, check=checkUser)
            msg = 'Thank you for that description {}.\nBelow is a copy of your writings. please confirm to commit it\n\n'.format(user.mention)
            msg += '---------------------------------------------------\n'
            msg += '{}\n'.format(newContent.content)
            msg += '---------------------------------------------------\n\n Respond now with **confirm** to commit the above\n'
            msg += 'Respond now with **cancel** to cancel this transmission'
            await user.send(msg)
            ans = await self.bot.wait_for('message', timeout=320, check=checkUser)
            if ans.content.lower() == 'confirm':
                infoDict[args[0].lower()] = newContent.content
                msg = '**Committing description... ...**\n.'
                await user.send(msg)
                saveGeneralInfo(serverId, allianceId, infoDict["roe"], infoDict["ally"], infoDict["nap"], infoDict["kos"], infoDict["war"], infoDict["home"])
                msg = '*The information has been saved, and will now show in the * **intel** *command*\n**closing connection... ...**\n.'
                await user.send(msg)
            else:
                msg = '**Cancelling transmission. The above was not saved... ...**\n.'
                await user.send(msg)
        # TIME RAN OUT        
        except asyncio.TimeoutError:
            msg = '**[EXCEEDED TIME LIMIT] I cannot maintain a secure line of communication...**\n '
            msg += 'Closing this channel. Information was not saved... **Please try again** ... **goodbye**\n[CLOSED]\n'
            await user.send(msg)    






    @commands.command()
    async def setup(self, ctx, *args):


        #ERROR CHECK - dm bot commands not allowed
        try:
            ctx.guild.id # if no guild id then this is a dm
        except:
            error = "**You cannot run bot commands in a DM** "
            error += "Please retry your command in a bot friendly channel in your server where I reside."
            await ctx.message.author.send('{}'.format(error))
            return
        
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
        allowAllyIntelAccess = False

            
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
        # registered another alliance. 
        existingAllianceID = determineFirstTimeSetup(ctx.guild.id, allianceAcronym)
        if existingAllianceID != None:
            # post explanation to interface to explain how to use this screen
            explanation = 'Initiate setup mode...\n\n'
            explanation += '**Alliance Established: {}**... ...\n\n'.format(allianceAcronym)
            explanation += '**[EXIST**ING AL**LIANCE** DET**ECT**ED]... ...\n\n'
            explanation += 'It appears you have registered a master alliance on this server before, '
            explanation += 'and therefore {} will be added as a sub alliance to {}.\n\n'.format(allianceAcronym, existingAllianceID)

            explanation += 'If {} is to be the new master alliance for this server, first run '.format(allianceAcronym)
            explanation += '**.set new master {}**. *note* this command will preserve settings and intel but delete '.format(allianceAcronym)
            explanation += 'all sub alliances associated with this server.\n\n'


            desc = '**Select 👍 below to confirm {} as sub alliance**\n\n'.format(allianceAcronym)
            desc += '**Select 👎 to cancel setup for {}**\n\n'.format(allianceAcronym)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    EXISTING SETTINGS')
            msg = await ctx.channel.send(embed=embed)
            await msg.add_reaction(emoji='👍')
            await msg.add_reaction(emoji='👎')

            try:
                while True:
                    #wait for user to react
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

                    #Interpret response
                    if reaction.emoji == '👍':
                        saveAlliance(ctx.guild.id, allianceAcronym, isMaster=0)
                        explanation = '**SETUP COMPLETE**\n\n To review your settings, you can use the command **.settings**. '
                        explanation += 'If at any time you wish to reset the current settings, run **.setup <alliance acronym>** '
                        explanation += 'to do so.\n\n [DESTROYING] Interface...\n[ENCRYPTING] sensitive data...\n\nshutting down... ... ...'
                        # prepare embed interface for post
                        embed = discord.Embed(title=title, description=explanation, color=1234123)
                        embed.set_footer(text=footerText+' |    COMPLETE')
                        await msg.clear_reactions()
                        await msg.edit(embed=embed)
                        return

                    elif reaction.emoji == '👎':
                        explanation = '**SETUP CANCELLED**\n\n[DESTROYING] Interface...\n[ENCRYPTING] sensitive data...\n\nshutting down... ... ...'
                        # prepare embed interface for post
                        embed = discord.Embed(title=title, description=explanation, color=1234123)
                        embed.set_footer(text=footerText+' |    CANCELLED')
                        await msg.clear_reactions()
                        await msg.edit(embed=embed) 
                        return   
                    else:
                        msg.remove_reaction(emoji=reaction.emoji, member=user)
    
            # TIME RAN OUT        
            except asyncio.TimeoutError:
                error = '**[ERROR] - Cannot keep line secure**\n\n You took too long to respond... '
                error += 'Information NOT Saved...\n**Please try again**'
                embed = discord.Embed(title=title, description=error, color=1234123)
                embed.set_footer(text='TRANSMISSION CLOSED | PLEASE TRY AGAIN')
                msg = await ctx.channel.send(embed=embed)


        try:
            ### BEGIN INTERFACE SETUP MODE ###
            #Begin dialog with introduction screen
            desc = 'Initiate setup mode...\n\n'
            desc += '**Alliance Established: {}**... ...\n\n'.format(allianceAcronym)
            desc += 'Hello.\n\nThrough this interface, I shall guide you through setup. '
            desc += 'It is reccommended that you complete the setup entirely. **If you take to long to respond, '
            desc += 'this interface will be destroyed, and you will have to run the setup command again.**\n\n'
            desc += 'All interactions should be through **selecting the attached symbols** at the bottom of the '
            desc += 'interface.\n\n **Note** all changes are not saved until the very end\n\n'
            desc += '**WARNING** Much of my higher level functionality involves changing user nicknames, and adding '
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
            reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=check)




            # STEP 1: Determine new member role
            # determine wwhat role to assign new members on arrival

            # post explanation to interface to explain how to use this screen
            explanation = '**New Member Role**\n\n Please select which roles represent your regular Alliance '
            explanation += 'members. The role(s) you select below will be auto-assigned to users when using the register  '
            explanation += 'command with the argument **member**\n\n**Please select the corresponding symbols which represent '
            explanation += 'which role(s) should be granted to members.**\n\n'
            
            
            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 1/10')
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            # add reactions corresponding to each role in list above.
            for i in range(len(roles)):
                await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
            
            # interpret user interactions. Keep accepting responses until break logic
            while True:
            
                reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

                # if user reacts with 'NEXT', move to next interface
                if reaction.emoji == self.next:
                    break

                # need to figure out which role the users reaction corresponds with
                # this will either select or deselect a role depending on role selection state
                memberRoles, desc = getSelectedRoles(roles, reaction, memberRoles)

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 1/10')
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
            explanation += 'role(s) *(if any)* will be auto-assigned when using the register command with the '
            explanation += 'argument **ambassador**\n\n**Please select the corresponding symbols '
            explanation += 'which represent which roles should be granted to ambassadors. You can select ❌ '
            explanation += ', which means I will not assign a role when the argument "ambassador" is given.**\n\n'
            
            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 2/10')
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            # add reactions corresponding to each role in list above.
            for i in range(len(roles)):
                await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
            await msg.add_reaction(emoji='❌')
            
            # interpret user interactions. Keep accepting responses until break logic
            while True:
                
                reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

                # Do not auto-assign ambassador roles
                if reaction.emoji == '❌':
                    break

                # if user reacts with 'NEXT', move to next interface
                if reaction.emoji == self.next:
                    break

                # need to figure out which role the users reaction corresponds with
                # this will either select or deselect a role depending on role selection state
                ambassadorRoles, desc = getSelectedRoles(roles, reaction, ambassadorRoles)

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 2/10')
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
            explanation += 'between Allied Ambassadors and Non-Allied Ambassadors. If so, this section will allow you '
            explanation += 'to specify which roles to assign allied ambassadors. These roles will be auto-assigned '
            explanation += 'when using the register command with the argument **ally**\n\n. **Please select the '
            explanation += 'corresponding symbols which represent which roles should be granted to allied ambassadors.**\n\n'
            explanation += '**select ❌ to not differentiate between Allied and Non-Allied Ambassadors**\n\n'
            
            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 3/10')
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            # add reactions corresponding to each role in list above.
            for i in range(len(roles)):
                await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
            await msg.add_reaction(emoji='❌')
            
            # interpret user interactions. Keep accepting responses until break logic
            while True:
                
                reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

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
                embed.set_footer(text=footerText+' |    step 3/10')
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
            explanation = '**Admin Roles**\n\nMuch of my functionality is sensitive, such as my ability to add roles with the '
            explanation += 'command **.register**, or add ROE violations with the command **.intel**. Therefore, I will need to know '
            explanation += 'which roles will be allowed to use my more "sensitive" functionality...\n\n'
            explanation += '**Please select the corresponding symbols which represent which roles will be allowed to register other '
            explanation += 'users, add ROE violations, add other Alliance intelligence such as Allies, NAPs, war decrees, etc..**\n\n'

            # set up a list of roles on this server
            desc = ''
            for i in range(len(roles)):
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 4/10')
            await msg.clear_reactions()
            await msg.edit(embed=embed)

            # add reactions corresponding to each role in list above.
            for i in range(len(roles)):
                await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
            
            # interpret user interactions. Keep accepting responses until break logic
            while True:
            
                reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

                # if user reacts with 'NEXT', move to next interface
                if reaction.emoji == self.next:
                    break

                # need to figure out which role the users reaction corresponds with
                # this will either select or deselect a role depending on role selection state
                registerCommandRoleSelection, desc = getSelectedRoles(roles, reaction, registerCommandRoleSelection)

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 4/10')
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
            embed.set_footer(text=footerText+' |    step 5/10')
            await msg.clear_reactions()
            await msg.edit(embed=embed)
            await msg.add_reaction(emoji='👍')
            await msg.add_reaction(emoji='👎')

            while True:
                #wait for user to react
                reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

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
            explanation += 'channel between members of said alliance and your alliance. These channels are useful for private '
            explanation += 'conversations between the leaders of both alliances, in order to settle feuds or work out treaties.\n\n'
            explanation += '**New ambassadors for a previously created private channel will simply be given permission to access '
            explanation += 'the already established private alliance channel. Additionally, if you choose this feature, on '
            explanation += 'next screen we will determine which roles on your server should have access to this new channel.**\n\n'
            desc = '**Would you like me to create a private channel between your alliance leaders and new alliance ambassadors '
            desc += 'after user setup?**'

            # prepare embed interface for post
            embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
            embed.set_footer(text=footerText+' |    step 6/10')
            await msg.clear_reactions()
            await msg.edit(embed=embed)
            await msg.add_reaction(emoji='👍')
            await msg.add_reaction(emoji='👎')

            while True:
                #wait for user to react
                reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)
                
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
                embed.set_footer(text=footerText+' |    step 7/10')
                await msg.clear_reactions()
                await msg.edit(embed=embed)

                # add reactions corresponding to each role in list above.
                for i in range(len(roles)):
                    await msg.add_reaction(emoji=ORDERED_REACTIONS[i])

                # interpret user interactions. Keep accepting responses until break logic
                while True:
                
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

                    # if user reacts with 'NEXT', move to next interface
                    if reaction.emoji == self.next:
                        break

                    # need to figure out which role the users reaction corresponds with
                    # this will either select or deselect a role depending on role selection state
                    privateChannelRoleSelection, desc = getSelectedRoles(roles, reaction, privateChannelRoleSelection)
                    
                    # prepare embed interface for post
                    embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                    embed.set_footer(text=footerText+' |    step 7/10')
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
                embed.set_footer(text=footerText+' |    step 8/10')
                await msg.clear_reactions()
                await msg.edit(embed=embed)

                # add reactions corresponding to each category on the server.
                for i in range(len(categories)):
                    await msg.add_reaction(emoji=ORDERED_REACTIONS[i])
                
                # this step is optional, so add next reaction for them to skip
                await msg.add_reaction(self.next)

                while True:
                
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)

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


            # step 9
            # if user picke allies roles, check if they should get access to alliance intel commands
            if allyRoles:

                # post explanation to interface to explain how to use this screen
                explanation = '**Command Intel** *ally intel access*\n\nWe detect you have set up ally roles. Do you wish to give '
                explanation += 'Allies access to your Alliance intel? This can be useful in sharing targets & information.**\n\n'
                desc = '**Give the thumbs up to share intel with allies. Otherwise, give the thumbs down**\n\n'

                # prepare embed interface for post
                embed = discord.Embed(title=title, description=explanation+desc, color=1234123)
                embed.set_footer(text=footerText+' |    step 9/10')
                await msg.clear_reactions()
                await msg.edit(embed=embed)
                await msg.add_reaction(emoji='👍')
                await msg.add_reaction(emoji='👎')

                while True:
                    #wait for user to react
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)
                    
                    #Interpret response
                    if reaction.emoji == '👍':
                        allowAllyIntelAccess = True
                        break
                    elif reaction.emoji == '👎':
                        break
                    else:
                        msg.remove_reaction(emoji=reaction.emoji, member=user)


            # STEP 9
            # Summarize user settings

            summary = getSetupSummary('Summary of Setup', ctx.guild.id, ctx.guild.name, allianceAcronym, allowManualRegister, allowPrivateChannelCreation, allowAllyIntelAccess,
                                    selectedCategory, memberRoles, ambassadorRoles, allyRoles, registerCommandRoleSelection, privateChannelRoleSelection)
            summary += '\n**To accept these settings, select** {}\n**To cancel setup, select** {}\n'.format('✅', '❌')
            embed = discord.Embed(title=title, description=summary, color=1234123)
            embed.set_footer(text=footerText+' |    step 10/10')
            await msg.clear_reactions()
            await msg.edit(embed=embed)
            await msg.add_reaction(emoji='✅')
            await msg.add_reaction(emoji='❌')

            while True:
            
                reaction, user = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkUser)
                
                # if user reacts with 'NEXT', move to next interface
                if reaction.emoji == '✅':
                    saveSettings(
                        ctx.guild.id,
                        ctx.guild.name,
                        allianceAcronym,
                        allowManualRegister,
                        allowPrivateChannelCreation,
                        selectedCategory.name if selectedCategory else '', 
                        memberRoles,
                        ambassadorRoles,
                        allyRoles,
                        registerCommandRoleSelection,
                        privateChannelRoleSelection,
                        allowAllyIntelAccess
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
    
        # TIME RAN OUT        
        except asyncio.TimeoutError:
            error = '**[ERROR] - Cannot keep line secure**\n\n You took too long to respond... '
            error += 'Information NOT Saved...\n**Please try again**'
            embed = discord.Embed(title=title, description=error, color=1234123)
            embed.set_footer(text='TRANSMISSION CLOSED | PLEASE TRY AGAIN')
            msg = await ctx.channel.send(embed=embed) 




# set the cog up
def setup(bot):
    bot.add_cog(SetupCog(bot))
