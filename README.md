# openmc_uq_sinbad
Repository for running SINBAD benchmarks with openmc and nuclear data uncertainty propagation. Nuclear data is propagated with Monte Carlo simulation, à la Total Monte Carlo (TMC).

Required:

* [openmc](https://github.com/openmc-dev/openmc)
* [openmc/data](https://github.com/openmc-dev/data)
* [NJOY](https://github.com/njoy/NJOY21)
* [SANDY](https://github.com/luca-fiorito-11/sandy)


Useage:
---
* Download relevant endf and hdf5 data with [openmc/data](https://github.com/openmc-dev/data) scripts (NNDC, TENDL and JEFF used)
* Set relevant environmental variables in environment.sh
* (If TENDL) Set names of TENDL endf files with [randomData/rename_tendl_lib.py](https://github.com/AnderGray/openmc_uq_benchmarks/blob/main/randomData/rename_tendl_lib.py)
* Sample benchmark data with scripts in randomData
  * SANDY used for sampling
  * Slurm submission scripts provided, appropriate changes required
  * Default number of samples: 500

Details:
---
In TMC random evaluations of the nuclear data quantities are created either by using the endf covaraiance information (produces gaussian random evalutations) or by using a bayesian method with a nuclear reaction model code (TENDL library produced this way). The particle transport simulation is then repeated with each random evaluation. Each transport simulation has statistical uncertainty assosiated with it, which also must be considered. If the individual statistical uncertainty is negliable compared to the ND uncertainty, then standard probability theory may be applied. If this is not the case and both need to be considered, we use [imprecise probabilities](https://en.wikipedia.org/wiki/Imprecise_probability) to perform further analysis. This is especially relevent in "Fast-TMC", where larger statistical uncertainty is exchanged for compute time.
