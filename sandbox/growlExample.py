import Growl as grr
import numpy as N
import time

# Growl setup
appname = 'Growl example'
notification_names = ['Iteration finished','Program finished']
appicon = grr.Image.imageFromPath('App.icns')

popup = grr.GrowlNotifier(appname,notification_names,applicationIcon=appicon)
popup.register()


# Code that does work
for i in N.arange(1,6):
	time.sleep(5)
	print "Iteration %s finished." % i
	popup.notify(notification_names[0],appname,'Iteration %s finished.' % i)

popup.notify(notification_names[1],appname,'Growl example finished.')
