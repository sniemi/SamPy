"""
Power spectrum related functions.
"""
import numpy as np

def growth_func(z, Om, Ol, Ok=0):
    """
    The growth function.

    .. math::

       P(k,z) = 2*\\pi^{2} * norm_z0 * pfunc * growth_func(z)^{2}
    """
    D0 = 2.5*Om / (Om**(4./7) - Ol + (1 + 0.5*Om)*(1 + Ol/70.))
    
    zp1 = 1 + z
    zp1_2 = zp1**2
    zp1_3 = zp1**3
    temp =  Ol + Ok*zp1_2 + Om*zp1_3
    omegaz = Om * zp1_3 / temp
    omegalz = Ol / temp

    temp = omegaz**(4./7) - omegalz + (1 + 0.5*omegaz)*(1 + omegalz/70.)
    Dz = 1./zp1 * 2.5 * omegaz / temp
    return Dz / D0

def cdm_corr_z2p5(rvals, fudge=4.9, sigma8 = 0.809, omegam = 0.272,
                  omegal = 0.728):
    """
    Return the dark matter correlation function at separations given by rvals at z=2.5

    rvals in h^-1 Mpc
    """
    rvals = np.asarray(rvals)

    assert rvals.max() < 180
    assert rvals.min() > 1e-3
    import astro
    prefix = astro.__path__[0]
    r,xi0 = np.loadtxt(prefix + '/data/slosar09_corr.txt', unpack=1)
    xivals = np.interp(rvals, r, xi0)

    # just normalisation, don't worry too much about it
    norm = (sigma8 / 0.00039453207450944561)**2
    xi1 = 1. / (2*np.pi)**3 * xivals * norm * growth_func(2.5, omegam, omegal)

    return fudge * xi1

def powerspec(y, dt, fig=None):
    """ Find the power spectrum using an FFT. 
    
    The samples y must be equally spaced with spacing dt. It is
    assumed y is real.

    return the coords in fourier transform space (e.g. 1/t) and the power
    spectrum values, 2 * abs(fft)**2
    """
    fft = np.fft.fft(y)
    nu = np.fft.fftfreq(len(y), dt)
    pspec = (2*np.abs(fft)**2)[:len(y)//2 + 1]
    pnu = np.abs(nu)[:len(y)//2 + 1]
    if fig is not None:
        import pylab as pl
        ax = fig.add_subplot(211)
        ax.plot(np.arange(len(y))*dt, y)
        ax.set_ylabel('$y$')
        ax.set_xlabel('T')
        ax = fig.add_subplot(212)

        ax.semilogy(pnu, pspec)
        ax.set_ylabel(r'$2*abs(fft(y))^2$')
        ax.set_xlabel('f = 1/T')

    return pnu, pspec
