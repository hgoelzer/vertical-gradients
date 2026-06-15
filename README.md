# SMB gradients from runoff and ST mimicking MAR 

## python setup smbenv (see also environment.yml)
```
conda create -n smbenv -c conda-forge scikit-learn numpy scipy xarray netCDF4 pandas matplotlib openpyxl gdal progress cdo
conda activate smbenv
```

## Create gradients on low resolution 20km grid
```
conda activate smbenv
python meta_dRudz.py
  dRudz_src.py

python meta_dSTdz.py
  dSTdz_src.py
```

## Interpolate to ISMIP grid
```
conda activate nc
./meta_interp.sh
  ./interp_func.sh
  ./interp_func_ST.sh
```

## Directories 
```
Expecting forcing and auxiliary files in Data/
Producing temporary (20 km) files in Pre/
Resulting output in Output/
```
