###
#   Defining enviromental variables 
#   Please change these directories to the apropriate ones
#                   A.G.
###


# Home directory of openmc
export OPENMC_HOME=/cosma/home/dp163/dc-gray2/opt/openmc 

##
#   openmc crossection files
##
# Crossections xml file (default)
export OPENMC_CROSS_SECTIONS=/cosma/home/dp163/dc-gray2/data7/neutronics/nuclearData/nndc-b7.1-hdf5/cross_sections.xml

# TENDL library xml
export OPENMC_TENDL_XS=/cosma/home/dp163/dc-gray2/data7/neutronics/nuclearData/tendl-2019-hdf5/cross_sections.xml

# JEFF library xml
export OPENMC_JEFF_XS=/cosma/home/dp163/dc-gray2/data7/neutronics/nuclearData/jeff-3.3-hdf5/cross_sections.xml

##
#   data endf files
##
# Crossection endf dir
#export OPENMC_ENDF=/cosma/home/dp163/dc-gray2/data7/neutronics/nuclearData/nndc-b7.1-hdf5/cross_sections.xml


##
# Openmc data processing directory: https://github.com/openmc-dev/data
##
PATH=$PATH:/cosma/home/dp163/dc-gray2/opt/openmc/data
PYTHONPATH=$PYTHONPATH:/cosma/home/dp163/dc-gray2/opt/openmc/data