#!/usr/bin/env python3
import pathos.multiprocessing as mp
from tkinter import N, NS
import openmc
import random
import h5py
import os
import sys
from shutil import copyfile
import shutil
import copy
from pathlib import Path
import numpy as np
import time
import argparse
from scipy.stats import norm
import csv
import pandas

description = """
Gets the moments from a TMC simulation
"""


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


parser = argparse.ArgumentParser(
    description=description, formatter_class=CustomFormatter)

parser.add_argument("-d", "--destination", default=None, 
                    help="Directory to save results")
parser.add_argument("-t", "--tally", default=None, 
                    help="Tally ID")
parser.add_argument("-s", "--samples", default=None, 
                    help="Number of statepoint files")
parser.add_argument("-name", "--savename", default=None, 
                    help="Simulation name")
parser.add_argument("-p", "--ncores", default=1, 
                    help="Simulation name")

args = parser.parse_args()

args = parser.parse_args()
script_dir = Path.cwd()

input_dir = args.destination
simname = args.savename
TallyId = args.tally
Nsamps = args.samples
save_name = args.savename
ncores = int(args.ncores)

if input_dir == None:
    input_dir = Path.cwd()
else:
    input_dir = Path(input_dir).resolve() 

if TallyId == None:
    TallyId = 1
else:
    TallyId = int(TallyId)

if simname == None:
    simname = os.path.basename(input_dir)

if Nsamps == None:    
    Nsamps = np.sum([filename.startswith("statepoint.") for filename in os.listdir(input_dir)])
else:
    Nsamps = int(Nsamps)

if Nsamps == 0: raise Exception("No samples found")

#===============================
# Get energy of first simulation

sp1 = openmc.StatePoint(f'{input_dir}/statepoint.1.h5')
Tal = sp1.get_tally(id = TallyId).get_pandas_dataframe()

enHi = Tal['energy high [eV]']
enLo = Tal['energy low [eV]']


def get_samples(indecies, TallyId, statePointDir):
    index = indecies[0]
    try: 
        sp1 = openmc.StatePoint(f'{statePointDir}/statepoint.{index}.h5')
    except:
        sp1 = openmc.StatePoint(f'{statePointDir}/statepoint.{index-1}.h5')

    Tal = sp1.get_tally(id = TallyId).get_pandas_dataframe()

    means = np.array(Tal['mean'])
    stds = np.array(Tal['std. dev.'])

    for i in indecies[1:]:
        try:
            sp = openmc.StatePoint(f'{statePointDir}/statepoint.{i}.h5')
        except:
            sp = openmc.StatePoint(f'{statePointDir}/statepoint.{i-1}.h5')
            
        Tal = sp.get_tally(id = TallyId).get_pandas_dataframe()
        thisMean = np.array(Tal['mean'])
        thisStds = np.array(Tal['std. dev.'])

        means = np.vstack((means,thisMean))
        stds = np.vstack((stds,thisStds))

    return means, stds

def compute_area(means, stds):

    N_bins = len(means[0,:])
    N_samps = len(means[:,0])
    N_ps = 1000
    ps = np.linspace(0.0001,0.9999, N_ps)

    p_lo = [norm(means[0,i], stds[0,i]).ppf(ps) for i in range(N_bins)]
    p_hi = [norm(means[0,i], stds[0,i]).ppf(ps) for i in range(N_bins)]

    p_lo = np.array(p_lo)
    p_hi = np.array(p_hi)

    for i in range(1,N_samps):
        p_new = [norm(means[1,j], stds[1,j]).ppf(ps) for j in range(N_bins)]
        p_new = np.array(p_new)

        p_lo = np.minimum(p_lo, p_new)
        p_hi = np.maximum(p_hi, p_new)

    rectangles = np.abs((p_hi - p_lo))*(ps[2] - ps[1])
    Areas = np.sum(rectangles, axis = 1)

    return Areas

N_chunks = int(Nsamps/ncores)

inds = list(range(1,Nsamps+1))
chunks = [inds[x:x+N_chunks] for x in range(0, len(inds), N_chunks)]

def parallel_function(ind):
    return get_samples(ind, TallyId, input_dir)

Pool = mp.Pool(ncores)
results = Pool.map(parallel_function, chunks)


mean_samps, stds = zip(*results)

means = np.vstack(np.array(mean_samps))
stat_errs = np.vstack(np.array(stds))

sample_mean = np.mean(means, axis = 0)
sample_std = np.std(means, axis = 0)
av_stat = np.mean(stat_errs, axis = 0)
Areas = compute_area(means, stat_errs)

save_Data = pandas.DataFrame(
    {'E_lo': enLo.values,
    'E_hi': enHi.values,
    'mean': sample_mean,
    'std': sample_std,
    'av_stat_error': av_stat,
    'Area': Areas
    }
)
save_Data.to_csv(f'{simname}_moments.csv')

mean_data = pandas.DataFrame(
    {
        'E_lo': enLo.values,
        'E_hi': enHi.values,
        'mean_samples': means,
        'stds': stat_errs
    }
)
mean_data.to_csv(f'{simname}_means.csv')
'''
with open(f'{simname}_moments.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(rows)

field_names = ['mean_samps']

with open(f'{simname}_means.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(row_means)
'''
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
print()
print("av stat error:")
print(av_stat)
print()
print("-----------")
print()
print("Areas:")
print(Areas)
print()
print("-----------")
