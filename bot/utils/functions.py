import sys
import data_database as db



###################################################################
### GET FUNCTIONS #################################################
###################################################################


def getSettings(serverId):
    sql = '''
        SELECT *
        FROM Alliance AS A
        JOIN RegisterCommandSettings As R ON A.ServerID=R.ServerID
        WHERE R.ServerID={}
        AND (R.AdminRegister=1 OR R.AccessAmbassadorChannels=1)
    '''.format(serverId)
    resp = db.queryDatabase(sql)

    registerRoles = []
    accessRoles = []
    for r in resp:
        if r[10]:
            registerRoles.append(r[9])
        if r[11]:
            accessRoles.append(r[9])

    return {
        "alliance": resp[0][1],
        "manualRegister": resp[0][2],
        "createChannel": resp[0][3],
        "channelCategory": resp[0][4],
        "memberRole": resp[0][5],
        "ambassadorRole": resp[0][6],
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
            return c.category
    return None

# serverId: id for current server, from discord guild object
def getAllianceId(serverId):
    sql = '''
        SELECT A.AllianceID
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    return db.queryDatabase(sql)

# serverId: id for current server, from discord guild object
def getMemberRole(serverId):
    sql = '''
        SELECT A.MemberRole
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    return db.queryDatabase(sql)

# serverId: id for current server, from discord guild object
def getAmbassadorRole(serverId):
    sql = '''
        SELECT A.AmbassadorRole
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    return db.queryDatabase(sql)

def getAmbassadorCategory(serverId):
    sql = '''
        SELECT A.ChannelCategory
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    return db.queryDatabase(sql)



###################################################################
### ASSERT FUNCTIONS ##############################################
###################################################################



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
        SELECT A.ManualRegister
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    
    res = db.queryDatabase(sql)
    if len(res):
        return res[0][0]
    return False

# serverId: id for current server, from discord guild object
def createChannelAllowed(serverId):
    sql = '''
        SELECT A.CreateChannel
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    
    res = db.queryDatabase(sql)
    if len(res):
        return res[0][0]
    return False

# serverId: id for current server, from discord guild object
#    roles: list of discord role objects
def hasRegisterCommandPermission(serverId, roles):
    for role in roles:
        sql = '''
            SELECT R.AdminRegister
            FROM RegisterCommandSettings AS R
            WHERE R.ServerID={}
            AND R.AllianceRole=={}
        '''.format(serverId, role.name)
    
        res = db.queryDatabase(sql)
        if len(res) and res[0][0]:
            return True
    return False

# serverId: id for current server, from discord guild object
#     role: discord role object
def canAccessPrivateChannel(serverId, role):
    sql = '''
        SELECT R.AccessAmbassadorChannels
        FROM RegisterCommandSettings AS R
        WHERE R.ServerID={}
        AND R.AllianceRole=={}
    '''.format(serverId, role.name)
    
    res = db.queryDatabase(sql)
    if len(res):
        return res[0][0]
    return False


def serverNotRegistered(serverId):
    sql = '''
        SELECT A.ServerID
        FROM Alliance AS A
        WHERE A.ServerID={}
    '''.format(serverId)
    
    res = db.queryDatabase(sql)
    return len(res)




###################################################################
### HELPER FUNCTIONS ##############################################
###################################################################



# selectedRoles: list of dictionaries
#                parameter role: discord role object
#                paramater selected: boolean
#          role: discord role object
def deselectRole(selectedRoles, role):
    for r in selectedRoles:
        if r['role'].id == role.id:
            r['selected'] = False




