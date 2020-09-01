import sys
import os.path
import numpy as np
from datetime import date
from netCDF4 import Dataset

def bin_file_read2mtx(fname, dtype=np.float32):
    """ Open a binary file, and read data
        fname : file name with directory path
        dtype   : data type; np.float32 or np.float64, etc. """

    if not os.path.isfile(fname):
        print("File does not exist:"+fname)
        sys.exit()

    with open(fname,'rb') as fd:
        bin_mat = np.fromfile(file=fd, dtype=dtype)

    return bin_mat

from math import ceil
def lon_deg2x(lon,lon0,dlon):
    '''
    For given longitude information, return index of given specific longitude
    lon: target longitude to be transformed to index
    lon0: the first (smallest) value of longitude grid
    dlon: the increment of longitude grid
    return: integer index
    '''
    x = ceil((lon-lon0)/dlon)
    nx = int(360/dlon)
    if x<0:
        while(x<0):
            x+= nx
    if x>=nx: x=x%nx
    return x
lat_deg2y = lambda lat,lat0,dlat: ceil((lat-lat0)/dlat)

def open_netcdf(fname):
    if not os.path.isfile(fname):
        print("File does not exist:"+fname)
        sys.exit()

    fid=Dataset(fname,'r')
    print("Open:",fname)
    return fid


def read_nc_variable(fid,var_name):
    vdata=fid.variables[var_name][:]
    if vdata.shape[0]==1:  # Same to Numpy.squeeze()
        vdata=vdata.reshape(vdata.shape[1:])
    return vdata

def read_rmm_text(date_range=[]):
    """
    Read RMM Index Text file
    fname: include directory
    date_range: start and end dates, including both end dates, optional
    """
    indir= '../Data/'
    fname= indir+'rmm.74toRealtime.txt'

    if not os.path.isfile(fname):
        #print( "File does not exist:"+fname); sys.exit()
        sys.exit("File does not exist: "+fname)

    if len(date_range)!=0 and len(date_range)!=2:
        print("date_range should be [] or [ini_date,end_date]")
        sys.exit()

    time_info=[]; pcs=[]; phs=[]
    with open(fname,'r') as f:
        for i,line in enumerate(f):
            if i>=2:  ### Skip header (2 lines)
                ww=line.strip().split() #
                onedate=date(*map(int,ww[0:3])) ### "map()": Apply "int()" function to each member of ww[0:3]
                if len(date_range)==0 or (len(date_range)==2 and onedate>=date_range[0] and onedate<=date_range[1]):
                    pcs.append([float(ww[3]),float(ww[4])]) ### RMM PC1 and PC2
                    phs.append(int(ww[5]))  ### MJO Phase
                    time_info.append(onedate)  ### Save month only

    print("Total RMM data record=",len(phs))
    time_info, pcs, phs= np.asarray(time_info),np.asarray(pcs),np.asarray(phs) ### Return as Numpy array
    strs= np.sqrt((pcs**2).sum(axis=1))  # Euclidean distance

    ### Check missing
    miss_idx= phs==999
    if miss_idx.sum()>0:
        print("There are {} missing(s)".format(miss_idx.sum()))
    else:
        print("No missings")

    return time_info, pcs, phs, strs, miss_idx

def read_sst_from_HadISST(yrs=[2015,2019]):
    ###--- Parameters
    indir= '../Data/'
    yrs0= [2015,2019]
    lon0,dlon,nlon= -179.5,1.,360
    lat0,dlat,nlat=  -89.5,1.,180
    mon_per_yr= 12
    nt= (yrs0[1]-yrs0[0]+1)*mon_per_yr

    infn= indir+"HadISST1.sample.{}-{}.{}x{}x{}.f32dat".format(*yrs,nt,nlat,nlon)
    sst= bin_file_read2mtx(infn)  # 'dtype' option is omitted because 'f32' is basic dtype
    sst= sst.reshape([nt,nlat,nlon]).astype(float)  # Improve precision of calculation

    it= (yrs[0]-yrs0[0])*mon_per_yr
    nmons= (yrs[1]-yrs[0]+1)*mon_per_yr
    sst= sst[it:it+nmons,:,:]
    print(sst.shape)

    ### We already know that missings are -999.9, and ice-cover value is -10.00.
    miss_idx= sst<-9.9
    sst[miss_idx]= np.nan

    lats= dict(lat0=lat0,dlat=dlat,nlat=nlat)
    lons= dict(lon0=lon0,dlon=dlon,nlon=nlon)
    return sst, lats,lons


