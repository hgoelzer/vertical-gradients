# Find vertical gradient from spatial gradients 

#
#apath = '/nird/projects/NS8085K/PROTECT/RCM/HIRHAM5'
#agcm = 'CESM2-ssp585'
#afile = 'RU_HIRHAM5-yearly-CESM2-ssp585-2020.nc' 
# reading files
fn = apath + '/' + agcm + '/' + afile
ds = nc.Dataset(fn, 'r+',clobber=True)
st = ds['ST'][0,:,:]
x1 = ds['x'][:]
y1 = ds['y'][:]
#print(st.shape)
#print(x1.shape)
#print(y1.shape)


# Output file and array
fn = 'Pre/d' + afile
ds = nc.Dataset(fn, 'w', format='NETCDF4')
lat_dim = ds.createDimension('x', nxout) 
lon_dim = ds.createDimension('y', nyout) 

dvardz = np.zeros(shape=(nyout, nxout))
coeff = np.zeros(shape=(nyout, nxout))
sellen = np.zeros(shape=(nyout, nxout))
#print(dvardz.shape)
xout = np.zeros(shape=(nxout))
yout = np.zeros(shape=(nyout))

yc = -1
for y in range(0+sny, ny-sny, dny):
    yc=yc+1
    yout[yc] = y
    xc = -1
    for x in range(0+snx, nx-snx, dnx):
        xc=xc+1
        if (yc==0):
            #print(xc)
            xout[xc] = x
            
        #print(y,x)
        #print(y-sny,y+sny,x-snx,x+snx)
        stloc = st[y-sny:y+sny,x-snx:x+snx]
        #print(stloc)
        srfloc = srf[y-sny:y+sny,x-snx:x+snx]
        #print(srfloc)
        stvec = stloc.flatten()
        srfvec = srfloc.flatten()
        # filter for nan
        stvec = np.where(np.isfinite(stvec), stvec, 0)
        stvec = np.where(stvec<20000, stvec, 0)
        #print(stvec)
        #print(srfvec)

        # filter zero surface /zero runoff
        #sel1 = []
        #for i, x in enumerate(srfvec):
        #    if x != 0:
        #        sel1.append(i)
        #sel2 = []
        #for i, x in enumerate(stvec):
        #    if x != 0:
        #        sel2.append(i)
        sel3 = []
        for i, x in enumerate(stvec):
            if x != 0 and srfvec[i] != 0:
                sel3.append(i)

        srfvec = srfvec[sel3]
        stvec = stvec[sel3]
        #print(len(srfvec),int(snx*sny))
        #sellen[yc, xc] = len(sel3)
        
        ## filter 25 % full
        #if (len(sel1) > int(snx*sny)):
        # filter > 20 for meaningful statistics
        if (len(sel3) > 20):
            # linear regression problem
            xr = srfvec
            xr = np.reshape(xr, (len(xr), 1))
            yr = stvec
            #print(xr)
            
            model = LinearRegression().fit(xr, yr)
            r_sq = model.score(xr, yr)
            dvdz = model.coef_[0]
            #print(f"coefficient of determination: {r_sq}")
            #dvardz[y-sny:y+sny,x-snx:x+snx] = dvdz
            #coeff[yc, xc] = r_sq
            if (dvdz < 2):
                dvardz[yc, xc] = dvdz
            else:
                dvdz = 0.

        else:
            dvdz = 0.

# Write out netcdf 
try: outvariable = ds.createVariable('dvardz', 'float',('y','x'))
except: pass
outvariable.units = 'degree/m'
ds['dvardz'][:,:] = dvardz[:,:]

#try: outvariable = ds.createVariable('coeff', 'float',('y','x'))
#except: pass
#outvariable.units = '1'
#ds['coeff'][:,:] = coeff[:,:]
#
#try: outvariable = ds.createVariable('sellen', 'float',('y','x'))
#except: pass
#outvariable.units = '1'
#ds['sellen'][:,:] = sellen[:,:]

try: outvariable = ds.createVariable('x', 'float',('x'))
except: pass
outvariable.units = 'm'
ds['x'][:] = xout[:]

try: outvariable = ds.createVariable('y', 'float',('y'))
except: pass
outvariable.units = 'm'
ds['y'][:] = yout[:]

ds.close()
