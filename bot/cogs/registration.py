import discord
from discord.ext import commands
import sys, asyncio, perms
sys.path.append('../utils')
import functions as f





class RegistrationCog:
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def register(self, ctx, *args):

        #ERROR CHECKING
        if f.serverNotRegistered(ctx.guild.id):
            err =  '{}, You have not registered your server with me yet. '.format(ctx.message.author.mention)
            err += 'To use this command, you must perform the bot setup. Use the command:'
            err += '```.setup <alliance abbreviation``` to setup your server with me.'
            await ctx.send(err)
            return


        # VARIABLES
        roles              = ctx.guild.roles                    # server roles
        userRoles          = ctx.message.author.roles           # roles of the user: default to message sender
        user               = ctx.message.author                 # the user: default to message sender
        server             = ctx.guild                          # server the command was used on
        alliance           = f.getAllianceId(server.id)
        memberRole         = f.getMemberRole(server.id)
        visitorRole        = f.getAmbassadorRole(server.id)
        ambassadorCategory = f.getAmbassadorCategory(server.id)
        userAlliance       = ''                                 # 4 character string abrevation of user alliance
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

        ### STEP ONE ###
        ### Set user role and nickname

        # CASE 1
        # Command is being used by an administrator. 
        if ctx.message.author.guild_permissions.administrator or f.hasRegisterCommandPermission(server.id, userRoles):

            # if admin is user command for other user, a mention of said user must be provide
            if len(ctx.message.mentions) > 0:
                user = ctx.message.mentions[0]
            else:
                res = '\nThis command requires a mention of the user,' 
                res += ' thier alliance prefix with brackets, and an the name of the role you wish to give the user.\n'
                res += '**EXAMPLE COMMAND:** !register @DATA [TEST] member'
                await ctx.send(res)

            # check each argument provided by admin.
            for arg in args:
                # ignore mention argument, handled above
                if (arg[0] != '<') and (arg[-1] != '>'):
                    # if argument is a role, set that role to the given user mentioned in command
                    if f.Is_Role(roles, arg):
                        await user.add_roles(f.getRole(roles, arg))

                    # if argument is alliance abbreviation, add it to users nickname
                    elif len(arg) < 5:
                        userAlliance = arg
                        await user.edit(nick='[{}] {}'.format(userAlliance.upper(), user.name))

                    else:
                        await ctx.send('{}, the argument "{}" is not valid for this command.'.format(user.mention, arg))
                        return


        # CASE 2
        # command is being used by a non administrator. User is
        # sent a private message, with guided information on how
        # to register. INTERACTIVE
        else:
            if not f.manualRegisterAllowed(server.d):
                err =  '{}, This server does not allow self registration. Please check with admin.'.format(ctx.message.author.mention)
                await ctx.send(err)
                return


            await ctx.send(user.mention+', I sent you a private message. Please respond to me there.')
            msg = '**Welcome to the {} Alliance server. I am here to help you register.**\n\n'.format(salliance)
            msg += 'To begin, are you a {} member, or an ambassador representing another Alliance? '.format(alliance)
            msg += 'Please respond with either **member** or **ambassador**'
            await self.bot.send_message(user, msg)

            while True:
                # wait for user response
                ans = await self.bot.wait_for_message(timeout=300, author=user)

                # response: member
                if ans.content.lower() == 'member':
                    # set user role based on DB alliance membber role, and set nickname to include alliance abreviation
                    await self.bot.add_roles(user, f.getRole(roles, memberRole)) 
                    await user.edit(nick='[{}] {}'.format(alliance, user.name))
                    msg = 'Thank you, **I have set your role and your nickname for this server.** You are now all set!'
                    await self.bot.send_message(user, msg)
                    return

                # response: ambassador  
                elif ans.content.lower() == 'ambassador':
                    # set user role based on DB ambassador role
                    await self.bot.add_roles(user, f.getRole(roles, visitorRole))
                    msg = '**Thank you, I have set your role.**\n'
                    msg += 'The last thing I need to know is your Alliance abbreviation. Please respond with only your Alliance abbreviation.\n'
                    msg += '**EXAMPLE RESPONSE:** ABCD'
                    await self.bot.send_message(user, msg)

                    while True:
                        # wait for user response
                        ans = await self.bot.wait_for_message(timeout=300, author=user)
                        # set nickname to include their alliance abreviation
                        if len(ans.content) < 5:
                            userAlliance = ans.content.lower()
                            await user.edit(nick='[{}] {}'.format(ans.content.upper(), user.name))
                            msg = 'Thank you, **I have set your role and your nickname for this server.**'
                            msg += ' You are now all set!'
                            await self.bot.send_message(user, msg)
                            break
                        else:
                            msg = 'I did not understand that response..\n\n'
                            msg += 'The last thing I need to know is your Alliance abbreviation. Please respond with only your Alliance abbreviation.\n'
                            msg += '**EXAMPLE RESPONSE:** ABCD'
                            await self.bot.send_message(user, msg) 
                    break
                # response was not member or ambassador. reloop
                else:
                    msg = 'I did not understand that response..\n\n'
                    msg += 'Are you a {} member, or an ambassador representing another Alliance?'.format(alliance)
                    msg += ' Please respond with either **member** or **ambassador**'
                    await self.bot.send_message(user, msg) 


        ### STEP TWO ###
        ### Create private channel for ambassadors

        if not f.createChannelAllowed(server.id):
            return


        # If user is not an alliance member -> aka an ambassador, we need tp
        # create a new channel for ambassadors and chosen server roles only
        if userAlliance and userAlliance.lower() != alliance.lower():
            
            # new channel name should be a combbination of both alliances abbreviations
            channelName = '{}-{}'.format(alliance.lower(), userAlliance.lower())

            # check if channel exists. If so, just give user access to that channel
            if f.channelExists(server.channels, channelName):
                channel = f.getChannel(server.channels, channelName)
                await channel.set_permissions(user, overwrite=show)

            # if channel does not exist, create it and make it private except for the bot
            else:
                overwrites = {
                    server.default_role: hide,
                    server.me: show
                }
                channel = await server.create_text_channel(channelName, overwrites=overwrites)
                await channel.edit(category=f.getCategory(ctx.guild.channels, ambassadorCategory))

            # loop through all server roles. If role according to settings should be allowed to
            # enter channel, give them permissions to do so.
            for role in roles:
                if f.canAccessPrivateChannel(server.d, role):
                    await channel.set_permissions(role, overwrite=show)

            # finally, give the new user permission to see channel
            await channel.set_permissions(user, overwrite=show)

        

# set the cog up
def setup(bot):
    bot.add_cog(RegistrationCog(bot))