def bar_x_locator(width,data_dim=[1,10]):
    """
    Depending on width and number of bars,
    return bar location on x axis
    Input width: (0,1) range
    Input data_dim: [# of vars, # of bins]
    Output locs: list of 1-D array(s)
    """
    xx=np.arange(data_dim[1])
    shifter= -width/2*(data_dim[0]-1)
    locs=[]
    for x1 in range(data_dim[0]):
        locs.append(xx+(shifter+width*x1))
    return locs

def write_val(ax,values,xloc,yloc,crt=0,ha='center',va='center'):
    """
    Show values on designated location if val>crt.
    Input values, xloc, and yloc should be of same dimension
    """
    ### Show data values
    for val,xl,yl in zip(values,xloc,yloc):
        if val>crt: # Write large enough numbers only
            pctxt='{:.0f}%'.format(val)
            ax.text(xl,yl,pctxt,ha=ha,va=va,stretch='semi-condensed',fontsize=10)
    return

from matplotlib.ticker import MultipleLocator, FixedLocator
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
def map_common(ax,subtit,proj,gl_lab_locator=[False,True,True,False],yloc=10,xloc=30,lon_range=[-180,179]):
    """ Decorating Cartopy Map
    """
    ### Title
    ax.set_title(subtit,fontsize=13,ha='left',x=0.0)
    ### Coast Lines
    ax.coastlines(color='0.5',linewidth=1.)
    ### Grid Lines
    # Trick to draw grid lines over dateline; not necessary in Cartopy 0.18.0 or later
    gl= ax.gridlines(crs=proj, draw_labels=False,
                    linewidth=0.6, color='gray', alpha=0.5, linestyle='--')
    gl.xlocator = MultipleLocator(xloc)
    gl.ylocator = MultipleLocator(yloc)

    gl= ax.gridlines(crs=proj, draw_labels=True,
                    linewidth=0.6, color='gray', alpha=0.5, linestyle='--')

    ### x and y-axis tick labels
    gl.xlabels_top,gl.xlabels_bottom,gl.ylabels_left,gl.ylabels_right = gl_lab_locator
    #gl.xlocator = MultipleLocator(xloc)
    lon_locs= np.arange(np.ceil(lon_range[0]/xloc)*xloc,lon_range[1]+0.01,xloc)
    lon_locs[lon_locs>180]-=360
    gl.xlocator = FixedLocator(lon_locs)  # Test: [120,180,240,300]

    #gl.xlocator = FixedLocator(range(-180,180,xloc))
    gl.ylocator = MultipleLocator(yloc)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 10, 'color': 'k'}
    gl.ylabel_style = {'size': 10, 'color': 'k'}
    ### Aspect ratio of map
    ax.set_aspect('auto') ### 'auto' allows the map to be distorted and fill the defined axes
    return

def draw_colorbar(fig,ax,pic1,type='vertical',size='panel',gap=0.06,width=0.02,extend='neither'):
    '''
    Type: 'horizontal' or 'vertical'
    Size: 'page' or 'panel'
    Gap: gap between panel(axis) and colorbar
    Extend: 'both', 'min', 'max', 'neither'
    '''
    pos1=ax.get_position().bounds  ##<= (left,bottom,width,height)
    if type.lower()=='vertical' and size.lower()=='page':
        cb_ax =fig.add_axes([pos1[0]+pos1[2]+gap,0.1,width,0.8])  ##<= (left,bottom,width,height)
    elif type.lower()=='vertical' and size.lower()=='panel':
        cb_ax =fig.add_axes([pos1[0]+pos1[2]+gap,pos1[1],width,pos1[3]])  ##<= (left,bottom,width,height)
    elif type.lower()=='horizontal' and size.lower()=='page':
        cb_ax =fig.add_axes([0.1,pos1[1]-gap,0.8,width])  ##<= (left,bottom,width,height)
    elif type.lower()=='horizontal' and size.lower()=='panel':
        cb_ax =fig.add_axes([pos1[0],pos1[1]-gap,pos1[2],width])  ##<= (left,bottom,width,height)
    else:
        print('Error: Options are incorrect:',type,size)
        return

    cbar=fig.colorbar(pic1,cax=cb_ax,extend=extend,orientation=type)  #,ticks=[0.01,0.1,1],format='%.2f')
    cbar.ax.tick_params(labelsize=10)
    return cbar