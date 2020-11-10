import openmc
import os
from scipy.stats import norm
import numpy as np
import h5py
import warnings
warnings.simplefilter("ignore")

statepointdir = 'statepoints-endfFNG'

tallyId = 3

index = 1
Nfiles = 500


os.system(f"cp {statepointdir}/statepoint.{index}.h5 ./statepoint.mean.h5")
os.system(f"cp {statepointdir}/statepoint.{index}.h5 ./statepoint.upper.h5")
os.system(f"cp {statepointdir}/statepoint.{index}.h5 ./statepoint.lower.h5")
sp = openmc.StatePoint(f'{statepointdir}/statepoint.{index}.h5')

Tal = sp.get_tally(id = tallyId)

allMean = Tal.mean
stds = Tal.std_dev
upper95 = norm(allMean,stds).ppf(0.95)
lower95 = norm(allMean,stds).ppf(0.05)

upper95[np.isnan(upper95)] = allMean[np.isnan(upper95)]
lower95[np.isnan(lower95)] = allMean[np.isnan(lower95)]


for i in range(2, Nfiles+1):
    sp = openmc.StatePoint(f'{statepointdir}/statepoint.{i}.h5')
    Tal = sp.get_tally(id = tallyId)

    thisMean = Tal.mean
    thisStds = Tal.std_dev
    thisUpper = norm(thisMean,thisStds).ppf(0.95)
    thisLower = norm(thisMean,thisStds).ppf(0.05)

    thisUpper[np.isnan(thisUpper)] = thisMean[np.isnan(thisUpper)]
    thisLower[np.isnan(thisLower)] = thisMean[np.isnan(thisLower)]

    allMean = allMean + thisMean
    upper95 = np.maximum(upper95, thisUpper)
    lower95 = np.minimum(lower95, thisLower)
    print(f"Done with {i}")

allMean = allMean/Nfiles

h1 = h5py.File('statepoint.mean.h5', 'a')
h2 = h5py.File('statepoint.upper.h5', 'a')
h3 = h5py.File('statepoint.lower.h5', 'a')

# Assign means
means = h1['tallies/tally 3/results'][:]
means[:,0,0] = allMean.reshape(means[:,0,0].shape)
h1['tallies/tally 3/results'][:] = means
h1.close()

# Assign uppers 
these = h2['tallies/tally 3/results'][:]
these[:,0,0] = upper95.reshape(these[:,0,0].shape)
h2['tallies/tally 3/results'][:] = these
h2.close()

# Assign lowers
those = h3['tallies/tally 3/results'][:]
those[:,0,0] = lower95.reshape(those[:,0,0].shape)
h3['tallies/tally 3/results'][:] = those
h3.close()