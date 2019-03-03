import sqlite3 as sqlite
import sys

DBNAME = 'data.db'

if len(sys.argv) > 2:
    print('**ERROR: Too many arguments. program takes at most one.\nexiting... ... ...')
    sys.exit()
    
# handle argument
if len(sys.argv) > 1:
    DBNAME = sys.argv[1]




def saveResource(system, warp, region, resource, tier):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()

    sql = '''
        SELECT ReliabilityScore
        FROM Resources
        WHERE System="{}"
        AND Resource="{}"
        AND Tier={}
    '''.format(system.lower(), resource.lower(), tier)
    res = queryDatabase(sql)

    # entry already in database, update reliability score
    if len(res):
        newScore = res[0][0] + 1
        sql = 'UPDATE Resources SET ReliabilityScore = ? WHERE System = ? AND Resource = ? AND Tier = ?'
        cur.execute(sql, (newScore, system.lower(), resource.lower(), tier))     

    # entry is new
    else:
        clms = '"System", "Warp", "Region", "Resource", "Tier", "ReliabilityScore"'
        sql = 'INSERT INTO Resources(' + clms + ') VALUES (?, ?, ?, ?, ?, ?)'
        cur.execute(sql, (system.lower(), warp, region.lower(), resource.lower(), tier, 3))

    conn.commit()





# Takes in a sql stmnt, executes the query againts the database, and returns a 
# response to the calling function.
def queryDatabase(sql):
    # connect to database
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    resp = cur.execute(sql).fetchall()
    conn.close()
    return resp



# Connect to database
conn = sqlite.connect(DBNAME)
cur = conn.cursor()


statement = "DROP TABLE IF EXISTS 'Resources';"
cur.execute(statement)
conn.commit()


statement = '''
CREATE TABLE 'Resources' (
    'ID' INTEGER PRIMARY KEY AUTOINCREMENT,
    'System' TEXT,
    'Warp' INTEGER,
    'Region' TEXT,
    'Resource' TEXT,
    'Tier' INTEGER,
    'ReliabilityScore' INTEGER
);
'''
cur.execute(statement)
conn.commit()
conn.close()

rssFile = open('resources.txt')
rssLines = rssFile.readlines()
rssType = ''
system = ''
lvl = ''
region = ''
grade = ''
for r in rssLines:
    splitLine = r.split('(')
    if len(splitLine) > 1:
        r = splitLine[0].split()[0]
        system = r
        r= splitLine[1].split()
        lvl = r[0][:(len(r[0])-1)]
        region = r[2]
        if rssType != 'dilithium':
            grade = r[4][1::]
        else:
            grade = 0
        saveResource(system, lvl, region, rssType, grade)
    else:
        r = r.split()
        rssType = r[0].split('\n')[0]

