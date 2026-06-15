#!/bin/bash
# Interpolate from dvardz to ISMIP6 grid


# source and target data file
#infile=dRU_HIRHAM5-yearly-CESM2-ssp585-2015.nc
#outfile=/nird/projects/NS8085K/PROTECT/RCM/HIRHAM5/CESM2-ssp585/dRU_HIRHAM5-yearly-CESM2-ssp585-2015.nc

infile=$1
outfile=$2

# resolution
inres=20000m
outres=01000m

# input/output grid description files
ingdf=./Data/grid_dRUdz_${inres}.nc
outgdf=./Data/textGDFs/gdf_ISMIP7_GrIS_${outres}.txt

#weights
wgts=./Grid/weights_dRUdz${inres}_e${outres}.nc

# bilinear
cdo remapbil,${outgdf} -selvar,dvardz -setmisstoc,0 -setgrid,${ingdf} ${infile} tmp0.nc

# remove unused vars
ncks -O -C -x -v lat,lon,lon_bnds,lat_bnds tmp0.nc tmp0.nc
# rename
ncrename -v dvardz,dRU tmp0.nc
# replace missing with zeros
cdo setmisstoc,0 tmp0.nc ${outfile}
