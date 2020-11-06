# SINBAD fusion benchmarks with UQ and openmc
Repository for running SINBAD benchmarks with openmc and nuclear data uncertainty propagation. Nuclear data is propagated with Monte Carlo simulation, à la Total Monte Carlo (TMC).

Required:

* [openmc](https://github.com/openmc-dev/openmc)
* [openmc/data](https://github.com/openmc-dev/data)
* [NJOY](https://github.com/njoy/NJOY21)
* [SANDY](https://github.com/luca-fiorito-11/sandy)


Useage:
---
**Nuclear Data sampling:**
* Download relevant endf and hdf5 data with [openmc/data](https://github.com/openmc-dev/data) scripts (NNDC, TENDL and JEFF used)
* Set relevant environmental variables in environment.sh
* (If TENDL) Set names of TENDL endf files with _[randomData/rename_tendl_lib.py](https://github.com/AnderGray/openmc_uq_benchmarks/blob/main/randomData/rename_tendl_lib.py)_
* Sample benchmark data with scripts in _[randomData](https://github.com/AnderGray/openmc_uq_benchmarks/blob/main/randomData)_
  * SANDY used for sampling
  * Slurm submission scripts provided, appropriate changes required
  * Default number of samples: 500
  * Variance reduction cannot be used with these cross sections due to [issue #1699](https://github.com/openmc-dev/openmc/issues/1699)
  
**Benchmarks and Uncertainty Propagation**
* For Ni and FNG, build source with _buildSource.sh_

Details:
---
In TMC random evaluations of the nuclear data quantities are created either by using the endf covaraiance information (produces gaussian random evalutations) or by using a bayesian method with a nuclear reaction model code (TENDL library produced this way). The particle transport simulation is then repeated with each random evaluation. Each transport simulation has statistical uncertainty assosiated with it, which also must be considered. If the individual statistical uncertainty is negliable compared to the ND uncertainty, then standard probability theory may be applied. If this is not the case and both need to be considered, we use [imprecise probabilities](https://en.wikipedia.org/wiki/Imprecise_probability) to perform further analysis. This is especially relevent in "Fast-TMC", where larger statistical uncertainty is exchanged for compute time.
