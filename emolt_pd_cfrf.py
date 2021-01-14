# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 14:50:26 2021

@author: JiM
routine to process CFRF data given Aubrey's exported xlsx file from mySQL
"""

import pandas as pd
import netCDF4 # used for getting estimated NGDC depths
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime as dt
import warnings
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
from conversions import dd2dm,c2f,m2fth

####HARDCODES####
infile='CFRF_LobsterCrabResearchFleet_TempExample_12_30_20.xlsx'
max_bad_expected=30 #typical max number of haul for the time series
threshold=1.0 # number of STD criteria in "clean_time_series" function
rolling_ave=180 # typically "30" for hourly data but made "180" for 10-minute data
#################

def clean_time_series(FFR,threshold,rolling_ave,max_bad_expected):
      # function to clean time series record of "threshold" times the standard deviations 
      # various methods of despiking are coded but, in Oct 2020, JiM hardcoded the "rolling_median" method
      # borrowed this from "fsrs2emolt.py".
      # Input "FFR" is the raw dataframe that has one column called "temp" and does a 30 pt rolling window check
      # where it returns the same dataframe with a new columns called "temp_despiked" and "temp_roll_med"
      # Modified by JiM in Jan 2021 to require "max_bad_expected" which might be, for example, the # of hauls that might cause a spike in the time series
      FFR['temp_roll_med']=FFR['temp'].rolling(window=rolling_ave,center=True).median().fillna(method='bfill').fillna(method='ffill')
      difference=np.abs(FFR['temp']-FFR['temp_roll_med'])
      outlier_idx=difference > threshold
      FFR['temp_despiked']=FFR['temp']
      FFR['temp_despiked'][outlier_idx]=np.nan
      num_spikes=FFR.temp_despiked.isnull().sum()
      if num_spikes>0:
          print(str(num_spikes)+' spikes removed in 1st pass')
      if num_spikes>max_bad_expected: # likely not to happen in one season so redo with larger threshold
          print('redoing since number of spikes exceeded '+str(max_bad_expected))
          #threshold_new=threshold*2
          threshold_new=threshold
          FFR['temp_roll_med']=FFR['temp_despiked'].rolling(window=rolling_ave,center=True).median().fillna(method='bfill').fillna(method='ffill')
          difference=np.abs(FFR['temp_despiked']-FFR['temp_roll_med'])
          outlier_idx=difference > threshold_new
          #FFR['temp_despiked']=FFR['temp']
          FFR['temp_despiked'][outlier_idx]=np.nan
          num_spikes=FFR.temp_despiked.isnull().sum()
          print(str(num_spikes)+' total spikes removed after 2nd pass')
      return FFR,num_spikes

def get_depth(loni,lati,mindist_allowed):
    # routine to get depth (meters) using vol1 from NGDC
    url='https://www.ngdc.noaa.gov/thredds/dodsC/crm/crm_vol1.nc'
    nc = netCDF4.Dataset(url).variables 
    lon=nc['x'][:]
    lat=nc['y'][:]
    xi,yi,min_dist= nearlonlat_zl(lon,lat,loni,lati) 
    if min_dist>mindist_allowed:
      depth=np.nan
    else:
      depth=nc['z'][yi,xi].data
    return float(depth)#,min_dist

def nearlonlat_zl(lon,lat,lonp,latp): # needed for the next function get_FVCOM_bottom_temp 
    """ 
    used in "get_depth"
    """ 
    # approximation for small distance 
    cp=np.cos(latp*np.pi/180.) 
    dx=(lon-lonp)*cp
    dy=lat-latp 
    xi=np.argmin(abs(dx)) 
    yi=np.argmin(abs(dy))
    min_dist=111*np.sqrt(dx[xi]**2+dy[yi]**2)
    return xi,yi,min_dist

####  MAIN CODE #####
print('loading '+infile+'...')
xl=pd.ExcelFile(infile)
df = {sh:xl.parse(sh) for sh in xl.sheet_names} # creates a nested dataframe of sorts

# form the header dataframe and convert to datetime
dfhead=df['temp_session']
#dfhead['when_start']=pd.to_datetime(dfhead['when_start'],format='%Y-%m-%d %H:%M:%S')
#dfhead['when_end']=pd.to_datetime(dfhead['when_end'],format='%Y-%m-%d %H:%M:%S')
dfhead['in_water']=pd.to_datetime(dfhead['in_water'],format='%Y-%m-%d %H:%M:%S')
dfhead['out_water']=pd.to_datetime(dfhead['out_water'],format='%Y-%m-%d %H:%M:%S')

# form the data dataframe, set date-time as the index, convert to datetime, and rename "temp_c"
dfd=df['temp_sample'].set_index('when_sampled')
dfd.index=pd.to_datetime(dfd.index,format='%Y-%m-%d %H:%M:%S')
dfd=dfd.rename(columns={'temp_c':'temp'})

fout=open(infile[0-4]+'_fixed.dat','w')
fheader=open(infile[0-14]+'_header.dat','w')
# for each session the header dataframe, plot data and save to the output .csv file
#for k in range(len(dfhead)):
for k in [1]:    
    fig, ax = plt.subplots()
    dfds=dfd[dfd['session_id']==dfhead['id'][k]]
    dfds['temp'].plot()
    [dfds,num_spikes]=clean_time_series(dfds,threshold,rolling_ave,max_bad_expected)
    dfds=dfds[(dfds.index>=dfhead['in_water'][k]) & (dfds.index<=dfhead['out_water'][k])]
    dfds['temp_despiked'].plot()
    plt.xlabel('Date') 
    plt.ylabel('degC')
    SN=str(dfhead['logger_id'][k])
    fn='Aubrey'
    ln='Ellertson'
    Sc='CFRF'+str(dfhead['vessel_id'][k]).zfill(2)
    lat,lon=dd2dm(dfhead['latitude'][k],dfhead['longitude'][k])# converts to decimal minutes
    dep_ngdc='%0.1f'%m2fth(get_depth(dfhead['longitude'][k],dfhead['latitude'][k],0.4))
    dep='%0.0f' % float(dfhead['depth'][k]/6.)
    print('NGDC depth='+dep_ngdc+' logged depth='+dep)
    Ps='01'#consecutive time this probe has been deployed
    sal='99.999'# salinity
    plt.title(str(num_spikes)+' spikes removed from vessel #'+str(dfhead['vessel_id'][k])+' (SN='+SN+') in ~'+dep+' fathoms')
    mint=c2f(np.nanmin(dfds['temp'].values))[0]
    maxt=c2f(np.nanmax(dfds['temp'].values))[0]
    ax4=ax.twinx()
    ax4.set_ylabel('degF')
    ax4.set_ylim(mint,maxt)
    plt.show()
    fheader.write(Sc+","+'%0.2f'%lat+","+'%0.2f'%lon+","+dep+","+fn+","+ln+"\n")
    # now loop through data and write out to .dat
    for j in range(len(dfds)):
      dtime=dfds.index[j] 
      yd=(dtime-dt(dtime.year,1,1,0,0,0)).total_seconds()/86400.
      
      fout.write(Sc+","+SN+","+Ps+","+str(dtime)+","+'%0.4f'%(yd)+","+'%0.2f'%dfds['temp_despiked'][j]+","+sal+","+'%0.1f'+dep+"\n")
    fig.savefig(Sc+'_'+str(dfhead['id'][k])+'.png')  
      
      #fout.write(Sc+","+SN[-5:-1]+","+Ps+","+str(dtime)+","+'%0.4f'%(yd)+","+'%0.2f'%c2f(dfd['temp'][j])[0]+","+sal+","+'%0.1f'%dep+"\n"

    
    



