import os
import subprocess
import pathlib
import numpy as np
from sklearn.linear_model import LinearRegression
import netCDF4 as nc

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ── Configuration ──────────────────────────────────────────────────────────
APATH  = './Data/HIRHAM5/'
AGCM   = 'CESM2-ssp585'
YEARS  = range(2015, 2016)
SRF_NC = 'Data/HIRHAM5_static_fields.nc'

SNX, SNY = 30, 30   # stencil half-width (pixels)
DNX, DNY = 20, 20   # sampling stride (pixels)

INRES  = '20000m'
OUTRES = '01000m'
INGDF  = f'./Data/grid_dRUdz_{INRES}.nc'
OUTGDF = f'./Data/textGDFs/gdf_ISMIP7_GrIS_{OUTRES}.txt'

VAR_CONFIG = {
    'RU': {'nc_var': 'RU', 'has_time_dim': False, 'units': 'mmWE/yr/m'},
    'ST': {'nc_var': 'ST', 'has_time_dim': True,  'units': 'degree/m'},
}


def compute_gradient(data2d, srf, ny, nx, snx, sny, dnx, dny):
    """Fit elevation-variable linear regression on a strided stencil grid.

    Returns dvardz (nyout x nxout), xout (pixel indices), yout (pixel indices).
    """
    nxout = int((nx - 1 - 2 * snx) / dnx + 1)
    nyout = int((ny - 1 - 2 * sny) / dny + 1)
    dvardz = np.zeros((nyout, nxout))
    xout   = np.zeros(nxout)
    yout   = np.zeros(nyout)

    yc = -1
    for y in range(sny, ny - sny, dny):
        yc += 1
        yout[yc] = y
        xc = -1
        for x in range(snx, nx - snx, dnx):
            xc += 1
            if yc == 0:
                xout[xc] = x

            dataloc = data2d[y - sny:y + sny, x - snx:x + snx]
            srfloc  = srf[y - sny:y + sny,   x - snx:x + snx]
            datavec = dataloc.flatten()
            srfvec  = srfloc.flatten()

            datavec = np.where(np.isfinite(datavec), datavec, 0)
            datavec = np.where(datavec < 20000, datavec, 0)

            sel = [i for i, v in enumerate(datavec)
                   if v != 0 and srfvec[i] != 0]
            srfvec  = srfvec[sel]
            datavec = datavec[sel]

            if len(sel) > 20:
                xr = srfvec.reshape(-1, 1)
                model = LinearRegression().fit(xr, datavec)
                dvdz = model.coef_[0]
                if dvdz < 2:
                    dvardz[yc, xc] = dvdz

    return dvardz, xout, yout


def write_pre(out_path, dvardz, xout, yout, units):
    """Write intermediate 20 km gradient to Pre/ as NetCDF4."""
    nyout, nxout = dvardz.shape
    ds = nc.Dataset(out_path, 'w', format='NETCDF4')
    ds.createDimension('x', nxout)
    ds.createDimension('y', nyout)

    v = ds.createVariable('dvardz', 'float', ('y', 'x'))
    v.units = units
    ds['dvardz'][:, :] = dvardz

    vx = ds.createVariable('x', 'float', ('x',))
    vx.units = 'm'
    ds['x'][:] = xout

    vy = ds.createVariable('y', 'float', ('y',))
    vy.units = 'm'
    ds['y'][:] = yout

    ds.close()


def interpolate(var, pre_path, out_path):
    """Bilinear remapping from 20 km intermediate grid to ISMIP7 1 km grid."""
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    tmp = './tmp_interp.nc'
    subprocess.run(
        ['cdo', f'remapbil,{OUTGDF}', '-selvar,dvardz',
         '-setmisstoc,0', f'-setgrid,{INGDF}', pre_path, tmp],
        check=True)
    subprocess.run(
        ['ncks', '-O', '-C', '-x', '-v', 'lat,lon,lon_bnds,lat_bnds', tmp, tmp],
        check=True)
    subprocess.run(['ncrename', '-v', f'dvardz,d{var}', tmp], check=True)
    subprocess.run(['cdo', 'setmisstoc,0', tmp, out_path], check=True)
    os.remove(tmp)


if __name__ == '__main__':
    srf_ds = nc.Dataset(SRF_NC, 'r')
    srf = srf_ds['elev'][:, :]
    srf_ds.close()
    ny, nx = srf.shape

    for var, cfg in VAR_CONFIG.items():
        for yr in YEARS:
            afile    = f'{var}_HIRHAM5-yearly-{AGCM}-{yr}.nc'
            in_path  = f'{APATH}{AGCM}/{afile}'
            pre_path = f'Pre/d{afile}'
            out_path = f'Output/{AGCM}/d{afile}'

            print(f'{var} {yr}: computing gradient ...')
            ds_in  = nc.Dataset(in_path, 'r')
            data2d = ds_in[cfg['nc_var']][0, :, :] if cfg['has_time_dim'] \
                     else ds_in[cfg['nc_var']][:, :]
            ds_in.close()

            dvardz, xout, yout = compute_gradient(
                data2d, srf, ny, nx, SNX, SNY, DNX, DNY)
            write_pre(pre_path, dvardz, xout, yout, cfg['units'])

            print(f'{var} {yr}: interpolating to 1 km ...')
            interpolate(var, pre_path, out_path)
