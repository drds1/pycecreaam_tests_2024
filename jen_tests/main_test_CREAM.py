import numpy as np
import matplotlib.pyplot as plt
import pycecream
import time
import os
import sys
import multiprocessing
import pandas as pd
import corner 


project_folder='test_fit'
refit = True

def read_and_proces_lightcurves(file,nwavelengths=6):
    lc_raw= np.loadtxt(file).reshape(-1,nwavelengths+1)
    n_epochs = int(lc_raw[:,0].max()+1)
    n_samples = len(lc_raw)
    n_lightcurves = int(n_samples/n_epochs)
    print('reading file {}'.format(file))
    print("found {} sets of light curves with {} epochs each".format(n_lightcurves,n_epochs))
    return [lc_raw[i*n_epochs:(i+1)*n_epochs] for i in range(n_lightcurves)]
    


if refit:
    os.system('rm -rf {}'.format(project_folder))
    #theta_true = np.loadtxt(dir_output+'../data/test_SBI_theta_1000.txt')

    ## read in test data
    
    lc_groups = read_and_proces_lightcurves('test_SBI_x_5.txt')
    lc = lc_groups[0]

    
    wavelength = [3751, 4740, 6172, 7500, 8678, 9711]
    ## set up pycecream
    #instantiate a pycecream object

    ncores = 1
    start_time = time.time()

    start_time_single = time.time()
    a = pycecream.pycecream()
    a.fortran_caller = 'gfortran'
    a.project_folder = project_folder
    ## remove later: for quick debugging
    a.high_frequency = 0.2
    a.redshift = 0.0
    a.bh_mass = 1e8
    a.bh_efficieny = 0.1
    a.N_iterations = 50
    a.lag_lims = [-50.0,50.0] #the window for the response function
    #fitted parameters
    a.p_inclination = 0.
    a.p_inclination_step = 0.1
    a.p_accretion_rate = 1.
    a.p_accretion_rate_step = 0.1
    a.p_viscous_slope = 0.75
    a.p_viscous_slope_step = 0.1
    a.p_extra_variance_step = 0.1
    ## start LC

    n_epochs = len(lc)
    n_wavelengths = len(lc[0,1:])
    assert(n_wavelengths==len(wavelength))
    for j in range(n_wavelengths):
        lc_err = np.median(lc[:,j+1])/100 ## set the uncertainity to 5%
        lc_arr = np.array((lc[:,0],lc[:,j+1],np.zeros(n_epochs)+lc_err)).T
        print(lc_arr.shape)
        a.add_lc(lc_arr,name='continuum'+str(wavelength[j]),wavelength=wavelength[j],kind='continuum')
    a.run(ncores = ncores)

    print('running {} MCMC steps'.format(a.N_iterations))
    ## get results
    output_chains = a.get_MCMC_chains(location = None)
    output_lightcurves = a.get_light_curve_fits(location = None)
    output_chains.to_csv(os.path.join(project_folder,'chains.txt'))


output_chains = pd.read_csv(os.path.join(project_folder,'chains.txt'))
## plot trace plot
disk_params = ['disk Mdot', 'disk cos i','disk Tr_alpha']
fig, ax = plt.subplots(len(disk_params),figsize=(10,2*len(disk_params)))
for j in range(len(disk_params)):
    if disk_params[j] == 'disk Mdot':
        ax[j].plot(np.array(np.log10(output_chains[disk_params[j]])).reshape(ncores,int(sys.argv[2])).T,alpha=0.3)
        ax[j].set_ylim([-2,4])
    else:
        ax[j].plot(np.array(output_chains[disk_params[j]]).reshape(ncores,int(sys.argv[2])).T,alpha=0.3)
        #ax[j].set_ylim([0,1])
ax[j].set_ylabel(disk_params[j])
plt.savefig(os.path.join(project_folder,'trace.pdf'))
## plot corner plot
mdot = np.array(output_chains[disk_params[0]]).reshape(ncores,int(sys.argv[2])).T[int(int(sys.argv[2])/2):,:].flatten()
cosi = np.array(output_chains[disk_params[1]]).reshape(ncores,int(sys.argv[2])).T[int(int(sys.argv[2])/2):,:].flatten()
alpha = np.array(output_chains[disk_params[2]]).reshape(ncores,int(sys.argv[2])).T[int(int(sys.argv[2])/2):,:].flatten()
samples = np.vstack([np.log10(mdot), np.arccos(cosi),alpha]).T
figure = corner.corner(samples,labels=[r'Mdot',r'$i$',r'\alpha'],\
                   quantiles=[0.16, 0.5, 0.84],\
                    #truths=[theta_true[i,2],theta_true[i,0],0.75],\
                   range=[[-2,2],[0,np.pi*2],0.99])
#plt.suptitle(str(theta_true[i,:]))
plt.savefig(os.path.join(project_folder,'corner.pdf'))
