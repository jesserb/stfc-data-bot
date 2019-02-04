import discord
from discord.ext import commands
import sys, asyncio
from utils.functions import (
    hasAdminPermission,
    serverRegistered,
    isInAlliance,
    getAllianceIdFromNick,
    getAllianceName,
    getMemberRoles,
    getAllyRoles,
    getAmbassadorRoles,
    getMember,
    getRole,
    isUser,
    getAllianceIds,
    manualRegisterAllowed,
    createChannelAllowed,
    channelExists,
    getAmbassadorCategory,
    getCategory,
    getChannel,
    canAccessPrivateChannel
)





class RegistrationCog:
    
    def __init__(self, bot):
        self.bot = bot


    # THE BREAD AND BUTTER. This command registers a user on a STFC discord server. Depending on
    # the role of the author, an admin or manual version is ran. The command will set a users
    # roles, nickname, and even set up private ambassador alliance channels.

    # PARAMAS
    #  -          member: The user to be registered, either a mention or string version of username. Admin only
    #  -            type: The type of new user, either member, ally, or ambassador
    #  - newUserAlliance: The alliance ID of the new user. 
    @commands.command()
    async def register(self, ctx, member=None, type='', newUserAlliance=''):


        #ERROR CHECK - dm bot commands not allowed
        try:
            test = ctx.guild.id # if no guild id then this is a dm
        except:
            error = "**You cannot run bot commands in a DM** "
            error += "Please retry your command in a bot friendly channel in your server where I reside."
            await ctx.message.author.send('{}'.format(error))
            return
        
        #ERROR CHECKING
        if member == None:
            # if the current user has roles for admin register command, they cannot use
            # command without parameter
            if hasAdminPermission(ctx.guild.id, getAllianceIdFromNick(ctx.message.author.nick), ctx.message.author.roles):
                err =  '{}, **No parameters wih command register.**\n'.format(ctx.message.author.mention)
                err += 'The register command without parameters can only be used by new members. To register '
                err += 'another user, please include the members name, whether they are a member, ally, or ambassador, '
                err += 'and their alliance ID.\nFor example: `.register @Test member ABCD` or `.register @Test ambassador WXYZ`.'
                await ctx.send(err)
                return   


        # if server is not in db, command cannot be run
        if not serverRegistered(ctx.guild.id):
            err =  '{}, **You have not registered your server with me yet.**\n'.format(ctx.message.author.mention)
            err += 'To use this command, a server admin must perform the bot setup. Use the command:'
            err += '```.setup <alliance abbreviation``` to setup your server with me.'
            await ctx.send(err)
            return

        # If member field is not empty and type field is given but not member or ambassador, unrecognized type error
        if member != None and (type.lower() != 'member' and type.lower() != 'ambassador' and type.lower() != 'ally'):
            err =  '{}, **Unrecognized/issing second parameter:** *User type*.\n'.format(ctx.message.author.mention)
            err += 'Second parameter must be "member" "ally" or "ambassador'
            await ctx.send(err)
            return

        # if member, type is given but alliance is missing, or of incorrect format, missing/invalid alliance param
        if member != None and type and (not newUserAlliance or len(newUserAlliance) > 4 or len(newUserAlliance) < 2):
            err =  '{}, **Missing required paramaters:** *alliance identifier*.\n'.format(ctx.message.author.mention)
            err += 'Third argument must contain a 2 to 4 letter Alliance identifier.'
            await ctx.send(err)
            return    

        if member != None and type != None and newUserAlliance != None:

            # type is member, but provided alliance id is not on server settings as member allianc.
            if type.lower() == 'member' and not isInAlliance(ctx.guild.id, newUserAlliance):
                err =  '{}, **Incorrect command:** *type and user alliance*.\n'.format(ctx.message.author.mention)
                err += '{} is not registered as a member alliance for this server. If this alliance '.format(newUserAlliance.upper())
                err += 'should be considered a member alliance, please set it up as so with the command'
                err += '```.setup {}``` Otherwise, use the type "ambassador" or "allie" for this alliance'.format(newUserAlliance.upper())
                await ctx.send(err)
                return

            # type is ambassador or ally, but provided alliance id is on server settings as member alliance.
            if (type.lower() == 'ambassador' or type.lower() == 'ally') and isInAlliance(ctx.guild.id, newUserAlliance):
                err =  '{}, **Incorrect command:** *type and user alliance*.\n'.format(ctx.message.author.mention)
                err += '{} is registered as a member alliance for this server, and therefore '.format(newUserAlliance.upper())
                err += 'cannot be used with the "ambassador" or "ally" argument.'
                await ctx.send(err)
                return


 
        # VARIABLES
        roles              = ctx.guild.roles                    # server roles
        userRoles          = ctx.message.author.roles           # roles of the user: default to message sender
        author             = ctx.message.author                 # the user: default to message sender
        newUser            = None
        allianceId         = getAllianceIdFromNick(author.nick)
        allianceName       = getAllianceName(ctx.guild.id)
        server             = ctx.guild                          # server the command was used on
        memberRoles        = getMemberRoles(server.id, allianceId)
        ambassadorRoles    = getAmbassadorRoles(server.id, allianceId)
        allyRoles          = getAllyRoles(server.id, allianceId)
        ambassadorCategory = getAmbassadorCategory(server.id)
        channel            = ''                                 # placeholder for new channel name

        # permissions for users/roles that can use new channel
        show = discord.PermissionOverwrite(
            read_messages    = True,
            send_messages    = True,
            add_reactions    = True,
            mention_everyone = True,
            attach_files     = True
        )

        # permissions for users/roles that cannot use new channel
        hide = discord.PermissionOverwrite(
            read_messages    = False,
            send_messages    = False,
            add_reactions    = False,
            mention_everyone = False,
            attach_files     = False
        )

        def checkUser(message):
            return message.author == ctx.message.author

        ### STEP ONE ###
        ### Set user role and nickname

        # CASE 1
        # Command is being used by an administrator. 
        if ctx.message.author.guild_permissions.administrator or hasAdminPermission(server.id, allianceId, userRoles):

            # if admin is user command for other user, a user must be provided
            if len(ctx.message.mentions) > 0:
                newUser = ctx.message.mentions[0]
            elif isUser(member, ctx.guild.members):
                newUser = getMember(member, ctx.guild.members)
            else:
                err =  '{}, Member {}. not found. Please  check the name and try again, '.format(ctx.message.author.mention, member)
                err += 'or mention the user instead.'
                await ctx.send(err)
                return

            # ERROR CHECK: Users cannot be registered if they already have roles
            if len(newUser.roles) > 1:
                err =  '{}, This user does not appear to be new to the server: **has existing roles**.'.format(ctx.message.author.mention)
                err += 'Remove users roles first to re-register them'
                await ctx.send(err)
                return

            await newUser.edit(nick='[{}] {}'.format(newUserAlliance.upper(), newUser.name))

            if type.lower() == 'member':
                for role in memberRoles:
                    await newUser.add_roles(getRole(roles, role))

            if type.lower() == 'ambassador':
                for role in ambassadorRoles:
                    await newUser.add_roles(getRole(roles, role))  

            if type.lower() == 'ally':
                for role in allyRoles:
                    await newUser.add_roles(getRole(roles, role))           

        # CASE 2
        # command is being used by a non administrator. User is
        # sent a private message, with guided information on how
        # to register. INTERACTIVE
        else:
            newUser = ctx.message.author

            # ERROR CHECK: Users cannot be registered if they already have roles
            if len(newUser.roles) > 1:
                err =  '{}, You do not appear to be new to the server: **has existing roles**.'.format(ctx.message.author.mention)
                await ctx.send(err)
                return

            if not manualRegisterAllowed(server.id):
                err =  '{}, This server does not allow self registration. Please check with admin.'.format(ctx.message.author.mention)
                await ctx.send(err)
                return


            await ctx.send(newUser.mention+', I sent you a private message. Please respond to me there.')
            msg = '**Welcome to the {} Alliance server. I am here to help you register.**\n\n'.format(allianceName)
            msg += 'To begin, are you a {} member, part of an Ally Alliance, or an ambassador representing another Alliance? '.format(allianceName)
            msg += 'Please respond with either **member**, **ally**, or **ambassador**'
            await ctx.message.author.send(msg)

            try:
                while True:
                    # wait for user response
                    ans = await self.bot.wait_for('message', timeout=120, check=checkUser)

                    # response: member
                    if ans.content.lower() == 'member':

                        # if more than one alliance is saved to database,  need to determine which this new member belongs to
                        ids = getAllianceIds(server.id)
                        if len(ids) > 1:
                            msg = 'Welcome {} Member. Which member alliance are you a part of? Please choose from '.format(allianceName)
                            msg += 'the list below:\n'
                            for id in ids:
                                msg += '**{}**\n'.format(id.upper())
                            await ctx.message.author.send(msg)
                            id = await self.bot.wait_for('message', timeout=120, check=checkUser)

                            # check user response. If response is not an alliance in DB, repeat the Q, and prompt again
                            while True:
                                id = id.content

                                # set the roles, set the nickname, and finish
                                if isInAlliance(server.id, id.upper()):
                                    memberRoles = getMemberRoles(server.id, id)
                                    for role in memberRoles:
                                        await newUser.add_roles(getRole(roles, role)) 
                                    await newUser.edit(nick='[{}] {}'.format(id.upper(), newUser.name))
                                    msg = 'Thank you, **I have set your role and your nickname for this server.** You are now all set!'
                                    await ctx.message.author.send(msg)
                                    return

                                else:
                                    msg = '**{}** not recognized. **Please choose from the following list so we can determine which '.format(id)
                                    msg += 'alliance you belong to.**\n'
                                    for id in ids:
                                        msg += '**{}**\n'.format(id.upper())
                                    await ctx.message.author.send(msg)
                        
                        # case when only one alliance is in DB for this server
                        else:
                            # set user role based on DB alliance member role, and set nickname to include alliance abreviation
                            for role in memberRoles:
                                await newUser.add_roles(getRole(roles, role)) 
                            await newUser.edit(nick='[{}] {}'.format(allianceId, newUser.name))
                            msg = 'Thank you, **I have set your role and your nickname for this server.** You are now all set!'
                            await ctx.message.author.send(msg)
                            return

                    # response: ambassador or ally 
                    elif ans.content.lower() == 'ambassador' or  ans.content.lower() == 'ally':

                        # get values for alliance Id, ambassador and ally roles
                        allianceId = getAllianceIds(server.id)[0]
                        ambassadorRoles = getAmbassadorRoles(server.id, allianceId)
                        allyRoles       = getAllyRoles(server.id, allianceId) 

                        # set user role based on DB ambassador role
                        if ans.content.lower() == 'ambassador':
                            for role in ambassadorRoles:
                                await newUser.add_roles(getRole(roles, role))  
                        if ans.content.lower() == 'ally':
                            for role in allyRoles:
                                await newUser.add_roles(getRole(roles, role))  

                        msg = '**Thank you, I have set your role.**\n'
                        msg += 'The last thing I need to know is your Alliance abbreviation. Please respond with only your Alliance abbreviation.\n'
                        msg += '**EXAMPLE RESPONSE:** ABCD'
                        await ctx.message.author.send(msg)

                        while True:
                            # wait for user response
                            ans = await self.bot.wait_for('message', timeout=120, check=checkUser)
                            # set nickname to include their alliance abreviation
                            if len(ans.content) < 5:
                                newUserAlliance = ans.content.upper()
                                await newUser.edit(nick='[{}] {}'.format(newUserAlliance, newUser.name))
                                msg = 'Thank you, **I have set your role and your nickname for this server.**'
                                msg += ' You are now all set!'
                                await ctx.message.author.send(msg)
                                break
                            else:
                                msg = 'I did not understand that response..\n\n'
                                msg += 'The last thing I need to know is your Alliance abbreviation. Please respond with only your Alliance abbreviation.\n'
                                msg += '**EXAMPLE RESPONSE:** ABCD'
                                await ctx.message.author.send(msg)
                        break
                    # response was not member or ambassador. reloop
                    else:
                        msg = 'I did not understand that response..\n\n'
                        msg += 'Are you a {} member, or an ambassador representing another Alliance?'.format(allianceName)
                        msg += ' Please respond with either **member** or **ambassador**'
                        await ctx.message.author.send(msg)

            # TIME RAN OUT              
            except asyncio.TimeoutError:
                msg = '**[EXCEEDED TIME LIMIT] I cannot maintain a secure line of communication...**\n '
                msg += 'Closing this channel. Information was not saved... **Please try again** ... **goodbye**\n[CLOSED]\n'
                await ctx.message.author.send(msg)          




        ### STEP TWO ###
        ### Create private channel for ambassadors

        if not createChannelAllowed(server.id):
            return


        # If user is not an alliance member -> aka an ambassador, we need tp
        # create a new channel for ambassadors and chosen server roles only
        if not isInAlliance(server.id, newUserAlliance):
            
            # new channel name should be a combination of both alliances abbreviations
            channelName = '{}-{}'.format(allianceId.lower(), newUserAlliance.lower())

            # check if channel exists. If so, just give user access to that channel
            if channelExists(server.channels, channelName):
                channel = getChannel(server.channels, channelName)
                await channel.set_permissions(newUser, overwrite=show)

            # if channel does not exist, create it and make it private except for the bot
            else:
                overwrites = {
                    server.default_role: hide,
                    server.me: show
                }
                channel = await server.create_text_channel(channelName, overwrites=overwrites)
                await channel.edit(category=getCategory(ctx.guild.channels, ambassadorCategory))

            # loop through all server roles. If role according to settings should be allowed to
            # enter channel, give them permissions to do so.
            for role in roles:
                if canAccessPrivateChannel(server.id, allianceId, role):
                    await channel.set_permissions(role, overwrite=show)

            # finally, give the new user permission to see channel
            await channel.set_permissions(newUser, overwrite=show)

        

# set the cog up
def setup(bot):
    bot.add_cog(RegistrationCog(bot))







