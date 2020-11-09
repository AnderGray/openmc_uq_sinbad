#!/bin/bash -l
#SBATCH -A dp163
#SBATCH -p cosma7
#SBATCH -e errors
#SBATCH -o output
#SBATCH -D ./
#SBATCH --export=ALL
#SBATCH -N 1
#SBATCH -n 28
#SBATCH -t 15:00:00

module purge
module load neutronics

#EXEC="python convert_tendl_rand.py -b"

OPENMC_CROSS_SECTIONS=OPENMC_JEFF_XS 
EXEC="openmc -s $SLURM_NTASKS"

#
# Should not need to edit below this line
#
echo ========================================================= echo SLURM job: submitted date = `date`
date_start=`date +%s`
echo ========================================================= echo Job output begins
echo -----------------
echo
hostname
# $SLURM_NTASKS is defined automatically as the number of processes in the # parallel environment.
echo Running with $SLURM_NTASKS cores
#mpirun -np $SLURM_NTASKS $EXEC
$EXEC
echo Done with OPENMC, processing

mv statepoint.10.h5 statepoint.jeff.h5


echo
echo ---------------
echo Job output ends
date_end=`date +%s`
seconds=$((date_end-date_start))
minutes=$((seconds/60))
seconds=$((seconds-60*minutes))
hours=$((minutes/60))
minutes=$((minutes-60*hours))
echo =========================================================
echo SLURM job: finished date = `date`
echo Total run time : $hours Hours $minutes Minutes $seconds Seconds echo =========================================================
