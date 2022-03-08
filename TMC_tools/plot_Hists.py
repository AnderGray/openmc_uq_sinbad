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
TallyId = int(args.tally)
name = args.name
n_cores = int(args.N_nodes)

script_dir = Path.cwd()

if statePointDir == None:
    statePointDir = script_dir
else:
    statePointDir = Path(statePointDir).resolve()

if args.Nsamples == None:
    files = os.listdir(statePointDir)
    Nsamps = sum([f.startswith("statepoint") for f in files])
else:
    Nsamps = int(args.Nsamples)

if name == None:
    name = f"UQ_sim_tal_{TallyId}"
else:
    name = f"{name}_tal_{TallyId}"

###
#   Plot parameters
###

fontsize = 22
labelsize = 18


##
#   Plotting stuff
##

index = 1
sp1 = openmc.StatePoint(f'{statePointDir}/statepoint.{index}.h5')

Tal = sp1.get_tally(id = TallyId).get_pandas_dataframe()

enHi = Tal['energy high [eV]']
enLo = Tal['energy low [eV]']


def get_samples(indecies, TallyId, statePointDir):
    index = indecies[0]
    sp1 = openmc.StatePoint(f'{statePointDir}/statepoint.{index}.h5')

    Tal = sp1.get_tally(id = TallyId).get_pandas_dataframe()

    means = np.array(Tal['mean'])


    for i in indecies[1:]:
        sp = openmc.StatePoint(f'{statePointDir}/statepoint.{i}.h5')
        Tal = sp.get_tally(id = TallyId).get_pandas_dataframe()
        thisMean = np.array(Tal['mean'])

        means = np.vstack((means,thisMean))

    return means


def plot_this(i, res):
    
    samps = res[:,i]
    if enLo[i] >= 10**6:
        enLo_this = enLo[i]*10**(-6)
        enHi_this = enHi[i]*10**(-6)
        this_title = f"[{enLo_this}, {enHi_this}] MeV"
    else:
        enLo_this = enLo[i]
        enHi_this = enHi[i]
        this_title = f"[{enLo_this}, {enHi_this}] eV"
    
    this_name =  f"{name}_bin_{i+1}"

    n_bins = int(len(samps)/10)
    plt.figure()
    plt.hist(samps, n_bins)
    plt.title(this_title, fontsize = fontsize)
    plt.xticks(fontsize=labelsize); plt.yticks(fontsize=labelsize)
    #plt.xlabel("Neutron flux", fontsize=labelsize)
    plt.ticklabel_format(axis="x", style="sci", scilimits=(0,0))
    plt.tight_layout()
    plt.savefig(f"{this_name}.png", dpi=800)

    

N_chunks = int(Nsamps/n_cores)

inds = list(range(1,Nsamps+1))
chunks = [inds[x:x+N_chunks] for x in range(0, len(inds), N_chunks)]


def parallel_function(ind):
    return get_samples(ind, TallyId, statePointDir)

def parallel_plot(ind):
    return plot_this(ind, res)


Pool = mp.Pool(n_cores)

results = Pool.map(parallel_function, chunks)

res = np.vstack(np.array(results))

inds = range(len(enHi))
[plot_this(i, res) for i in inds]

sample_mean = np.mean(res, axis = 0)
sample_std = np.std(res, axis = 0)

print("-----------")
print()
print("sample mean:")
print(sample_mean)
print()
print("-----------")
print()
print("sample std:")
print(sample_std)
print()
print("-----------")