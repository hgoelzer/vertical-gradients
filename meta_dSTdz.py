# Process a number of files by sourcing the processing script

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import SplineTransformer
from sklearn.metrics import mean_squared_error, r2_score
import netCDF4 as nc

fn = 'Data/HIRHAM5_static_fields.nc'
ds = nc.Dataset(fn, 'r+',clobber=True)
srf = ds['elev'][:,:]

# grid dimensions
ny, nx = srf.shape
#print(nx,ny)


# Settings
# stencil size
snx = 30
sny = 30

# sampling
dnx = 20
dny = 20

nxout = int((nx-1-2*snx)/dnx+1)
nyout = int((ny-1-2*sny)/dny+1)


exps = ['']
apath = './Data/HIRHAM5/'
agcm = 'CESM2-ssp585'

for yr in range(2015, 2016, 1):
    print(yr)
    afile = 'ST_HIRHAM5-yearly-' + agcm + '-' + str(yr) + '.nc' 
    exec(open('dSTdz_src.py').read())

