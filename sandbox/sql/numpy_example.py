import sqlite3
import numpy as N
import cPickle

#data
data = N.ones((31, 31))
#picled binary
bd = cPickle.dumps(data)

#DB connection
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

#create a table
cursor.execute('create table PSFs (id integer primary key, image BLOB)')

#insert data
#cursor.execute("insert into PSFs (image) values(?)", (sqlite3.Binary(bd),))
cursor.execute("insert into PSFs (image) values(?)", (bd,))

#read stuff
cursor.execute("SELECT image from PSFs where id = 1")
for PSF, in cursor:
    data_out = cPickle.loads(PSF.encode('utf-8'))

print type(data_out), N.shape(data_out)
