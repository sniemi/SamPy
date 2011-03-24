from yt.mods import *
import yt.analysis_modules.halo_mass_function.api as HMF

def calculate_analytical_dm_mfs(redshift,
                                h_100 = 0.7,
                                Omega_0 = 0.27,
                                #Omega_b = 0.02265/(0.7*0.7),
                                Omega_b = 0.02265,
                                lambdaL = 0.73,
                                n = 0.95,
                                sigma8 = 0.82):
    
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

    hmfPS.write_out(prefix="hmf-press-schechter_" + string, fit=True, haloes=False)
    hmfST.write_out(prefix="hmf-sheth-tormen_" + string , fit=True, haloes=False)
    hmfWa.write_out(prefix="hmf-warren_" + string, fit=True, haloes=False)

if __name__ == '__main__':

    times = {0.4984 : 1.0064,
             0.2464 : 3.0584,
             0.1983 : 4.0429,
             0.1323 : 6.5586,
             0.1084 : 8.2251,
             0.1623 : 5.1614,
             0.3303 : 2.0276,
             0.9943 : 0.0057}

    for z in times.itervalues():
        calculate_analytical_dm_mfs(z)
    
