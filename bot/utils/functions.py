import sys
from utils.data_database import queryDatabase, resetAllianceDatabase, createAllianceTables
from utils.constants import ORDERED_REACTIONS, IN_MESSAGE_REACTIONS





###################################################################
### GET FUNCTIONS #################################################
###################################################################



def getROEViolations(serverId, query):
    sql = '''
        SELECT AllianceID, Violations, PlayerName
        FROM ROE
        WHERE ServerId={}
    '''.format(serverId)

    if query:
        sql += 'AND AllianceID="{}"'.format(query)
    resp = queryDatabase(sql)

    if not len(resp):
        return ['**No ROE Violations']
    return resp
    



def getFormattedROEViolations(resp):

    roeList = ''
    for r in resp:
        roeList += '`[{}]'.format(r[0].upper() if r[0].lower() != 'n/a' else '????')
        i = len(r[0]) if r[0].lower() else 4
        while i < 5:
            roeList += '.'
            i += 1
        roeList += '` '
        roeList += '`{}'.format(r[2] if r[2] != None else '.')
        i = len(r[2]) if r[2] != None else 3
        while i < 15:
            roeList += '.'
            i += 1
        roeList += '`'
        roeList += ' `{} count`\n'.format(r[1])
    return roeList
    





def getAllies(serverId):
    sql = '''
        SELECT AllianceID
        FROM AllianceIntelligence
        WHERE ServerID={}
        AND AoA=1
    '''.format(serverId)
    resp = queryDatabase(sql)
    if len(resp):
        reduced = reduceResults(resp)
        strResult = ''
        for r in reduced:
            strResult += '{}, '.format(r) 
        return strResult
    return ''

def getKos(serverId):
    sql = '''
        SELECT AllianceID
        FROM AllianceIntelligence
        WHERE ServerID={}
        AND KOS=1
    '''.format(serverId)
    resp = queryDatabase(sql)
    if len(resp):
        reduced = reduceResults(resp)
        strResult = ''
        for r in reduced:
            strResult += '{}, '.format(r) 
        return strResult
    return ''

def getNaps(serverId):
    sql = '''
        SELECT AllianceID
        FROM AllianceIntelligence
        WHERE ServerID={}
        AND NAP=1
    '''.format(serverId)
    resp = queryDatabase(sql)
    if len(resp):
        reduced = reduceResults(resp)
        strResult = ''
        for r in reduced:
            strResult += '{}, '.format(r) 
        return strResult
    return ''


def getWar(serverId):
    sql = '''
        SELECT AllianceID
        FROM AllianceIntelligence
        WHERE ServerID={}
        AND War=1
    '''.format(serverId)
    resp = queryDatabase(sql)
    if len(resp):
        reduced = reduceResults(resp)
        strResult = ''
        for r in reduced:
            strResult += '{}, '.format(r) 
        return strResult
    return ''

def getRoeRules(serverId, allianceId):
    sql = '''
        Select RoeRules
        FROM GeneralAllianceInfo
        WHERE ServerID={}
        AND AllianceID="{}"
    '''.format(serverId, allianceId)
    resp = queryDatabase(sql)
    if len(resp):
        return resp[0][0]
    return ''

def getAlliesInfo(serverId, allianceId):
    sql = '''
        Select AlliesInfo
        FROM GeneralAllianceInfo
        WHERE ServerID={}
        AND AllianceID="{}"
    '''.format(serverId, allianceId)
    resp = queryDatabase(sql)
    if len(resp):
        return resp[0][0]
    return ''


def getNapInfo(serverId, allianceId):
    sql = '''
        Select NAPInfo
        FROM GeneralAllianceInfo
        WHERE ServerID={}
        AND AllianceID="{}"
    '''.format(serverId, allianceId)
    resp = queryDatabase(sql)
    if len(resp):
        return resp[0][0]
    return ''


def getKosInfo(serverId, allianceId):
    sql = '''
        Select KosInfo
        FROM GeneralAllianceInfo
        WHERE ServerID={}
        AND AllianceID="{}"
    '''.format(serverId, allianceId)
    resp = queryDatabase(sql)
    if len(resp):
        return resp[0][0]
    return ''


