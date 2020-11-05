#!/bin/bash -l
#SBATCH -A dp163
#SBATCH -p cosma7
#SBATCH -J Fng_tendl_processing
#SBATCH -e Fng_tendl_errors
#SBATCH -o Fng_tendl_print
#SBATCH -D ./
#SBATCH --export=ALL
#SBATCH -N 1
#SBATCH -n 28
#SBATCH -t 15:00:00

module purge
module load neutronics

EXEC="python3 sample_sandy.py -s 500 -n Cr50 Cr52 Cr54 Co59 Mo92 Mo94 Mo95 Mo96 Mo97 Mo98 Mo100 V50 V51 Na23 Al27 K39 K40 K41 Nb93 Au197 -p $SLURM_NTASKS -d tendl_rand -l $TENDL_ENDF"

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
