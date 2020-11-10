#!/usr/bin/env python3

#import ray
import h5py
import os
from shutil import copyfile
import shutil
import copy
from pathlib import Path
import numpy as np

import openmc

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

from scipy.stats import norm

import warnings

warnings.simplefilter("ignore")

###
#   Plot parameters
###

plotData = True
plotTendl = True 
plotJeff = False

fontsize = 22

useLeth = 1
useSurf = 1

r = 0.4

TallyId = 1

simDir = Path.cwd()

Nfiles = 500

SIMNAME1 = "endfFe"
SIMNAME2 = "tendlFe"
statePointDirSandy = simDir / f"statepoints-{SIMNAME1}"
statePointDirTendl = simDir / f"statepoints-{SIMNAME2}"




##
#   Plotting stuff
##

index = 1
sp1 = openmc.StatePoint(f'{statePointDirSandy}/statepoint.{index}.h5')

Tal = sp1.get_tally(id = TallyId).get_pandas_dataframe()

enHi = Tal['energy high [eV]']
enLo = Tal['energy low [eV]']

widths = (enHi - enLo)

leth = 1
surf = 1

if useLeth: leth = abs(np.log(widths) * (widths > 1))
if useSurf: surf = np.pi * 4 * r**2

means = np.array(Tal['mean'])

stds = np.array(Tal['std. dev.'])

Upper = norm(means,stds).ppf(0.95)
Lower = norm(means,stds).ppf(0.05)


print("Beginning endf plot...")

for i in range(2, Nfiles+1):
    sp = openmc.StatePoint(f'{statePointDirSandy}/statepoint.{i}.h5')
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

means = means/Nfiles

fig = plt.figure(figsize=(19, 15))
#ax = fig.add_subplot()

meansEndf = means * leth / surf
UpperEndf = Upper * leth / surf
LowerEndf = Lower * leth / surf




if plotTendl:

    index = 1
    sp1 = openmc.StatePoint(f'{statePointDirTendl}/statepoint.{index}.h5')

    Tal = sp1.get_tally(id = TallyId).get_pandas_dataframe()

    enHi = Tal['energy high [eV]']
    enLo = Tal['energy low [eV]']

    widths = enHi - enLo

    leth = 1
    surf = 1

    if useLeth: leth = abs(np.log(widths) * (widths > 1))
    if useSurf: s = np.pi * 4 * r**2

    means = np.array(Tal['mean'])

    stds = np.array(Tal['std. dev.'])

    Upper = norm(means,stds).ppf(0.95)
    Lower = norm(means,stds).ppf(0.05)
    

    print("Beginning tendl plot...")

    for i in range(2, Nfiles+1):
        sp = openmc.StatePoint(f'{statePointDirTendl}/statepoint.{i}.h5')
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

    means = means/Nfiles

    meansTendl = means * leth/surf
    UpperTendl = Upper * leth/surf
    LowerTendl = Lower * leth/surf


if plotData:
    print("Beginning Exp data plot...")
    highDir = simDir / "exp_data/OKTAV_high.xlsx"
    lowDir = simDir / "exp_data/OKTAV_low.xlsx"
    high = pd.read_excel(highDir)
    low = pd.read_excel(lowDir)

    plt.errorbar(high['energy'] * 10e5, high['current'], yerr= high['error'] * high['current'] / 100, ecolor= 'blue', fmt='o', capsize=1, markersize = 2, alpha = 1, label='Oktav-Fe High eV')
    plt.errorbar(low['energy'] * 10e5, low['current'], yerr= low['error'] *  low['current'] / 100, ecolor= 'blue', fmt='o', capsize=1, markersize = 2, alpha = 1, label='Oktav-Fe Low eV')


plt.step(enHi, meansEndf,color = "green", alpha = 1,linewidth = 2, label='ENDF/B-VII.1', where = "post")
plt.step(enHi, UpperEndf,color = "red", alpha = 1,linewidth = 1, where = "post")
plt.step(enHi, LowerEndf,color = "red", alpha = 1,linewidth = 1, where = "post")
plt.fill_between(enHi, LowerEndf, UpperEndf,alpha=0.3, color ="red", step = "post" , label='ENDF 95%')

if plotTendl:
    plt.step(enHi, meansTendl,color = "blue", alpha = 1,linewidth = 2, label='tendl-2019', where = "post")
    plt.step(enHi, UpperTendl,color = "grey", alpha = 1,linewidth = 1, where = "post")
    plt.step(enHi, LowerTendl,color = "grey", alpha = 1,linewidth = 1, where = "post")
    plt.fill_between(enHi, LowerTendl, UpperTendl,alpha=0.3, color ="grey", step = "post", label='tendl 95%')


if plotJeff:
    print("Beginning jeff plot...")
    sp = openmc.StatePoint("statepoint.jeff.h5")
    Tal = sp.get_tally(id = TallyId).get_pandas_dataframe()
    #enHi = Tal['energy high [eV]']
    #enLo = Tal['energy low [eV]']
    mean = Tal['mean']
    stf = Tal['std. dev.']
    meanJeff = mean * leth/surf
    plt.step(enHi, meanJeff, color = "black", alpha = 1,linewidth = 2, label='jeff', where = "post")


leg = plt.legend()

plt.yscale("log")
plt.xscale("log")
plt.xlim([10**3, 2*10**7])
#plt.ylim([10**(-9), 1])
plt.ylim([10**(-6), 1])

plt.xticks(fontsize=fontsize); plt.yticks(fontsize=fontsize)
plt.xlabel("Energy [eV]", fontsize=fontsize)
if useLeth: 
    plt.ylabel("Neutron current [ n/source/lethargy] ", fontsize=fontsize)
else:
    plt.ylabel("Neutron current [ n/source] ", fontsize=fontsize)

print("saving...")
plt.savefig(f"oktav_fe_current.png", dpi=1200)
plt.clf()