def getWarInfo(serverId, allianceId):
    sql = '''
        Select WarInfo
        FROM GeneralAllianceInfo
        WHERE ServerID={}
        AND AllianceID="{}"
    '''.format(serverId, allianceId)
    resp = queryDatabase(sql)
    if len(resp):
        return resp[0][0]
    return ''


def getFieldIntel(inputStr, newline):
    returnStr = ''
    count = 0
    for a in inputStr.split(','):
        count += 1
        if count < newline:
            returnStr += '{}, '.format(a)
        else:
            count = 0
            returnStr += '\n{}, '.format(a)
    return returnStr[:(len(returnStr) - 2)]


def getHomeInfo(serverId, allianceId):
    sql = '''
        Select HomeInfo
        FROM GeneralAllianceInfo
        WHERE ServerID={}
        AND AllianceID="{}"
    '''.format(serverId, allianceId)
    resp = queryDatabase(sql)
    if len(resp):
        return resp[0][0]
    return ''





# emojis: List of dicrod emoji objects
#  emoji: String, representing the name of emoji to get
def getEmoji(emojis, emoji):
    for e in emojis:
        if e.name.lower() == emoji.lower():
            return e
    return ''


# resource: String reperesentation of an stfc resource
#     tier: Integer value for stfc resouce grade (values 1, 2, 3, and 4)
#   system: String representationf of the stfc system the resource is located in
def getResourceReliability(resource, tier, system):
    addition = ''
    sql = '''
        SELECT ReliabilityScore
        FROM Resources
        WHERE Resource="{}"
        AND System="{}"
    '''.format(resource.lower(), system.lower())
    if tier:
        addition = ' AND Tier={}'.format(tier)

    res = queryDatabase(sql + addition)
    return res[0][0]


# resource: String reperesentation of an stfc resource
#     tier: Integer value for stfc resouce grade (values 1, 2, 3, and 4)
#   region: String representation of the stfc region the resource is located in
def getResourceResults(resource, tier, region):
    sql = 'select * FROM Resources'
    whereClause = ' WHERE'
    filter = ''
    numFilters = 0
    if resource:
        numFilters += 1
        filter += ' Resource="{}"'.format(resource.lower())
    if tier:
        numFilters += 1
        if numFilters > 1:
            filter += ' AND Tier="{}"'.format(int(tier))
        else:
            filter += ' Tier="{}"'.format(int(tier))
    if region:
        numFilters += 1
        if numFilters > 1:
            filter += ' AND Region="{}"'.format(region.lower())
        else:
            filter += ' region="{}"'.format(region.lower())

    if numFilters > 0:
        sql = sql + whereClause
    
    return queryDatabase(sql+filter+' ORDER BY Resource == "dilithium", Resource, Tier DESC, Region')


