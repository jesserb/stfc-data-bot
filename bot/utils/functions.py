import sys
import data_database as db
from constants import ORDERED_REACTIONS, IN_MESSAGE_REACTIONS


###################################################################
### GET FUNCTIONS #################################################
###################################################################

#  nickname: string representation of users server nickname
def getAllianceIdFromNick(nickname):
    nick = nickname.split()[0]
    if (nick and nick[0] == '[' and nick[-1] == ']'):
        return nick[1:(len(nick)-1)]
    return None

# members: list of discord member objects
#  member: string name of member
def getMember(member, members):
    for m in members:
        if m.name.lower() == member.lower():
            return m
        return None


#   serverId: id for current server, from discord guild object
# allianceId: an alliance string ID
#      roles: list of discord role objects
# categories: list of discord category objects
def getSettings(serverId, allianceId, roles, categories):
    sql = '''
        SELECT S.AllianceName, S.CreateChannel, S.ChannelCategory, R.Role, R.MemberRole, R.AmbassadorRole, R.AllyRole, R.AdminRegister, R.AccessAmbassadorChannels
        FROM Server AS S
        JOIN RegisterCommandSettings As R ON S.ServerID=R.ServerID AND R.AllianceID='{}'
        WHERE S.ServerID={}
    '''.format(allianceId, serverId)

    resp = db.queryDatabase(sql)
    memberRoles = []
    ambassadorRoles = []
    allyRoles = []
    registerRoles = []
    accessRoles = []
    for i in range(len(resp)):
        memberRoles.append({"role": getRole(roles, resp[i][3]), "selected": False})
        ambassadorRoles.append({"role": getRole(roles, resp[i][3]), "selected": False})
        allyRoles.append({"role": getRole(roles, resp[i][3]), "selected": False})
        registerRoles.append({"role": getRole(roles, resp[i][3]), "selected": False})
        accessRoles.append({"role": getRole(roles, resp[i][3]), "selected": False})
        if resp[i][4]:
            memberRoles[i]["selected"] = True
        if resp[i][5]:
            ambassadorRoles[i]["selected"] = True
        if resp[i][6]:
            allyRoles[i]["selected"] = True
        if resp[i][7]:
            registerRoles[i]["selected"] = True
        if resp[i][8]:
            accessRoles[i]["selected"] = True

    return {
        "alliance": resp[0][0],
        "manualRegister": resp[0][1],
        "createChannel": resp[0][2],
        "channelCategory": getCategory(categories, resp[0][3]),
        "memberRoles": memberRoles,
        "ambassadorRoles": ambassadorRoles,
        "allyRoles": allyRoles,
        "canRegisterUserRoles": registerRoles,
        "canAccessPrivateChannelRoles": accessRoles
    }


# roles: list of discord role objects
#  role: string name of role
def getRole(roles, role):
    for r in roles:
        if (r.name).lower() == role.lower():
            return r
    return None

# channels: list of discord channel objects
#  channel: string name of channel
def getChannel(channels, channel):
    for c in channels:
        if c.name.lower() == channel.lower():
            return c
    return None

# channels: list of discord channel objects
# category: string name of category
def getCategory(channels, category):
    for c in channels:
        if c.name.lower() == category.lower():
            return c
    return None

