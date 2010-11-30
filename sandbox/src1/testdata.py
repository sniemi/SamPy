import sys

SMNmods = '/Users/Sammy/Python/'
sys.path.append(SMNmods)

import sami.MySQLdbSMN as DB

sql = 'select mvir, np from FieldEllipticals where type = 0 order by galaxyId'
db = DB.MySQLdbSMN(sql, 'FieldEllipticalStudy')
dt = db.fetchdata()

import numpy as N
data = N.array(dt)

print data[:,0]
