"""
Common functions to be used in the section F. Datetime and Time series

By Daeho Jin
"""

import sys
import os.path
import numpy as np
from datetime import date, datetime, timedelta

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

def get_months(time0,time1,include_end=False):
    """ For given time period,
        return a list of monthly dates
    """
    iyr, imo= time0.year, time0.month
    eyr, emo= time1.year, time1.month
    if iyr==eyr and imo<=emo:
            nmon= emo-imo+int(include_end)
    elif iyr<eyr:
        nmon= (12-imo)+(eyr-iyr-1)*12+emo+int(include_end)
    else:
        sys.exit('time1, {} should be later than time0, {}'.format(time1,time0))

    times=[]
    yr,mm= iyr,imo
    for t in range(nmon):
        times.append(date(yr,mm,15))
        mm+=1
        if mm>12: mm-=12; yr+=1
    return times

def read_qbo_text(infn,tgt_dates):
    tgt_iyr, tgt_eyr= tgt_dates[0].year, tgt_dates[1].year

    with open(infn,'r') as f:
        lines, years=[],[]
        for line in f:
            line= line.strip()
            if len(line)>2 and (line[0:2]=='19' or line[0:2]=='20'):
                years.append(int(line[0:4]))
                ww=[]
                for idx in range(4,len(line),7):
                    ww.append(float(line[idx:idx+7]))
                lines.append(ww)

    iyr,eyr= years[0], years[-1]
    outdata=[]
    undef= lines[-1][-1]
    if iyr>tgt_iyr:
        for yy in range(tgt_iyr,iyr):
            outdata.append([undef,]*12)
    for i,wws in enumerate(lines):
        lyy= years[i]
        if lyy>=tgt_iyr and lyy<=tgt_eyr:
            outdata.append(wws)
    if tgt_eyr>eyr:
        for yy in range(eyr+1,tgt_eyr+1,1):
            outdata.append([undef,]*12)

    outdata= np.asarray(outdata).reshape(-1)
    if tgt_dates[0].month!=1 or tgt_dates[1].month!=12:
        imon= tgt_dates[0].month-1
        emon= tgt_dates[1].month-12
        outdata= outdata[imon:emon] if emon<0 else outdata[imon:]

    return outdata

def read_mjoidx_text(mjo_id,date_range=[],omi_flip=False):
    """
    Read RMM or OMI Index Text file
    fname: include directory
    date_range: start and end dates, including both end dates, optional
    """
    mjo_idx_nm= ['RMM','OMI']
    mjo_idx_fn= ['rmm.74toRealtime.txt','omi.79toRealtime.txt']
    mjo_idx_dir='/Users/djin1/Documents/CLD_Work/Data_Obs/'
    fname= mjo_idx_dir+mjo_idx_fn[mjo_id]

    if not os.path.isfile(fname):
        #print( "File does not exist:"+fname); sys.exit()
        sys.exit("File does not exist: "+fname)

    if len(date_range)!=0 and len(date_range)!=2:
        print("date_range should be [] or [ini_date,end_date]")
        sys.exit()

    mjo_kind= fname.strip().split('/')[-1].split('.')[0]
    if mjo_kind=='rmm':
        nheader=2
        pc_idx= [3,4]
        strs_idx= 6
    elif mjo_kind=='omi':
        nheader=0
        pc_idx= [4,5]
        strs_idx= 6
    else:
        sys.exit("Now only rmm and omi are supported")

    time_info, pcs, strs = [], [], []
    with open(fname,'r') as f:
        for i,line in enumerate(f):
            if i>=nheader:  ### Skip header (2 lines)
                ww=line.strip().split() #
                onedate=date(*map(int,ww[0:3])) ### "map()": Apply "int()" function to each members of ww[0:3]
                if len(date_range)==0 or (len(date_range)==2 and onedate>=date_range[0] and onedate<=date_range[1]):
                    pcs.append([float(ww[k]) for k in pc_idx]) ### PC1 and PC2
                    strs.append(float(ww[strs_idx]))  ### MJO strength
                    #months.append(onedate.month)
                    time_info.append(onedate)  ### Save date-info for displaying time-series

    print("Total {} data record=".format(mjo_idx_nm[mjo_id]),len(strs))
    time_info= np.asarray(time_info)
    pcs= np.asarray(pcs)
    if mjo_id==1 and omi_flip:
        pcs[:,0]*=-1
        pcs= pcs[:,::-1]
    strs= np.asarray(strs)
    return time_info,pcs,strs ### Return as Numpy array

def read_nn34_text(infn,tgt_dates):
    tgt_iyr, tgt_eyr= tgt_dates[0].year, tgt_dates[1].year

    with open(infn,'r') as f:
        lines=[]
        for line in f:
            ww= line.strip().split()
            if len(ww)>0:
                if ww[0][:3]=='-99':
                    undef= float(ww[0])
                    break
                else:
                    lines.append(ww)

    iyr,eyr= map(int,lines[0])
    outdata=[]
    if iyr>tgt_iyr:
        for yy in range(tgt_iyr,iyr):
            outdata.append([undef,]*12)
    for wws in lines[1:]:
        lyy= int(wws[0])
        if lyy>=tgt_iyr and lyy<=tgt_eyr:
            outdata.append([float(val) for val in wws[1:13]])
    if tgt_eyr>eyr:
        for yy in range(eyr+1,tgt_eyr+1,1):
            outdata.append([undef,]*12)

    outdata= np.asarray(outdata).reshape(-1)
    if tgt_dates[0].month!=1 or tgt_dates[1].month!=12:
        imon= tgt_dates[0].month-1
        emon= tgt_dates[1].month-12
        outdata= outdata[imon:emon] if emon<0 else outdata[imon:]

    return outdata

def get_nn34_daily(infn, t_list):
    tdd0= t_list[0]-timedelta(days=16)
    tdd1= t_list[-1]+timedelta(days=16)
    nn34ano= read_nn34_text(infn,(tdd0,tdd1))  # Need buffers before and after the period
    print(nn34ano.shape, nn34ano.mean())

    ms_idx= nn34ano<-99
    if ms_idx.sum()>0:
        sys.exit('Missing data is found!')
        ### Or some treatment needed (removing, duplication, etc.)

    nn34ano_dy= Interp_mon2day(nn34ano,t_list,(tdd0,tdd1))
    return nn34ano_dy

from scipy.interpolate import interp1d
def Interp_mon2day(vals,t_list,val_dates):
    ### Interpolate Monthly data to Daily data
    ### vals: 1-D, wrapping t_list period

    ## First, we need to decide exact time where the monthly data is located
    xx=[]
    iyr,imon= val_dates[0].year, val_dates[0].month
    mdays=0
    for yy in range(iyr,val_dates[1].year+1,1):
        imm=imon if yy==iyr else 1
        for mm in range(imm,13,1):
            mm2, yy2 = mm+1, yy  # Idenfity next month to identify dy_per_mon
            if mm2>12:
                mm2-=12; yy2=yy+1
            dy_per_mon=(date(yy2,mm2,1)-date(yy,mm,1)).days
            xx.append(dy_per_mon/2+0.5+mdays)  # Center of a month's days
            mdays+=dy_per_mon
            if mm==val_dates[1].month and yy==val_dates[1].year: break
    xx=np.asarray(xx)
    print(vals.shape,xx.shape)

    f= interp1d(xx,vals,kind='cubic')  # Set up the interpolation coefficients

    xnew= [(dd-date(iyr,imon,1)).days for dd in t_list]  # Date points to be interpolated
    xnew= np.asarray(xnew)
    f2= f(xnew)
    print(f2.shape)
    return f2