# -*- coding: utf-8 -*-
# emolt2_pd.py this is the Pandas code we use to generate plots for lobstermen
# Written by Yacheng Wang, Jim Manning,
# This is a revision of the old "emolt2.py" which used scikits timeseries

# Note: Beginning in June 2014, this code accesses the ERDDAP server
# so I needed to run merge_emolt_site_sensor.pl after loading the data into NOVA
#
# Note: Beginning in Spring 2017, the Pandas read_csv no longer read ERDDAP urls
# so I manually downloed a csv file using the web interface and called it eMOLT.csv in this directory or the sql directory
#
# Note: In Feb 2020, I added "climatology" to the plot
'''
step0: import modules and hardcodes
step1: read-in data
step2: groupby 'Year'and'Days'
step3: plot figure
'''
#from pydap.client import open_url
from pandas import DataFrame,read_csv,to_datetime
from datetime import datetime as dt, timedelta as td
from matplotlib.dates import num2date
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('xtick', labelsize=14) 
matplotlib.rc('ytick', labelsize=14)
import sys
import matplotlib.dates as dates
#from dateutil import parser
from dateutil.parser import parse
import numpy as np

#from getdata import getemolt_data#####very similar with getemolt_temp
#HARCODES####
site='BN01' # this is the 4-digit eMOLT site code you must know ahead of time
surf_or_bot='bot' #surf, bot, or both
special='NARR' #sites where only the last decade is plotted to prevent clutter like WHAQ, NARR, etc
#############
def getclim(lat,lon,datet):# get CLIM
    dflat=read_csv(clim_files_directory+'LatGrid.csv',header=None)
    dflon=read_csv(clim_files_directory+'LonGrid.csv',header=None)
    bt=read_csv(clim_files_directory+'Bottom_Temperature/BT_'+datet.strftime('%j').lstrip('0')+'.csv',header=None) # gets bottom temp for this day of year with leading zero removed
    latall=np.array(dflat[0])   # gets the first col (35 to 45)
    lonall=np.array(dflon.loc[0])# gets the first row (-75 to -65) changed "ix to "loc" in Feb 2020
    idlat = np.abs(latall - lat).argmin()# finds the nearest lat
    idlon = np.abs(lonall - lon).argmin()# finds the nearest lon
    #print('bottom clim =','%.3f' % bt[idlon][idlat])
    return bt[idlon][idlat]

def get_dataset(url):
    """
    Just checks to see if the OPeNDAP URL is working
    """
    try:
        dataset = open_url(url)
        print url+' is avaliable.'
    except:
        print 'Sorry, ' + url + 'is not available'
        sys.exit(0)
    return dataset
 
def c2f(*c):
    """
    convert Celsius to Fahrenheit
    accepts multiple values
    """
    if not c:
        c = input ('Enter Celsius value:')
        f = 1.8 * c + 32
        return f
    else:
        f = [(i * 1.8 + 32) for i in c]
        return f   

def getemolt_latlon(site):
    """
    get lat, lon, and depth for a particular emolt site 
    """
    import numpy as np
    urllatlon = 'http://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?latitude,longitude,depth&SITE=%22'+str(site)+'%22&distinct()'
    df=read_csv(urllatlon,skiprows=[1])
    dd=max(df["depth (m)"])
    return df['latitude (degrees_north)'][0], df['longitude (degrees_east)'][0], dd

def getobs_tempsalt(site):
    """
    Function written by Jim Manning 
    get data from url, return datetime, temperature, and start and end times
    input_time can either contain two values: start_time & end_time OR one value:interval_days
    and they should be timezone aware 
    example: input_time=[dt(2003,1,1,0,0,0,0,pytz.UTC),dt(2009,1,1,0,0,0,0,pytz.UTC)]
    """
    try:
        url = 'https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&SITE=%22'+str(site)+'%22&orderBy(%22time%22)'
        df=read_csv(url,skiprows=[1])
        df['time']=df['time (UTC)']
        temp=1.8 * df['sea_water_temperature (degree_C)'].values + 32 #converts to degF
        depth=df['depth (m)'].values
        time=[];
        for k in range(len(df)):
            time.append(parse(df.time[k]))
    except:
        df=read_csv('../sql/eMOLT.csv',header=None,delimiter='\s+') # use this option when the ERDDAP-read_csv-method didn't work
        # see the top of emolt_notes for instructions, requires time depth temp header
        #df['sea_water_temperature']=df[5].values
        #df['depth']=df[4].values
        #df['time']=df[1].values
        temp=df[3].values
        depth=df[2].values
        #df['time']=pd.to_datetime(df[0]+" "+df[1])
        print 'converting to datetime'
        time=to_datetime(df[0]+" "+df[1])

    dfnew=DataFrame({'temp':temp,'Depth':depth},index=time)
    return dfnew


#tsoall=getemolt_data(site)
tsoall=getobs_tempsalt(site)

#################add some keys for tso#########################
tsoall['Year']=tsoall.index.year
tsoall['Day']=tsoall.index.dayofyear
if (surf_or_bot=='surf') | (surf_or_bot=='both'):
  tso=tsoall[tsoall['Depth']<np.mean(tsoall['Depth'])]# this grabs surface only
