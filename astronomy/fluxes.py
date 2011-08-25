"""
Functions related astronomical fluxes.

:requires: NumPy
:requires: SciPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import numpy as np
import scipy.integrate as integrate
import scipy.interpolate as i

def convolveSpectrum(wave, flux, wave2, throughput):
    """
    Convolve a spectrum through a filter to obtain flux.
    Returns also the effective wavelength of the flux distribution.

    :note: if the spectrum is shorter in wavelength than the filter transmittance
           curve, then sets the outside range values to zeros

    :param: wave, wavelength of the spectrum
    :param: flux, flux of the spectrum
    :param: wave2, wavelgnth of the filter
    :param: throughput, normalized throughput of the filter
    """
    min = np.min(wave2)
    max = np.max(wave2)

    msk = np.where((wave >= min) & (wave <= max))
    if len(msk[0]) <= 1:
        print 'ERROR - supplied wavelengths outside of filter response curve'

    #generate the wavelength grid
    wgrid = np.append(wave2, wave[msk])
    #sort and find uniques
    wgrid.sort()
    wgrid = np.unique(wgrid)

    #interpolate on the new grid
    f = i.interp1d(wave, flux, bounds_error=False, fill_value=0.0)
    fluxg = f(wgrid)
    f = i.interp1d(wave2, throughput, bounds_error=False, fill_value=0.0)
    frelg = f(wgrid)

    #calculate the effective flux through the filter
    feff = fluxg * frelg
    #effective wavelength
    wff = integrate.trapz(wgrid * feff) / integrate.trapz(feff)
    #integrate the total flux
    flux = integrate.trapz(feff, wgrid) / integrate.trapz(frelg, wgrid)

    output = {'effectiveFlux': feff,
              'effectiveWave': wff,
              'flux': flux,
              'wave': wgrid}
    return output
