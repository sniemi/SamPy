import sqlite3
import time

def power10(x):
    return 10**x

#create a Connection object that represents the database                                                        #to a file                                                                                                       
#conn = sqlite3.connect('/tmp/example')                                                                          
#to memory                                                                                                       
conn = sqlite3.connect(':memory:')

conn.create_function("power10", 1, power10)
c = conn.cursor()

# Create table 

c.execute('''create table properties 
(id integer, object text, sdds_g real, size real, colour real)''')

#insert data                                                                                                     
for t in [(1, 'NGC 123', -15, 1, -1.4),
          (2, 'NGC 220', -16, 1.5, -1.0),
          (3, 'NGC 999', -20, 2, 0.05)]:
    c.execute('insert into properties values (?,?,?,?,?)', t)

c.execute('''CREATE UNIQUE INDEX id_prop on properties (id)''')

# Save (commit) the changes                                                                                      
conn.commit()

#create another table                                                                                            
c.execute('''create table haloes (id integer, mass real, momentum real)''')

for t in [[2, 12.345435, 0.0345345345],
          [3, 13.1, 0.23434354],
          [9, 9.9, 0.999999999],
          [22, 14.2222, 0.12345]
          ]:
    c.execute('insert into haloes values (?,?,?)', t)

c.execute('''CREATE UNIQUE INDEX id_halo on haloes (id)''')

conn.commit()

#print out properties                                                                                            
print 'properties table:'
c.execute('select * from properties order by id')
for row in c:
    print row

print '\nA haloes table:'
#print out haloes                                                                                                
c.execute('select * from haloes order by id')
for row in c:
    print row


st = time.clock()
#lets join the to tables with ids                                                                                
#inner join could also be join                                                                                   
c.execute('''select *                                                                                            
from properties                                                                                                  
inner join haloes on                                                                                             
properties.id = haloes.id                                                                                        
''')

print '\nJoin table with inner join:'
for row in c:
    print row
print 'Time %e' % (time.clock() - st)

print '\nJoin 2 table with inner join (more stuff):'
st = time.clock()
c.execute('''select properties.id, object, sdds_g, size, colour,                                                 
power10(mass) / power10(9), momentum                                                                         
from properties                                                                                                  
inner join haloes on                                                                                             
properties.id = haloes.id                                                                                        
''')

data = c.fetchall()

for row in data:
    print row
print 'Time: %e' % (time.clock() - st)

#join using where

print '\nJoin with where (same query as above):'

st = time.clock()
c.execute('''select properties.id, object, sdds_g, size, colour,
power10(mass)/power10(9), momentum from properties, haloes where
properties.id = haloes.id''')

for row in c.fetchall(): print row
print 'Time %e' % (time.clock() - st)


print '\nJoin with where using idexing:'

st = time.clock()
c.execute('''select properties.id, object, sdds_g, size, colour,
power10(mass)/power10(9), momentum from properties, haloes
where
properties.id = haloes.id''')

for row in c.fetchall(): print row
print 'Time %e' % (time.clock() - st)

# We can also close the cursor if we are done with it                                                            
c.close()

