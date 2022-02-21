#!/bin/bash -l
#SBATCH -A UKAEA-AP001-CPU
#SBATCH -p cclake
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH -e errors
#SBATCH -o output
#SBATCH -D ./
#SBATCH --export=ALL
#SBATCH --output=array_%A-%a.out    # Standard output and error log


module purge
module load openmc


#EXEC="python convert_tendl_rand.py -b"
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

cd $1-$SLURM_ARRAY_TASK_ID

$EXEC
echo Done with OPENMC, processing

mv statepoint.$2.h5 ../statepoints-$1/statepoint.$SLURM_ARRAY_TASK_ID.h5
cd ..
rm -r $1-$SLURM_ARRAY_TASK_ID

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
