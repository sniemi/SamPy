import os

print "Some info of your environment...\n"
print "\n".join(["%s=%s" % (k,v) for k, v in os.environ.items()])

