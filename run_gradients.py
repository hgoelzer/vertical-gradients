import numpy as np
from sklearn.linear_model import LinearRegression
import netCDF4 as nc

# ── Configuration ──────────────────────────────────────────────────────────
APATH  = './Data/HIRHAM5/'
AGCM   = 'CESM2-ssp585'
YEARS  = range(2015, 2016)
SRF_NC = 'Data/HIRHAM5_static_fields.nc'

SNX, SNY = 30, 30   # stencil half-width (pixels)
DNX, DNY = 20, 20   # sampling stride (pixels)

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


def write_output(out_path, dvardz, xout, yout, units):
    """Write gradient result to NetCDF4."""
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


if __name__ == '__main__':
    srf_ds = nc.Dataset(SRF_NC, 'r')
    srf = srf_ds['elev'][:, :]
    srf_ds.close()
    ny, nx = srf.shape

    for var, cfg in VAR_CONFIG.items():
        for yr in YEARS:
            print(f'{var} {yr}')
            afile    = f'{var}_HIRHAM5-yearly-{AGCM}-{yr}.nc'
            in_path  = f'{APATH}{AGCM}/{afile}'
            out_path = f'Pre/d{afile}'

            ds_in  = nc.Dataset(in_path, 'r')
            data2d = ds_in[cfg['nc_var']][0, :, :] if cfg['has_time_dim'] \
                     else ds_in[cfg['nc_var']][:, :]
            ds_in.close()

            dvardz, xout, yout = compute_gradient(
                data2d, srf, ny, nx, SNX, SNY, DNX, DNY)
            write_output(out_path, dvardz, xout, yout, cfg['units'])
