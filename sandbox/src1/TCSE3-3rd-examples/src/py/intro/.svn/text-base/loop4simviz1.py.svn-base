#!/usr/bin/env python
"""calls simviz1.py with different m values (in a loop)"""
import sys, os, commands
usage = 'Usage: %s m_min m_max m_increment [ simviz1.py options ]' \
        % sys.argv[0]

try:
    m_min = float(sys.argv[1])
    m_max = float(sys.argv[2])
    dm    = float(sys.argv[3])
except IndexError:
    print usage;  sys.exit(1)

simviz1_options = ' '.join(sys.argv[4:])

html = open('tmp_mruns.html', 'w')
html.write('<HTML><BODY BGCOLOR="white">\n')
psfiles = []  # plot files in PostScript format

m = m_min
while m <= m_max:
    case = 'tmp_m_%g' % m
    cmd = 'python simviz1.py %s -m %g -case %s' % \
          (simviz1_options, m, case)
    print 'running', cmd
    failure, output = commands.getstatusoutput(cmd)
    html.write('<H1>m=%g</H1> <IMG SRC="%s">\n' \
               % (m,os.path.join(case,case+'.png')))
    psfiles.append(os.path.join(case,case+'.ps'))
    m += dm
html.write('</BODY></HTML>\n')
pscmd = 'epsmerge -o tmp_mruns.ps -x 2 -y 3 -par ' + \
        ' '.join(psfiles)
failure, output = commands.getstatusoutput(pscmd)
