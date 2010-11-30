def Luminosity(abs_mag): return 10.0**((4.85-abs_mag)/2.5)

import math
print -19.6 - 5.*math.log10(0.73)
print 'Luminosity of a -20 mag galaxy is about %eL_sun' % Luminosity(-20.)