#     args: A list of arguments, representing a resources search query
#   footer: a string value of the footer for the resources embed
# resource: String reperesentation of an stfc resource
#     tier: Integer value for stfc resouce grade (values 1, 2, 3, and 4)
#   system: String representationf of the stfc system the resource is located in
def getSearchQuerys(args, footer, resource, region, tier):
    footer = 'FILTERS:'

    resource = tier = region = ''
    # loop through search parameters, and set resource, region, and tier variable
    for arg in args:
        arg = str(arg)
        if arg.lower() == 'crystal' or arg.lower() == 'ore' or arg.lower() == 'gas' or arg.lower() == 'dilithium':
            footer += ' "{}" '.format(arg) # add filter name to footer for info purposes
            resource = arg
        if arg.lower() == 'federation' or arg.lower() == 'romulan' or arg.lower() == 'klingon' or arg.lower() == 'neutral':
            footer += ' "{}" '.format(arg) # add filter name to footer for info purposes
            region = arg
        if arg[0] == '1' or arg[0] == '2' or arg[0] == '3' or arg[0] == '4':
            footer += ' "grade {}" '.format(arg[0]) # add filter name to footer for info purposes
            tier = arg[0]
    
    # If user did not include any search paramaters, then filters is none
    if not len(args):
        footer += 'none'

    return footer, resource, region, tier


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
        SELECT S.AllianceName, S.CreateChannel, S.ChannelCategory, R.Role, R.MemberRole, R.AmbassadorRole, R.AllyRole, R.AdminRole, R.AccessAmbassadorChannels
        FROM Server AS S
        JOIN AllianceRolePermissions As R ON S.ServerID=R.ServerID AND R.AllianceID='{}'
        WHERE S.ServerID={}
    '''.format(allianceId, serverId)

    resp = queryDatabase(sql)
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
    res = queryDatabase(sql)
    return reduceResults(res)


# serverId: id for current server, from discord guild object
def getAllianceName(serverId):
    sql = '''
        SELECT S.AllianceName
        FROM Server AS S
        WHERE S.ServerID={}
    '''.format(serverId)
    res = queryDatabase(sql)
    return res[0][0]


# serverId: id for current server, from discord guild object
def getMemberRoles(serverId, allianceId):
    sql = '''
        SELECT R.Role
        FROM AllianceRolePermissions AS R
        WHERE R.ServerID={}
        AND R.AllianceID='{}'
        AND R.MemberRole=1
    '''.format(serverId, allianceId.upper())
    return reduceResults(queryDatabase(sql))


# serverId: id for current server, from discord guild object
def getAmbassadorRoles(serverId, allianceId):
    sql = '''
        SELECT R.Role
        FROM AllianceRolePermissions AS R
        WHERE R.ServerID={}
        AND R.AllianceID='{}'
        AND R.AmbassadorRole=1
    '''.format(serverId, allianceId.upper())
    return reduceResults(queryDatabase(sql))


# serverId: id for current server, from discord guild object
def getAllyRoles(serverId, allianceId):
    sql = '''
        SELECT R.Role
        FROM AllianceRolePermissions AS R
        WHERE R.ServerID={}
        AND R.AllianceID='{}'
        AND R.AllyRole=1
    '''.format(serverId, allianceId.upper())
    return reduceResults(queryDatabase(sql))


# serverId: id for current server, from discord guild object
def getAmbassadorCategory(serverId):
    sql = '''
        SELECT S.ChannelCategory
        FROM Server AS S
        WHERE S.ServerID={}
    '''.format(serverId)
    res = queryDatabase(sql)
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
    
    res = queryDatabase(sql)
    return res[0]


# serverId: id for current server, from discord guild object
def createChannelAllowed(serverId):
    sql = '''
        SELECT S.CreateChannel
        FROM Server AS S
        WHERE S.ServerID={}
    '''.format(serverId)
    
    res = queryDatabase(sql)
    if len(res):
        return res[0][0]
    return False


def hasIntel(serverId):
    sql = '''
        SELECT *
        FROM AllianceIntelligence
        WHERE ServerID={}
    '''.format(serverId) 
    res = queryDatabase(sql)
    return len(res)

def hasGeneralInfo(serverId):
    sql = '''
        SELECT *
        FROM GeneralAllianceInfo
        WHERE ServerID={}
    '''.format(serverId) 
    res = queryDatabase(sql)
    return len(res)


def isAllianceMember(serverId, userRoles):
    for role in userRoles:
        sql = '''
            SELECT R.AdminRole
            FROM AllianceRolePermissions AS R
            WHERE R.ServerID={}
            AND R.Role='{}'
        '''.format(serverId, role.name.lower())
        res = queryDatabase(sql)

        if len(res) and res[0][0]:
            return True

        sql = '''
            SELECT R.MemberRole
            FROM AllianceRolePermissions AS R
            WHERE R.ServerID={}
            AND R.Role='{}'
        '''.format(serverId, role.name.lower())
        res = queryDatabase(sql)

        if len(res) and res[0][0]:
            return True
    return False



# serverId: id for current server, from discord guild object
#    roles: list of discord role objects
def hasAdminPermission(serverId, allianceId, roles):
    for role in roles:
        sql = '''
            SELECT R.AdminRole
            FROM AllianceRolePermissions AS R
            WHERE R.ServerID={}
            AND R.AllianceID='{}'
            AND R.Role='{}'
        '''.format(serverId, allianceId, role.name.lower())

        res = queryDatabase(sql)
        if len(res) and res[0][0]:
            return True
    return False


# serverId: id for current server, from discord guild object
#     role: discord role object
def canAccessPrivateChannel(serverId, allianceId, role):
    sql = '''
        SELECT R.AccessAmbassadorChannels
        FROM AllianceRolePermissions AS R
        WHERE R.ServerID={}
        AND R.AllianceID='{}'
        AND R.Role='{}'
    '''.format(serverId, allianceId, role.name.lower())
    
    res = queryDatabase(sql)
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

    res = queryDatabase(sql)
    return len(res)


#      serverId: Discord server id number
# newAllianceId: String of new alliance id
def isInAlliance(serverId, newAllianceId):
    sql = '''
        SELECT A.AllianceID
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    res = queryDatabase(sql)

    for id in res:
        if id[0].lower() == newAllianceId.lower():
            return True
    return False


