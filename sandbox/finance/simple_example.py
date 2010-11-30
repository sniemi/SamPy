# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 09:26:40 2010

@author: -
"""

import matplotlib.finance as f
import numpy as N
import pylab as P

sp = f.quotes_historical_yahoo('^GSPC', (1,1,2001), (1,1,2010), asobject=True, adjusted=True)
returns = (sp.open[1:] - sp.open[:-1])/sp.open[1:]
[n,bins,patches] = P.hist(returns, 100)
mu = N.mean(returns)
sigma = N.std(returns)
x = P.normpdf(bins, mu, sigma)
P.plot(bins, x, color='red', lw=2)

print returns