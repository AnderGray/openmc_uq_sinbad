##
#   Making oktav-ni source. OPENMC_HOME must be set
##

mkdir source/bld
cd source/bld
cmake ..
make 
cp libsource.so ../../
cd ../..