#!/bin/bash
# Interpolate dvardz from 20 km grid to ISMIP7 GrIS 1 km grid
# Usage: ./interp_func.sh <VAR> <infile> <outfile>
#   VAR: RU or ST

var=$1
infile=$2
outfile=$3

inres=20000m
outres=01000m

ingdf=./Data/grid_dRUdz_${inres}.nc
outgdf=./Data/textGDFs/gdf_ISMIP7_GrIS_${outres}.txt

cdo remapbil,${outgdf} -selvar,dvardz -setmisstoc,0 -setgrid,${ingdf} ${infile} tmp0.nc
ncks -O -C -x -v lat,lon,lon_bnds,lat_bnds tmp0.nc tmp0.nc
ncrename -v dvardz,d${var} tmp0.nc
cdo setmisstoc,0 tmp0.nc ${outfile}
/bin/rm tmp0.nc