elif surf_or_bot=='bot':
  tso=tsoall[tsoall['Depth']>=0.5*np.nanmean(tsoall['Depth'])]# this 80% grabs
del tso['Depth']  # we do not need depth anymore
if site==special:
  tso=tso[tso['Year']>2000] # since we do not want the plot to be too cluttered
tso1=tso.groupby(['Day','Year']).mean().unstack()

#################create the datetime index#################################
date=[]
for i in range(len(tso1.index)-1):
    date.append(parse(num2date(tso1.index[i]).replace(year=2000).isoformat(" ")))
date.append(parse(num2date(tso1.index[len(tso1.index)-2]).replace(year=2000).isoformat(" ")))
'''
to explain the previous few lines.... 
because tso1.index contain(1-366) so when we convert days to datetime format,366 will become 2000/jan/1,
so we delete the last index 366 and copy the last second record.
'''
############### finally, plot the time series ##############################################################
fig=plt.figure()
ax=fig.add_subplot(111)
ax.plot(date,tso1.values)
ax.set_ylabel('fahrenheit')
ax.set_ylim(np.nanmin(tso1.values),np.nanmax(tso1.values))
#save these values for later incase we need to add other sets
mint=np.nanmin(tso1.values)
maxt=np.nanmax(tso1.values)
for i in range(len(ax.lines)):#plot in different ways
    if i<int(len(ax.lines)/2):# and i<>(len(ax.lines)-1):
        ax.lines[i].set_linestyle('--')
        ax.lines[i].set_linewidth(2)
    elif i>=int(len(ax.lines)/2) and i<(len(ax.lines)-1):
        ax.lines[i].set_linestyle('-')
        ax.lines[i].set_linewidth(2)
    else:
        print str(i)+' years of data'
        ax.lines[-1].set_linewidth(5)
        ax.lines[-1].set_color('black')
#ax.legend(set(tso['Year'].values),loc='center left', bbox_to_anchor=(.1, .6))
#ax.legend(np.sort(list(set(tso['Year'].values))),loc='best')
# Shrink current axis by 20%
box = ax.get_position()
#ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
#ax.legend(np.sort(list(set(tso['Year'].values))),loc='center left',bbox_to_anchor=(1.1, 0.5))#, borderaxespad=0.4)
ax.legend(np.sort(list(set(tso['Year'].values))),loc='best',fontsize=12)#,bbox_to_anchor=(1.1, 0.5))#, borderaxespad=0.4)
#kk=map(str,list(set(tso['Year'].values)))
#kk.append('clim')
#ax.legend(kk,loc='best',fontsize=12)
#ax.legend(map(str,list(set(tso['Year'].values))).append('clim'),loc='best',fontsize=12)

# For case of "both" surface and bottom, we now plot the bottom case
if surf_or_bot=='both':
  tso=tsoall[tsoall['Depth']>=0.8*np.mean(tsoall['Depth'])]# this 80% grabs
  del tso['Depth']  # we do not need depth anymore
  tso1=tso.groupby(['Day','Year']).mean().unstack()
  date=[]
  for i in range(len(tso1.index)-1):
     date.append(parse(num2date(tso1.index[i]).replace(year=2000).isoformat(" ")))
  date.append(parse(num2date(tso1.index[len(tso1.index)-2]).replace(year=2000).isoformat(" ")))
  ax3=fig.add_subplot(111)
  ax3.plot(date,tso1.values,linewidth=1)
  for k in range(len(set(tso['Year'].values))):
     ax3.lines[-k-1].set_linewidth(3) 
  ax3.lines[-1].set_linewidth(5)
  ax3.lines[-1].set_color('black')


ax4=ax.twinx()
#ax4.set_title(site)
ax4.set_ylabel('celsius')
#ax4.set_ylim((np.nanmin(tso1.values)-32)/1.8,(np.nanmax(tso1.values)-32)/1.8)
ax4.set_ylim((mint-32)/1.8,(maxt-32)/1.8)

# here we add the climatology curve by getting a value each month
print 'adding climatology ...'
clim_files_directory='/net/data5/jmanning/clim/'
climt,datett=[],[]
[lat1,lon1,dep]=getemolt_latlon(site)
for k in range(12):
    datett.append(dt(2000,k+1,1,0,0,0))# note that it assumes year 2000
    climt.append(getclim(lat1,lon1,dt(2000,k+1,1,0,0,0)))
datett.append(dt(2001,1,1,0,0,0)) # adds one more point to close out the year
climt.append(climt[0])
ax4.plot(datett,climt,linewidth=4)

'''
below is to format the x-axis
'''
ax.set_xlabel('Month')
#ax.title(site)
ax.set_title(site)
ax.xaxis.set_minor_locator(dates.MonthLocator(bymonth=None, bymonthday=1, interval=1, tz=None))
ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
ax.xaxis.set_major_locator(dates.YearLocator())
ax.xaxis.set_major_formatter(dates.DateFormatter(' '))
patches,labels=ax.get_legend_handles_labels()

plt.show()
if surf_or_bot=='bot':
  plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'.png')
  plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'.ps')
else:
  plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'_'+surf_or_bot+'.png')
  plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'_'+surf_or_bot+'.ps')
