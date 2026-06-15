# SMB gradients from runoff and ST mimicking MAR 

## Setup

```
conda create -n smbenv -c conda-forge scikit-learn numpy scipy xarray netCDF4 pandas matplotlib openpyxl gdal progress cdo nco
conda activate smbenv
```

See also `environment.yml`.

## Run the pipeline

All commands must be run from inside `vertical-gradients/`.

```
conda activate smbenv
python run_gradients.py
```

This single script runs the full pipeline for both variables (RU and ST):
1. Computes vertical gradients on a 20 km intermediate grid → `Pre/`
2. Bilinearly interpolates to the ISMIP7 GrIS 1 km grid → `Output/`

## Configuration

Edit the top of `run_gradients.py` to change scenario, year range, or paths:

```python
AGCM  = 'CESM2-ssp585'
YEARS = range(2015, 2016)
APATH = './Data/HIRHAM5/'
```

## Directories 

| Directory | Contents |
|-----------|----------|
| `Data/`   | Input forcing files, static fields (`HIRHAM5_static_fields.nc`), grid description files |
| `Pre/`    | Intermediate 20 km gradient files (`dRU_*.nc`, `dST_*.nc`) |
| `Output/` | Final ISMIP7 1 km gradient files |
