'''
Created on Aug 24, 2009

@author: niemi
'''

import os, glob, time, shutil
 
#from
folder = '/smov/cos/Data/11484/fastrack/'
file = '*rawtag*.fits' 

#to
to = '/grp/hst/cos/users/niemi/COSFocus/data/'

#comparison
dt = time.strptime("24 Aug 09 12:12:12", "%d %b %y %H:%M:%S")
#dt = time.strptime("25 Jul 09 12:12:12", "%d %b %y %H:%M:%S")
#dt = time.strptime("24 Aug 09", "%d %b %y")


#time sorting
# (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
timed = 9

date_file_list = []

for fits in glob.glob(folder + file):
    # retrieves the stats for the current file as a tuple
    # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
    # the tuple element mtime at index 8 is the last-modified-date
    stats = os.stat(fits)
    # create tuple (year yyyy, month(1-12), day(1-31), hour(0-23), minute(0-59), second(0-59),
    # weekday(0-6, 0 is monday), Julian day(1-366), daylight flag(-1,0 or 1)) from seconds since epoch
    # note:  this tuple can be sorted properly by date and time
    date = time.localtime(stats[timed])
    # create list of tuples ready for sorting by date
    date_file_list.append((date, fits))
 
date_file_list.reverse()  # newest first
    
for file in date_file_list:
    folder, file_name = os.path.split(file[1])
    # convert date tuple to MM/DD/YYYY HH:MM:SS format
    #file_date = time.strftime("%m/%d/%y %H:%M:%S", file[0])

    copy = True
    #check that file is not already preset
    for old in glob.glob(to + '*rawtag*.fits'):
        fd_, fn = os.path.split(old)
        if fn == file_name:
            copy = False
    
    if copy:
        #check that the file is newer than dt
        if file[0] > dt:
            #lets copy
            print 'Copying %s to %s' % (folder+'/'+file_name, to)
            shutil.copy(folder+'/'+file_name, to)
        else:
            break

#print "%-40s %s" % ("filename:", "last modified:")
#for file in date_file_list:
    # extract just the filename
#    folder, file_name = os.path.split(file[1])
    # convert date tuple to MM/DD/YYYY HH:MM:SS format
#    file_date = time.strftime("%m/%d/%y %H:%M:%S", file[0])
#    print "%-40s %s" % (file_name, file_date)
 

print '-'*60
print 'Scipt finished...'