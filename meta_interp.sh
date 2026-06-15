#!/bin/bash
# interpolate some files

inpath=./Pre
outpath=./Output

# Setup

#agcmscen=CESM2-histo
#mkdir -p ${outpath}/${agcmscen}
#for year in {1971..2014}; do
#
#    infile=${inpath}/dST_HIRHAM5-yearly-${agcmscen}-${year}.nc
#    outfile=${outpath}/${agcmscen}/dST_HIRHAM5-yearly-${agcmscen}-${year}.nc
#    ./interp_func_ST.sh ${infile} ${outfile}
#
#    infile=${inpath}/dRU_HIRHAM5-yearly-${agcmscen}-${year}.nc
#    outfile=${outpath}/${agcmscen}/dRU_HIRHAM5-yearly-${agcmscen}-${year}.nc
#    ./interp_func_RU.sh ${infile} ${outfile}
#    
#done

agcmscen=CESM2-ssp585
mkdir -p ${outpath}/${agcmscen}
#for year in {2015..2100}; do
for year in {2015..2015}; do

    infile=${inpath}/dST_HIRHAM5-yearly-${agcmscen}-${year}.nc
    outfile=${outpath}/${agcmscen}/dST_HIRHAM5-yearly-${agcmscen}-${year}.nc
    ./interp_func_ST.sh ${infile} ${outfile}

    infile=${inpath}/dRU_HIRHAM5-yearly-${agcmscen}-${year}.nc
    outfile=${outpath}/${agcmscen}/dRU_HIRHAM5-yearly-${agcmscen}-${year}.nc
    ./interp_func_RU.sh ${infile} ${outfile}
    
done

