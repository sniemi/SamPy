# might be a good idea to check for errors, eh?

# Tim Mooney 3/25/03

from CaChannel import *
import time

# The dictionary cadict will be used to associate PV names with the
# machinery required to talk to EPICS PV's.  If no entry is found (the
# name hasn't been used yet in a ca call), then we create a new instance
# of CaChannel, connect it to EPICS, and put it in the dictionary.  We also
# include a flag some of the ca_util routines can use to check if a callback
# has occurred for this PV.

cadict = {}

def checkName(name):
	"""usage: checkName("xxx:m1.VAL")"""
	if not cadict.has_key(name):
		# Make a new entry in the PV-name dictionary
		channel = CaChannel()
		try:
			channel.searchw(name)
		except CaChannelException, status:
			print "checkName: CaChannel exception, status=", status
			raise CaChannelException, status
			return
		cadict[name] = [channel, 0]		# [channel, callback_flag]

def caget(name):
	"""usage: val = caget("xxx:m1.VAL")"""
	try:
		checkName(name)
	except CaChannelException, status:
		print "caget: CaChannel exception, status=", status
		raise CaChannelException, status
		return 0

	try:
		val = cadict[name][0].getw()
	except CaChannelException, status:
		print "caget: CaChannel exception, status=", status
		raise CaChannelException, status
		return 0

	return val

def caput(name, value):
	"""usage: caput("xxx:m1.VAL", new_value)"""
	try:
		checkName(name)
	except CaChannelException, status:
		print "caput: CaChannel exception, status=", status
		raise CaChannelException, status
		return

	try:
		cadict[name][0].putw(value)
	except CaChannelException, status:
		print "caput: CaChannel exception, status=", status
		raise CaChannelException, status

def waitCB(epics_args, user_args):
	cadict[user_args[0]][1] = 1

def caputw(name, value):
	"""usage: caputw("xxx:m1.VAL", new_value)"""
	try:
		checkName(name)
	except CaChannelException, status:
		print "caputw: CaChannel exception.  status=", status
		raise CaChannelException, status
		return
	cadict[name][1] = 0
	try:
		cadict[name][0].array_put_callback(value,None,None,waitCB,name)
	except CaChannelException, status:
		print "caputw: CaChannel exception, status=", status
		cadict[name][1] = 1
		return
	#ca.flush_io()
	while not cadict[name][1]:
		#print "waiting for ", name
		time.sleep(0.1)
#		ca.pend_io(0.1)
		ca.poll()

def camonitor(name, function, user_args):
	"""usage: camonitor("xxx:m1.VAL", python_function, user_args)"""
	try:
		checkName(name)
	except CaChannelException, status:
		print "camonitor: CaChannel exception, status=", status
		raise CaChannelException, status
		return

	try:
		cadict[name][0].add_masked_array_event(
			None,None,ca.DBE_VALUE, function, user_args)
	except CaChannelException, status:
		print "camonitor: CaChannel exception, status=", status
		return

def caunmonitor(name):
	"""usage: caunmonitor("xxx:m1.VAL")"""
	if not cadict.has_key(name):
		return
	try:
		cadict[name][0].clear_event()
	except CaChannelException, status:
		print "caunmonitor: CaChannel exception, status=", status
		return

def test_monitor_function(epics_args, user_args):
	print 'test_monitor_function:'
	print "...epics_args ", repr(epics_args)
	print "...user_args ", repr(user_args)
