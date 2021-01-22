####
#   Changes the file names of the tendl endf library to match the nndc library.
#   Allows library to be used by sample_sandy.py
#
#   Run this file in the tendl-2019-endf/ directory with neutron_file from tendl-2017
#
#                                       A.Gray, Uni of liverpool
###


import os
import shutil
import sys
from pathlib import Path

import openmc.data


directory = Path.cwd()
atomic_dict = openmc.data.ATOMIC_NUMBER

print("Making neutron file")
os.system("mkdir neutron")

print("Copying files")
os.system("cp -r neutron_file/*/*/lib/endf/* neutron")

os.system("cd neutron")

print("Renaming files")

directory = Path.cwd()

for filename in os.listdir(directory):
    if filename.endswith(".tendl"):
        atomic_sym = ""
        massNumber= ""
        prefix = ""
        i = 2
        this = filename[i]
        while not this.isdigit():
            atomic_sym = atomic_sym + this
            i = i + 1
            this = filename[i]
        while this.isdigit():
            massNumber = massNumber + this
            i = i + 1
            this = filename[i]
        if not this == ".": prefix = this

        newFile = f"n-{int(atomic_dict[atomic_sym]):03}_{atomic_sym}_{massNumber}{prefix}.endf"
        os.rename(filename, newFile)

os.rename("n-006_C_012.endf", "n-006_C_000.endf")

print("Done!")