# serverId: id for current server, from discord guild object
def getAllianceIds(serverId):
    sql = '''
        SELECT A.AllianceID
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    res = db.queryDatabase(sql)
    return reduceResults(res)

# serverId: id for current server, from discord guild object
def getAllianceName(serverId):
    sql = '''
        SELECT S.AllianceName
        FROM Server AS S
        WHERE S.ServerID={}
    '''.format(serverId)
    res = db.queryDatabase(sql)
    return res[0][0]

# serverId: id for current server, from discord guild object
def getMemberRoles(serverId, allianceId):
    sql = '''
        SELECT R.Role
        FROM RegisterCommandSettings AS R
        WHERE R.ServerID={}
        AND R.AllianceID='{}'
        AND R.MemberRole=1
    '''.format(serverId, allianceId.upper())
    return reduceResults(db.queryDatabase(sql))

# serverId: id for current server, from discord guild object
def getAmbassadorRoles(serverId, allianceId):
    sql = '''
        SELECT R.Role
        FROM RegisterCommandSettings AS R
        WHERE R.ServerID={}
        AND R.AllianceID='{}'
        AND R.AmbassadorRole=1
    '''.format(serverId, allianceId.upper())
    return reduceResults(db.queryDatabase(sql))

# serverId: id for current server, from discord guild object
def getAllyRoles(serverId, allianceId):
    sql = '''
        SELECT R.Role
        FROM RegisterCommandSettings AS R
        WHERE R.ServerID={}
        AND R.AllianceID='{}'
        AND R.AllyRole=1
    '''.format(serverId, allianceId.upper())
    return reduceResults(db.queryDatabase(sql))

# serverId: id for current server, from discord guild object
def getAmbassadorCategory(serverId):
    sql = '''
        SELECT S.ChannelCategory
        FROM Server AS S
        WHERE S.ServerID={}
    '''.format(serverId)
    res = db.queryDatabase(sql)
    return res[0][0]



###################################################################
### ASSERT FUNCTIONS ##############################################
###################################################################


# members: list of discord member objects
#  member: string name of member
def isUser(member, members):
    for m in members:
        if (m.name).lower() == member.lower():
            return True
    return False

# roles: list of discord role objects
#  role: string name of role
def Is_Role(roles, role):
    for r in roles:
        if (r.name).lower() == role.lower():
            return True
    return False

# channels: list of discord channel objects
#  channel: string name of channel
def channelExists(channels, channel):
    for c in channels:
        if c.name.lower() == channel.lower():
            return True
    return False

# selectedRoles: list of dictionaries
#                parameter role: discord role object
#                paramater selected: boolean
#          role: discord role object
def selectedRole(selectedRoles, role):
    for r in selectedRoles:
        if r['role'].id == role.id:
            return r['selected']
    return False

# serverId: id for current server, from discord guild object
def manualRegisterAllowed(serverId):
    sql = '''
        SELECT S.ManualRegister
        FROM Server AS S
        WHERE S.ServerID={}
    '''.format(serverId)
    
    res = db.queryDatabase(sql)
    return res[0]

# serverId: id for current server, from discord guild object
def createChannelAllowed(serverId):
    sql = '''
        SELECT S.CreateChannel
        FROM Server AS S
        WHERE S.ServerID={}
    '''.format(serverId)
    
    res = db.queryDatabase(sql)
    if len(res):
        return res[0][0]
    return False

# serverId: id for current server, from discord guild object
#    roles: list of discord role objects
def hasRegisterCommandPermission(serverId, allianceId, roles):
    for role in roles:
        sql = '''
            SELECT R.AdminRegister
            FROM RegisterCommandSettings AS R
            WHERE R.ServerID={}
            AND R.AllianceID='{}'
            AND R.Role='{}'
        '''.format(serverId, allianceId, role.name.lower())

        res = db.queryDatabase(sql)
        if len(res) and res[0][0]:
            return True
    return False

# serverId: id for current server, from discord guild object
#     role: discord role object
def canAccessPrivateChannel(serverId, allianceId, role):
    sql = '''
        SELECT R.AccessAmbassadorChannels
        FROM RegisterCommandSettings AS R
        WHERE R.ServerID={}
        AND R.AllianceID='{}'
        AND R.Role='{}'
    '''.format(serverId, allianceId, role.name.lower())
    
    res = db.queryDatabase(sql)
    if len(res):
        return res[0][0]
    return False

# serverId: Discord server id number
def serverRegistered(serverId):
    sql = '''
        SELECT A.ServerID
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)

    res = db.queryDatabase(sql)
    return len(res)


