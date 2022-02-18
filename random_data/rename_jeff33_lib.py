####
#   Changes the file names of the tendl endf library to match the nndc library.
#   Allows library to be used by sample_sandy.py
#
#   Run this file in the tendl-2019-endf/neutron directory
#
#                                       A.Gray, Uni of liverpool
###


import os
import shutil
from pathlib import Path

import openmc.data


directory = Path.cwd()
atomic_dict = openmc.data.ATOMIC_NUMBER

for filename in os.listdir(directory):
    if filename.endswith(".jeff33"):
        atomic_sym = ""
        massNumber= ""
        prefix = ""
        i = filename.find("-") + 1
        this = filename[i]
        while not this.isdigit():
            atomic_sym = atomic_sym + this
            i = i + 1
            this = filename[i]

        atomic_sym = atomic_sym[0:-1]
        
        while this.isdigit():
            massNumber = massNumber + this
            i = i + 1
            this = filename[i]
        #if not this == ".": prefix = this

        newFile = f"n-{int(atomic_dict[atomic_sym]):03}_{atomic_sym}_{massNumber}.endf"
        os.rename(filename, newFile)

os.rename("n-006_C_012.endf", "n-006_C_000.endf")
