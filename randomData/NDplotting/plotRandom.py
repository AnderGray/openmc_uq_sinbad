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
from plottingUtils import plotRandom

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

parser.add_argument('-mt', '--reactions', nargs='+',
                    default=[1], help="Select which reactions to plot")

parser.add_argument('-t', '--temp', nargs='+',
                    default=[294], help="Temperatures to plot")

parser.add_argument('-Nf', '--Nfiles',
                    default=10, help="Number of samples to plot")

parser.add_argument('-d', '--destination', default=None,
                    help='Destination of top of nuclear data library')


args = parser.parse_args()


nucs = args.nuclides
reacts = [int(i) for i in args.reactions]
temps = args.temp
Nfiles = int(args.Nfiles)

libdir = args.destination
if libdir is None:
    libdir = outputDir = os.path.abspath(os.getcwd())


for nuc in nucs:
        for mt in reacts:
            for t in temps:
                plotRandom(nuc, Nfiles, mt, t, libdir)


'''
with Pool() as pool:
    results = []
    for nuc in nucs:
        for mt in reacts:
            for t in temps:
                #print('Starting something!')
                #plotRandom(nuc, Nfiles, mt, t, libdir)
                inargs = (nuc, Nfiles, mt, t, libdir)
                r = pool.apply_async(plotRandom, inargs)
                results.append(r)

    for r in results:
        r.wait()

'''