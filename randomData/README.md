# SANDY sampling errors

missing covariance files
--
* Fe_endf: N14, P31, Mn55, S32, S33, S36

* Ni_endf: Ni62, Ni64, Mn55, Cu63, Cu63, N14

* fng_str_endf: Cr54, Mn55, Co59, Ni62, Ni64, Cu63, Cu65, V50, V51, K39, K40, K41, Nb93


ENDF format error
--
* Fe_tendl: O16, N14

* Ni_tendl: H1, B10, B11

* fng_str_tendl: H1, O16, N14, B10, B11


Uncertainty plots
--

* plotRandom.py: plots cross section with random evaluations
* plotSlice.py: plots random cross section, zoomed and distribution at two marked energies

Useage:

```python3
python3 plotRandom.py -n Fe56 -mt 1 -d endf_hdf5 --Nfiles 500 
```

![alt text](https://imgur.com/7zFAeko.png "Fe56 absorption")

![alt text](https://imgur.com/CjLz8Sr.png "Fe56 zoomed")

![alt text](https://imgur.com/9nN7rM4.png "Bivariate distribution at 2 energies")

![alt text](https://imgur.com/GbiYLGR.png "Correlation matrix")