#      serverId: Discord server id number
# newAllianceId: String of new alliance id
def isInAlliance(serverId, newAllianceId):
    sql = '''
        SELECT A.AllianceID
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    res = db.queryDatabase(sql)

    for id in res:
        if id[0].lower() == newAllianceId.lower():
            return True
    return False


###################################################################
### HELPER FUNCTIONS ##############################################
###################################################################


# arr: an array of tuples (2d)
def reduceResults(arr):
    newArr = []
    for ele in arr:
        newArr.append(ele[0])
    return newArr


# selectedRoles: list of dictionaries
#                parameter role: discord role object
#                paramater selected: boolean
#          role: discord role object
def deselectRole(selectedRoles, role):
    for r in selectedRoles:
        if r['role'].id == role.id:
            r['selected'] = False



#         roles: List of discord role objects
#      reaction: A discord reaction object
# selectedRoles: list of dictionaries
#                parameter role: discord role object
#                paramater selected: boolean
def getSelectedRoles(roles, reaction, roleSelection):
    desc = ''
    for i in range(len(roles)):

        # in first block, handle selected emoji and its role
        if reaction.emoji == ORDERED_REACTIONS[i]:

            #if role is currently not selected, select it - otherwise deselect it
            if not selectedRole(roleSelection, roles[i]):
                roleSelection[i]['selected'] = True
                desc +='{} {}  {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name, '✅')
            else:
                deselectRole(roleSelection, roles[i])
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

        # for all other roles, show based on state in rroleSelection state
        else:
            if roleSelection[i]['selected']:
                desc +='{} {}  {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name, '✅')
            else:
                desc +='{} {}\n'.format(IN_MESSAGE_REACTIONS[i], roles[i].name)

    # once user has at least one selected role, explain how to move on to next step
    if len(roleSelection) > 0:
        desc += '\n**When you have selected all your roles, please select the :arrow_right: symbol to continue...**'
    
    return roleSelection, desc



#           title: string
#        serverId: discord server id, integer
#        alliance: the name of the current discord server
#      allianceId: an alliance acronym, 4 letter string
#          manual: integer of 0 or 1, represents manual Registration perm
#         private: integer of 0 or 1, represents private channel creation perm
#        category: a discord channel category object
#     memberRoles: array of objects with param role: discord role obj. selected: boolean
# ambassadorRoles: array of objects with param role: discord role obj. selected: boolean
#       allyRoles: array of objects with param role: discord role obj. selected: boolean
#   registerRoles: array of objects with param role: discord role obj. selected: boolean
#        pvtRoles: array of objects with param role: discord role obj. selected: boolean
def getSetupSummary(title, serverId, alliance, allianceId, manual, private, category,
                    memberRoles, ambassadorRoles, allyRoles, registerRoles, pvtRoles):

        res = db.queryDatabase('SELECT AllianceID FROM Alliance WHERE ServerID={}'.format(serverId))

        summary = '**{}**\n\nBelow is your server settings.\n\n'.format(title)
        summary += '**ALLIANCE:** {}\n'.format(alliance)

        if not len(res):
            summary += '**ALLIANCE-ID:** {}\n\n'.format(allianceId)
        else:
            summary += '**ALLIANCE-IDS:**\n'
            for id in res:
                summary += '× {}\n'.format(id[0])
            summary += '\n'

        if manual:
            summary += '**[YES]** [NO] Users can self register\n'
        else:
            summary += '[YES] **[NO]** Users can self register\n'

        if private:
            summary += '**[YES]** [NO] Create private channel\n\n'
        else:
            summary += '[YES] **[NO]** Create private channel\n\n'

        if category != None:
            summary += '**Private Channel Category:** {}\n'.format(category.name)

        summary += '\n__**REGISTER COMMAND**__\n***New roles to give to new members:***\n'
        for r in memberRoles:
            if r['selected']:
                summary += '× {}\n'.format(r['role'].name)

        summary += '\n***Roles to give new ambassadors:***\n'
        for r in ambassadorRoles:
            if r['selected']:
                summary += '× {}\n'.format(r['role'].name)

        summary += '\n***Roles to give new ally ambassadors:***\n'
        for r in allyRoles:
            if r['selected']:
                summary += '× {}\n'.format(r['role'].name)

        summary += '\n***Roles that can set up other users:***\n'
        for r in registerRoles:
            if r['selected']:
                summary += '× {}\n'.format(r['role'].name)
        summary += '\n'

        summary += '**PRIVATE CHANNEL PERMS**\n***Roles that have access to new privte channels:***\n'
        for r in pvtRoles:
            if r['selected']:
                summary += '× {}\n'.format(r['role'].name)
        return summary



###################################################################
### DATABASE ACTIONS FUNCTIONS ####################################
###################################################################

#   serverId: discord server id, integer
# allianceId: an alliance acronym, 4 letter string
def determineFirstTimeSetup(serverId, allianceId):
    sql = 'SELECT AllianceID FROM Alliance WHERE ServerID={}'.format(serverId)
    alliancesExist = db.queryDatabase(sql)
    sql = 'SELECT AllianceID FROM Alliance WHERE ServerID={} AND AllianceID="{}"'.format(serverId, allianceId)
    thisAllianceExists = db.queryDatabase(sql)

    # Not first time set up if server is registered and this alliance id is not
    if len(alliancesExist) and not len(thisAllianceExists):
        return alliancesExist[0][0]
    return None


# completely wipe the database,a nd recreate tables
def databaseReset():
    db.resetDatabase()
    db.createDatabase()
    


