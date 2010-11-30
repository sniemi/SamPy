# Miscellanous methods used in postprocessing tasks

def getTCSField():

    """ Return current Telescope field angle """

    import MySQLdb
    cnx = MySQLdb.connect(host='lili',user='select_user',passwd='select_pass',db='Operations')
    cursor = cnx.cursor()
    cursor.execute('SELECT FieldRotationDeg FROM TCSStatusNow')
    cnx.commit()
    a = cursor.fetchone()
    cnx.close()
    return float(a[0])


def getCurrentDimm():

    """ Return current DIMM measurement """

    import MySQLdb
    cnx = MySQLdb.connect(host='eeva',user='select_user',passwd='select_pass',db='SiteData')
    cursor = cnx.cursor()
    cursor.execute("""SELECT AVG((fwhmhorl+fwhmvert+fwhmverl)/3) FROM RoboDimmING
                      WHERE DateTimeUT 
		      BETWEEN DATE_SUB(NOW(), INTERVAL 900 SECOND) AND NOW()""")
    cnx.commit()
    a = cursor.fetchone()
    cnx.close()
    try:
      return '%.2f' % float(a[0])
    except TypeError:
      return 'n/a'

def getLatestImage(dir,prefix):

  """ Return image with most recent content modification """

  import os  
  filelist = [os.path.join(dir,x) for x in os.listdir(dir) if x[:2] == prefix and x[-5:] == '.fits']
  lastfile = sorted(filelist, cmp=lambda x,y: cmp(os.stat(x)[-2], os.stat(y)[-2]))[-1] 
  return os.path.split(lastfile)[1]


def writeLog(path,image,str):
  import time
  timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
  debugfile = open(path + '/debug.log', 'a')
  debugfile.write(timestamp + ' ' + image + ':' + str)
  debugfile.write('\n')
  debugfile.close()

def writeTalker(ident,msg):

  """ Write a message in LOG_LOCAL0 facility for Talker window """

  import syslog
  syslog.openlog(ident, syslog.LOG_CONS, syslog.LOG_LOCAL0)
  syslog.syslog(syslog.LOG_DEBUG, msg)
  syslog.closelog()	


def flattenImageALFOSC(fn,outfn):

  """ Flatten all ALFOSC image extentions """

  import numpy
  import pyfits

  f = pyfits.open(fn)
  h1 = f[1].header
  d1 = f[1].data
  d2 = f[2].data
  f.close()

  d = numpy.hstack((d1,d2))

  hdu = pyfits.PrimaryHDU(d)
  n = pyfits.HDUList([hdu])
  n[0].header.update('AMPLMODE','A')
  n[0].header.update('CTYPE1', h1['CTYPE1'])
  n[0].header.update('CTYPE2', h1['CTYPE2'])
  n[0].header.update('CRVAL1', h1['CRVAL1'])
  n[0].header.update('CRVAL2', h1['CRVAL2'])
  n[0].header.update('CUNIT1', h1['CUNIT1'])
  n[0].header.update('CUNIT2', h1['CUNIT2'])
  n[0].header.update('CRPIX1', h1['CRPIX1'])
  n[0].header.update('CRPIX2', h1['CRPIX2'])
  n[0].header.update('CD1_1', h1['CD1_1'])
  n[0].header.update('CD1_2', h1['CD1_2'])
  n[0].header.update('CD2_1', h1['CD2_1'])
  n[0].header.update('CD2_1', h1['CD2_1'])

  n.writeto(outfn)


def flattenImageMOSCA(fn,outfn):

  """ Flatten all MOSCA image extentions """

  import numpy
  import pyfits

  f = pyfits.open(fn)
  h1 = f[1].header
  d1 = f[1].data
  d2 = f[2].data
  d2 = f[3].data
  d2 = f[4].data

  f.close()

  d = numpy.hstack((d1,d2))

  hdu = pyfits.PrimaryHDU(d)
  n = pyfits.HDUList([hdu])
  n[0].header.update('AMPLMODE','A')
  n[0].header.update('CTYPE1', h1['CTYPE1'])
  n[0].header.update('CTYPE2', h1['CTYPE2'])
  n[0].header.update('CRVAL1', h1['CRVAL1'])
  n[0].header.update('CRVAL2', h1['CRVAL2'])
  n[0].header.update('CUNIT1', h1['CUNIT1'])
  n[0].header.update('CUNIT2', h1['CUNIT2'])
  n[0].header.update('CRPIX1', h1['CRPIX1'])
  n[0].header.update('CRPIX2', h1['CRPIX2'])
  n[0].header.update('CD1_1', h1['CD1_1'])
  n[0].header.update('CD1_2', h1['CD1_2'])
  n[0].header.update('CD2_1', h1['CD2_1'])
  n[0].header.update('CD2_1', h1['CD2_1'])

  n.writeto(outfn)