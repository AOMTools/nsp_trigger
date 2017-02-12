"""
Small procedural functions to estimate the parameters of lorentzian
"""

import numpy as np
from lmfit import Model

# Define the fitting function
def lorentzian(x, amp, width, mean):
    top = amp * (width**2 / 4)
    bottom = (x - mean)**2 + (width/2)**2
    y = top/bottom
    return y

def lorentz_fitting(data, init, no_trials = 1):
    # Declare model and initializing data
    print('Fitting now...')
    lzmod = Model(lorentzian)
    xdata = data[:,0]
    ydata = data[:,1]
    ystderr = data[:,2] / np.sqrt(no_trials)

    # Set parameter hints
    lzmod.set_param_hint('amp', value = init[0], min=0)
    lzmod.set_param_hint('width', value = init[1], min=0)
    lzmod.set_param_hint('mean', value = init[2])
    pars = lzmod.make_params()

    fit = lzmod.fit(ydata, pars, x=xdata, weights=1/ystderr, verbose=False)
    #print fit.fit_report()

    amp_est = fit.params['amp'].value
    amp_std = fit.params['amp'].stderr
    width_est = fit.params['width'].value
    width_std = fit.params['width'].stderr
    mean_est = fit.params['mean'].value
    mean_std = fit.params['mean'].stderr
    redchi = fit.redchi

    # Return back the result list with the following order:
    result_list = [amp_est, amp_std, width_est, width_std, mean_est, mean_std, redchi]

    return result_list

if __name__ == '__main__':
    data = np.loadtxt('test.dat')
    init = np.array([1000, 100, 400])
    res = lorentz_fitting(data, init, 10)
    print res[4]
