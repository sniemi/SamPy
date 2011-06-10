import yt.analysis_modules.halo_mass_function.api as HMF

def calculateAnalyticalDMMFs(redshift,
                             h_100=0.7,
                             Omega_0=0.27,
                             #Omega_b = 0.02265/(0.7*0.7),
                             Omega_b=0.02265,
                             lambdaL=0.73,
                             n=0.95,
                             sigma8=0.82,
                             write=True):
    '''
    Calculates three analytical dark matter halo mass functions
    '''
    hmfPS = HMF.HaloMassFcn(None, omega_matter0=Omega_0, omega_lambda0=lambdaL,
                            omega_baryon0=Omega_b, hubble0=h_100, this_redshift=z,
                            log_mass_min=7., log_mass_max=16., sigma8input=sigma8,
                            primordial_index=n, fitting_function=1)

    hmfST = HMF.HaloMassFcn(None, omega_matter0=Omega_0, omega_lambda0=lambdaL,
                            omega_baryon0=Omega_b, hubble0=h_100, this_redshift=z,
                            log_mass_min=7., log_mass_max=16., sigma8input=sigma8,
                            primordial_index=n, fitting_function=3)

    hmfWa = HMF.HaloMassFcn(None, omega_matter0=Omega_0, omega_lambda0=lambdaL,
                            omega_baryon0=Omega_b, hubble0=h_100, this_redshift=z,
                            log_mass_min=7., log_mass_max=16., sigma8input=sigma8,
                            primordial_index=n, fitting_function=4)

    string = str(round(redshift, 2)).replace('.', '_')

    if write:
        hmfPS.write_out(prefix="hmf-press-schechter_" + string, fit=True, haloes=False)
        hmfST.write_out(prefix="hmf-sheth-tormen_" + string, fit=True, haloes=False)
        hmfWa.write_out(prefix="hmf-warren_" + string, fit=True, haloes=False)
    else:
        return hmfPS, hmfST, hmfWa

if __name__ == '__main__':
#    times = {0.4984: 1.0064,
#             0.2464: 3.0584,
#             0.1983: 4.0429,
#             0.1323: 6.5586,
#             0.1084: 8.2251,
#             0.1623: 5.1614,
#             0.3303: 2.0276,
#             0.9943: 0.0057}
    times = {0.9434: 0.059995760017,
             0.9073: 0.102171277417,
             0.8324: 0.201345506968,
             0.7663: 0.304971943103,
             0.7124: 0.403705783268,
             0.6643: 0.505343971097,
             0.6223: 0.606941989394,
             0.5864: 0.705320600273,
             0.5564: 0.797268152408,
             0.5283: 0.892863903085,
             0.4984: 1.00642054575}

    for z in times.itervalues():
        calculateAnalyticalDMMFs(z)
    
