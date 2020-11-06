#!/usr/bin/env python3

import openmc
import random
from multiprocessing import Pool
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

import tmc_tools


description = """
Uses a previously randomly sampled nuclear data library and performs Total Monte Carlo (TMC)/ 2nd order Monte Carlo simulation.
To be run in the same directory as the openmc inputs.
"""


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


parser = argparse.ArgumentParser(
    description=description, formatter_class=CustomFormatter)

parser.add_argument("-n", "--nuclides", nargs="+", 
                    default=["Fe56"], help="The nuclide(s) to be sampled")
parser.add_argument("-d", "--destination", default=None, 
                    help="Directory to save results")
parser.add_argument("-l", "--libdir", default=None, 
                    help="Directory of nuclear data library with random evals eg. crossections.xml")
parser.add_argument("-s", "--samples", default=500, 
                    help="Number of nuclear data samples")
parser.add_argument("-name", "--simname", default=None, 
                    help="Simulation name. Required")
parser.add_argument("-b", "--batches", default=None, 
                    help="Number of batches per sim. None for settings.xml specification")
parser.add_argument("-N", "--Nparticles", default=None, 
                    help="Number of particles per batch. None for settings.xml specification")

args = parser.parse_args()


args = parser.parse_args()
script_dir = Path.cwd()

nuclides = args.nuclides
output_dir = args.destination
simname = args.simname
crossections = args.libdir
Nouter = int(args.samples)
Ninner  = args.batches
Nparticles = args.Nparticles


if simname == None: raise Exception("Simulation name required. Use -name to specify")

if output_dir == None:
    output_dir = script_dir 
else:
    output_dir = Path(output_dir).resolve() 

if crossections == None:
    raise Exception("crossections.xml with random evaluations required. Specify location with -l")
else:
    crossections = Path(crossections).resolve()

statepoint_dir = output_dir/ f"statepoints-{simname}"

#============================================================
#   Read openmc input files

settings    = openmc.Settings.from_xml("settings.xml")
materials   = openmc.Materials.from_xml("materials.xml")
geometry    = openmc.Geometry.from_xml("geometry.xml")              # We do nothing we geometry, however parameteric geometry may also be sampled


#============================================================
#   Generate list of random nuclides and random seeds

Nnuclides   = len(nuclides)
NuclideStream = [None]*Nnuclides

for i in range(Nnuclides):
    numberStream = random.sample(range(1,Nouter+1),Nouter)
    Nuclide = nuclides[i]
    NuclideStream[i] = [f"{Nuclide}-{j}" for j in numberStream]

randomSeeds = [random.randint(1, sys.maxsize) for i in range(Nouter)]


#============================================================
#   Set simulation parameters

if Ninner is None: Ninner = settings.batches
if Nparticles is None: Nparticles = settings.particles

settings.particles = int(Nparticles)
settings.batches = int(Ninner)
materials.cross_sections = crossections


#============================================================
#   Create sim directory and save details

statepoint_dir.mkdir(exist_ok=True)

h1 = h5py.File( f'{statepoint_dir}/TMC_details.h5', 'w')

h1.create_dataset('uncertain_nulides', data = [n.encode("ascii", "ignore") for n in nuclides])
h1.create_dataset('Ninner', data = np.array(Ninner))
h1.create_dataset('Nouter', data = np.array(Nouter))
h1.create_dataset('NuclideStream', data = [[NuclideStream[i][j].encode("ascii", "ignore") for i in range(Nnuclides)] for j in range(Nouter)])
 
h1.close()



def prepSim(mats, sets, geo, index):

    print(f"Preparing sim {index}")

    SimName = f"{simname}-{index}"
    ThisSim = f"{output_dir}/{SimName}"

    if not os.path.exists(ThisSim):
        os.mkdir(ThisSim)
    os.chdir(ThisSim)
    
    sets.seed = randomSeeds[index-1]

    sets.export_to_xml()
    geo.export_to_xml()
    copyfile(f"{script_dir}/tallies.xml", f"{ThisSim}/tallies.xml")

    for i in range(Nnuclides):
        tmc_tools.replaceNuclideMaterial(nuclides[i], mats, NuclideStream[i][index-1])
    mats.export_to_xml()

    os.system(f"cp {script_dir}/openmc_sub.sh .")
    #os.system(f"cp ../formatTallies.py .")

    command = f"sbatch -J {index}_{simname} openmc_sub.sh {simname} {index} {Ninner}"
    os.system(command)
    
    os.chdir(script_dir)