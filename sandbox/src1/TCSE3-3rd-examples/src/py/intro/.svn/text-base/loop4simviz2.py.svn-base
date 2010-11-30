#!/usr/bin/env python
"""
As loop4simviz1.py, but here we call simviz2.py, make movies,
and also allow any simviz2.py option to be varied in a loop.
"""
import sys, os, commands
usage = 'Usage: %s parameter min max increment '\
        '[ simviz2.py options ]' % sys.argv[0]
try:
    option_name = sys.argv[1]
    min = float(sys.argv[2])
    max = float(sys.argv[3])
    incr = float(sys.argv[4])
except:
    print usage;  sys.exit(1)

simviz2_options = ' '.join(sys.argv[5:])

html = open('tmp_%s_runs.html' % option_name, 'w')
html.write('<HTML><BODY BGCOLOR="white">\n')
psfiles = []    # plot files in PostScript format
pngfiles = []   # plot files in PNG format

value = min
while value <= max:
    case = 'tmp_%s_%g' % (option_name, value)
    cmd = 'python simviz2.py %s -%s %g -case %s' % \
          (simviz2_options, option_name, value, case)
    print 'running', cmd
    failure, output = commands.getstatusoutput(cmd)
    psfile = os.path.join(case,case+'.ps')
    pngfile = os.path.join(case,case+'.png')
    html.write('<H1>%s=%g</H1> <IMG SRC="%s">\n' \
               % (option_name, value, pngfile))
    psfiles.append(psfile)
    pngfiles.append(pngfile)
    value += incr
cmd = 'convert -delay 50 -loop 1000 %s tmp_%s.gif' \
      % (' '.join(pngfiles), option_name)
print 'converting PNG files to animated GIF:\n', cmd
failure, output = commands.getstatusoutput(cmd)
html.write('<H1>Movie</H1> <IMG SRC="tmp_%s.gif">\n' % \
           option_name)
cmd = 'ps2mpeg.py %s' % ' '.join(psfiles)
print 'converting PostScript files to an MPEG movie:\n', cmd
failure, output = commands.getstatusoutput(cmd)
os.rename('movie.mpeg', 'tmp_%s.mpeg' % option_name)
html.write('<H1><A HREF="tmp_%s.mpeg">MPEG Movie</A></H1>\n' \
           % option_name)
html.write('</BODY></HTML>\n')
html.close()
cmd = 'epsmerge -o tmp_%s_runs.ps -x 2 -y 3 -par %s' \
      % (option_name, ' '.join(psfiles))
print cmd
failure, output = commands.getstatusoutput(cmd)
failure, output = commands.getstatusoutput(\
    'ps2pdf tmp_%s_runs.ps' % option_name)
