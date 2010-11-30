from pymc import DiscreteUniform, Exponential, deterministic, Poisson, Uniform
import numpy as np

disasters_array =   np.array([ 4, 5, 4, 0, 1, 4, 3, 4, 0, 6, 3, 3, 4, 0, 2, 6,
                   3, 3, 5, 4, 5, 3, 1, 4, 4, 1, 5, 5, 3, 4, 2, 5,
                   2, 2, 3, 4, 2, 1, 3, 2, 2, 1, 1, 1, 1, 3, 0, 0,
                   1, 0, 1, 1, 0, 0, 3, 1, 0, 3, 2, 2, 0, 1, 1, 1,
                   0, 1, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 1, 0, 2,
                   3, 3, 1, 1, 2, 1, 1, 1, 1, 2, 4, 2, 0, 0, 1, 4,
                   0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1])

s = DiscreteUniform('s', lower=0, upper=110, doc='Switchpoint[year]')

e = Exponential('e', beta=1)
l = Exponential('l', beta=1)

@deterministic(plot=False)
def r(s=s, e=e, l=l):
    """ Concatenate Poisson means """
    out = np.empty(len(disasters_array))
    out[:s] = e
    out[s:] = l
    return out

D = Poisson('D', mu=r, value=disasters_array, observed=True)


#missing data

x  = N.array([ 4, 5, 4, 0, 1, 4, 3, 4, 0, 6, 3, 3, 4, 0, 2, 6,
3, 3, 5, 4, 5, 3, 1, 4, 4, 1, 5, 5, 3, 4, 2, 5,
2, 2, 3, 4, 2, 1, 3, -999, 2, 1, 1, 1, 1, 3, 0, 0,
1, 0, 1, 1, 0, 0, 3, 1, 0, 3, 2, 2, 0, 1, 1, 1,
0, 1, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 1, 0, 2,
3, 3, 1, -999, 2, 1, 1, 1, 1, 2, 4, 2, 0, 0, 1, 4,
0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1])

masked_data = N.ma.masked_equal(x, value=-999)

# Switchpoint
s = DiscreteUniform('s', lower=0, upper=110)
# Early mean
e = Exponential('e', beta=1)
# Late mean
l = Exponential('l', beta=1)

@deterministic(plot=False)
def r(s=s, e=e, l=l):
    """Allocate appropriate mean to time series"""
    out = np.empty(len(disasters_array))
    # Early mean prior to switchpoint
    out[:s] = e
    # Late mean following switchpoint
    out[s:] = l
    return out

D = ImputeMissing('D', Poisson, masked_data, mu=r)

