import pycecream
import pycecream.modules.myfake as mf
import matplotlib.pylab as plt
import os


'''
mf.myfake arguments are

wavelengths: enter the wavelengths (-1 indicates an emission line light curve modelled with a top-hat response),

snr: set the signal-to-noise relative to light curve rms

cadence:set the mean cadence

top hat centroid: set the centroid for the top-hat (I think thats what this does but the line lag 
thing is still newish so Im used to just making continuum light curve)
'''


synthetic_data = mf.myfake(
    [4000.0,5000.0,6000.0,7000.0,-1.0,-1.0],
    [50.0,50.0,10.0,50.0,50,10.],
    [1.0,1.0,2.0,1.0,1.0,3.0],
    thcent = 20.0
)

'''This recovers the synthetic data'''
dat = synthetic_data['echo light curves']




#instantiate a pycecream object
a = pycecream.pycecream()

'''
If you use a fortran compiler other than gfortran please indicate here.
I just re-enter gfortran here for demonstration purposes even though 
this is unecassary as gfortran is the default argument.
'''
a.fortran_caller = 'gfortran'



'''Choose an output directory in which to save the results. 
This will be a new directory that you have not previously created (pycecream will make it automatically).

NOTE: Each new cream simulation must have a new name for "output_directory argument below 
otherwise an excpetion is raised. This is to prevent accidentally overwriting previous simulations. 
I might change this in a future version 
'''
a.project_folder = 'fit_synthetic_lightcurves'



'''
Add the light curves to be modeled. Inputs should be a 3 column numpy
 array of `time`, `flux`, `error`. 
In this case we are using the "dat" output 
from the synthetic data above.
'''
a.add_lc(dat[0], kind='continuum', wavelength =4000, name = 'continuum 4000')
#a.add_lc(dat[1], kind='continuum', wavelength =5000, name = 'continuum 5000')
#a.add_lc(dat[2], kind='continuum', wavelength =6000, name = 'continuum 6000')
#a.add_lc(dat[3], kind='continuum', wavelength =7000, name = 'continuum 7000')

#If adding a line light curve, must indicate using the "kind" argument
a.add_lc(dat[4],name='test line 1',kind='line',expand_errors=['var','multiplicative'])

#If we want the same line response function model, set "share_previous_lag"=True
a.add_lc(dat[4],name='test line 1 (shared)',kind='line',expand_errors=['var','multiplicative'],share_previous_lag=True)



'''
specify the numnber of MCMC iterations. Normally at least several thousand are necessary but shorter numbers 
can be used just to check everything is working is done here.
'''
a.N_iterations=100

'''
specify the step sizes for the fit parameters. 
Here we are setting the accretion rate step size to vary by ~ 0.1 solar masses per year.
'''
a.p_accretion_rate_step = 0.1

'''
Check the input settings are ok prior to running
'''
print(a.lightcurve_input_params)

'''
RUN! specify ncores (default = 1) to parallelise with 1 chain per core
'''
a.run()


chains = a.get_MCMC_chains()


a.plot_results()