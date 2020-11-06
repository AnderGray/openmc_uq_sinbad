####
#
#   This scripts plots multiple samples of a uncertain crossection. Plots mean and samples
#
#                   Ander Gray
####

import argparse
import os
import sys
from multiprocessing import Pool

import openmc.data
from plottingUtils import plotRandomSlice

description = '''
Plots random crossections
'''


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(
    description=description,
    formatter_class=CustomFormatter
)
parser.add_argument('-n', '--nuclides', nargs='+',
                    default=['Fe56'], help="Select which nuclides to plot")

parser.add_argument('-mt', '--reaction',
                    default=1, help="Select which reactions to plot")

parser.add_argument('-mt2', '--reaction2',
                    default=None, help="Select which reactions to plot")

parser.add_argument('-t', '--temp', nargs='+',
                    default=[294], help="Temperatures to plot")

parser.add_argument('-Nf', '--Nfiles',
                    default=10, help="Number of samples to plot")

parser.add_argument('-E1', '--Energy1',
                    default=3.8e5, help="First energy location to slice cross-section")

parser.add_argument('-E2', '--Energy2',
                    default=4.8e5, help="Second energy location to slice cross-section")                    

parser.add_argument('-d', '--destination', default=None,
                    help='Destination of top of nuclear data library')


args = parser.parse_args()


nucs = args.nuclides
temps = args.temp
Nfiles = int(args.Nfiles)
E1 = float(args.Energy1)
E2 = float(args.Energy2)

MT1 = int(args.reaction)

if args.reaction2 is None:
    MT2 = MT1
else:
    MT2 = int(args.reaction2)

libdir = args.destination
if libdir is None:
    libdir = outputDir = os.path.abspath(os.getcwd())


for nuc in nucs:
        for t in temps:
            plotRandomSlice(nuc, Nfiles, MT1, MT2, E1, E2, t, libdir)