def hasSTFCEmojis(emojis):
    numEmojisFound = 0
    for e in emojis:
        if e.name.lower() == 'crystal':
            numEmojisFound += 1
        if e.name.lower() == 'gas':
            numEmojisFound += 1
        if e.name.lower() == 'dilithium':
            numEmojisFound += 1
        if e.name.lower() == 'ore':
            numEmojisFound += 1
        if e.name.lower() == 'federation':
            numEmojisFound += 1
        if e.name.lower() == 'neutral':
            numEmojisFound += 1
        if e.name.lower() == 'klingon':
            numEmojisFound += 1
        if e.name.lower() == 'romulan':
            numEmojisFound += 1
        if e.name[0] == '0':
            numEmojisFound += 1
        if e.name[0] == '2':
            numEmojisFound += 1
        if e.name[0] == '3':
            numEmojisFound += 1
        if e.name[0] == '4':
            numEmojisFound += 1
    return numEmojisFound == 12


# reaction: A discord reaction object
def checkForSTFCEmoji(reaction):
    try:
        if reaction.emoji.name== 'crystal' or reaction.emoji.name == 'ore' or reaction.emoji.name == 'gas' or reaction.emoji.name == 'dilithium':
            return True
        if reaction.emoji.name == 'federation' or reaction.emoji.name == 'romulan' or reaction.emoji.name == 'klingon' or reaction.emoji.name == 'neutral':
            return True
        if reaction.emoji.name[0] == '1' or reaction.emoji.name[0] == '2' or reaction.emoji.name[0] == '3' or reaction.emoji.name[0] == '4':
            return True
    except:
        return False 



###################################################################
### HELPER FUNCTIONS ##############################################
###################################################################



# emojis: A list of discord Emoji objects
#   vals: list of Strings representing resource search params
def prepareResourceResults(emojis, vals):
    resource      = '`{}{}`'.format(vals[4], '.' * (10 - len(vals[4])))
    tier          = '`{}*`'.format(vals[5]) if vals[5] else '`..`'
    region        = '`{}`'.format(vals[3])
    hasEmojis     = hasSTFCEmojis(emojis)
    regionName    =  '{}'.format(vals[3].title()) if hasEmojis else ''
    if hasEmojis:
        emojiResource = getEmoji(emojis, vals[4])
        emojiTier     = getEmoji(emojis, '{}star'.format(vals[5]))
        emojiRegion   = getEmoji(emojis, vals[3])


    if hasEmojis and emojiResource:
        resource = emojiResource
    if hasEmojis and emojiRegion:
        region = emojiRegion
    if hasEmojis and emojiTier:
        tier = emojiTier

    # to keep things nice and tidy, format system name to be MIN 14 characters long
    systemName = '`{}({})'.format(vals[1], vals[2])
    i = len(vals[1])
    while i < 14:
        systemName += '.'
        i += 1
    systemName += '`'
    return '{} {} {} {}{}\n'.format(str(resource), str(tier), systemName, region, regionName)


#        args: a list of string search parameters
# searchParam: The param to remove from args
def removeSearchParam(args, searchParam):
    list = []
    for arg in args:
        if arg != searchParam:
            list.append(arg)
    return list


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

        res = queryDatabase('SELECT AllianceID FROM Alliance WHERE ServerID={}'.format(serverId))

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

        summary += '\n***Admin Roles:***\n'
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
    alliancesExist = queryDatabase(sql)
    sql = 'SELECT AllianceID FROM Alliance WHERE ServerID={} AND AllianceID="{}"'.format(serverId, allianceId)
    thisAllianceExists = queryDatabase(sql)

    # Not first time set up if server is registered and this alliance id is not
    if len(alliancesExist) and not len(thisAllianceExists):
        return alliancesExist[0][0]
    return None


# completely wipe the database,a nd recreate tables
def databaseReset():
    resetAllianceDatabase()
    createAllianceTables()
