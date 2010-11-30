import sqlite3
import image as I

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

imageName = "Example.png"

imageFile = open(imageName, 'rb') 

b = sqlite3.Binary(imageFile.read())

cursor.execute('create table images (id integer primary key, image BLOB)')

cursor.execute("insert into images (image) values(?)", (b,))


#print out the image
cursor.execute("SELECT image from images where id = 1")
for image, in cursor:
#    print image
    x = image


