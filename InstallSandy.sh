#!/bin/bash

set -eux


function load_modules() {
    module purge
    module load slurm
    module load dot
    module load turbovnc/2.0.1
    module load vgl/2.5.1/64
    module load rhel7/global
    module load cmake/latest
    module load gcc/7
    module load openmpi-3.1.3-gcc-7.2.0-b5ihosk
    module load python/3.7
    module load hdf5/1.12.1
    export CC=mpicc
    export CXX=mpic++
    export LIB_PATH=""
}


function build_njoy() {

    cd $WORKDIR

    # Get the desired version of NJOY21 (1.0.1 in this example)
    git clone https://github.com/njoy/NJOY21.git
    cd NJOY21

    mkdir bin
    cd bin
    
    cmake -D CMAKE_BUILD_TYPE=Release .. -DCMAKE_INSTALL_PREFIX=$WORKDIR/NJOY21

    make

 #    make test

    cd ..
}

function build_sandy() {

    cd $WORKDIR

    git clone https://github.com/luca-fiorito-11/sandy.git
    cd sandy

    python3 setup.py install --user
}


load_modules
build_njoy
