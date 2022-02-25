#!/usr/bin/env python3
import pathos.multiprocessing as mp
import h5py
import os
from shutil import copyfile
import shutil
import copy
from pathlib import Path
import numpy as np

import openmc

#import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt

import openpyxl
import pandas as pd

from scipy.stats import norm
import argparse

import warnings

warnings.simplefilter("ignore")



description = """
    Plots a number of random nuclides from an openmc tally
"""


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


parser = argparse.ArgumentParser(
    description=description, formatter_class=CustomFormatter)

parser.add_argument("-d", "--destination", default=None, 
                    help="Directory of statepoint files")
parser.add_argument("-n", "--Nsamples", default=None, 
                    help="Number of realisations to plot")
parser.add_argument("-t", "--tally", default=None, 
                    help="Tally ID to plot")
parser.add_argument("-nm", "--name", default=None, 
                    help="name of the plot")
parser.add_argument("-s", "--N_nodes", default=None, 
                    help="name of the plot")

args = parser.parse_args()

statePointDir = args.destination
Nsamps = args.Nsamples
TallyId = int(args.tally)
name = args.name
n_cores = int(args.N_nodes)

script_dir = Path.cwd()

if statePointDir == None:
    statePointDir = script_dir
else:
    statePointDir = Path(statePointDir).resolve()

if Nsamps == None:
    files = os.listdir(statePointDir)
    Nsamps = sum([f.startswith("statepoint") for f in files])

if name == None:
    name = f"UQ_sim_tal_{TallyId}"
else:
    name = f"{name}_tal_{TallyId}"

###
#   Plot parameters
###

fontsize = 22


##
#   Plotting stuff
##

index = 1
sp1 = openmc.StatePoint(f'{statePointDir}/statepoint.{index}.h5')

Tal = sp1.get_tally(id = TallyId).get_pandas_dataframe()

enHi = Tal['energy high [eV]']
enLo = Tal['energy low [eV]']

def get_range_and_mean(indecies, TallyId, statePointDir):
    index = indecies[0]
    sp1 = openmc.StatePoint(f'{statePointDir}/statepoint.{index}.h5')

    Tal = sp1.get_tally(id = TallyId).get_pandas_dataframe()

    means = np.array(Tal['mean'])

    stds = np.array(Tal['std. dev.'])

    Upper = norm(means,stds).ppf(0.95)
    Lower = norm(means,stds).ppf(0.05)

    Upper[np.isnan(Upper)] = means[np.isnan(Upper)]
    Lower[np.isnan(Lower)] = means[np.isnan(Lower)]

    for i in indecies[1:]:
        sp = openmc.StatePoint(f'{statePointDir}/statepoint.{i}.h5')
        Tal = sp.get_tally(id = TallyId).get_pandas_dataframe()
        thisMean = np.array(Tal['mean'])
        thisStd = np.array(Tal['std. dev.'])
        thisUpper = norm(thisMean,thisStd).ppf(0.95)
        thisLower = norm(thisMean,stds).ppf(0.05)

        thisUpper[np.isnan(thisUpper)] = thisMean[np.isnan(thisUpper)]
        thisLower[np.isnan(thisLower)] = thisMean[np.isnan(thisLower)]

        means = means + thisMean
        Upper = np.maximum(Upper, thisUpper)
        Lower = np.minimum(Lower, thisLower)

    means = means/Nsamps

    return means, Lower, Upper


N_chunks = int(Nsamps/n_cores)

inds = list(range(1,Nsamps+1))
chunks = [inds[x:x+N_chunks] for x in range(0, len(inds), N_chunks)]


def parallel_function(ind):
    return get_range_and_mean(ind, TallyId, statePointDir)

Pool = mp.Pool(n_cores)

results = Pool.map(parallel_function, chunks)

means1 = results[0][0]
Lower1 = results[0][1]
Upper1 = results[0][2]

for i in range(1,len(results)):

    means1 = means1 + results[i][0]
    Lower1 = np.minimum(Lower1, results[i][1])
    Upper1 = np.maximum(Upper1, results[i][1])

means1 = means1 / len(results)
Lower1 = np.maximum(Lower1, 0)

fig = plt.figure(figsize=(19, 15))


plt.step(enHi, means1,color = "green", alpha = 1,linewidth = 2, where = "post")
plt.step(enHi, Upper1,color = "red", alpha = 1,linewidth = 1, where = "post")
plt.step(enHi, Lower1,color = "red", alpha = 1,linewidth = 1, where = "post")
plt.fill_between(enHi, Lower1, Upper1,alpha=0.3, color ="red", step = "post" , label='95%')


leg = plt.legend(fontsize=fontsize)

plt.yscale("log")
plt.xscale("log")
plt.xlim([10**(-5), 2*10**7])
plt.ylim([10**(-6), 1.5])

plt.xticks(fontsize=fontsize); plt.yticks(fontsize=fontsize)
plt.xlabel("Energy [eV]", fontsize=fontsize)

plt.ylabel("Neutron flux", fontsize=fontsize)

print("saving...")
plt.savefig(f"{name}.png", dpi=800)
plt.clf()

