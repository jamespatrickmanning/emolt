# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 10:14:06 2011
This program was written after an request from Bill Adler, then president of the Mass Lobstermen, where he wanted to see temperatures in relation to historical records of each lobstermen.
@author: jmanning

IMPORTANT: This assumes you have previously run an old perl routine called "getts_adler_1site.plx" which outputs ALL the data for that site

Modifications made March 2020 to add shipboard climatology as blue line.
"""
from pandas import read_csv
import numpy as np
import matplotlib.mlab as ml
import matplotlib.pyplot as plt
from matplotlib.dates import num2date,MonthLocator, WeekdayLocator, DateFormatter,MONDAY
import datetime as dt
#from ocean_JiM import *
from conversions import f2c
import os

print "assumes './getts_adler_1site.plx site_id depth' has been run"

#t=ml.load('/net/home3/ocn/jmanning/sql/this2.dat') # abandoned this load method in 2016 when EPD2.7 python no longer worked w/new Linux
t=read_csv('/net/home3/ocn/jmanning/sql/this2.dat',delimiter=r"\s+",header=None)
lat=t[0]
lon=t[1]
wd=t[2]
yr=t[4]
yd=t[5]
temp=t[6]
depth=t[3][0]

# define a few variables to annotate figure
#site=raw_input('What site code? ')
site='BN01'
relyear=0 #set to zero for max year, 1 for previous year
numyrs=str(len(set(yr)))

mondays   = WeekdayLocator(MONDAY) # every monday
months    = MonthLocator()# every month
mondaysFmt = DateFormatter('%d')
#monthsFmt = DateFormatter('%Y-%m-%d %H:%M:%S')
monthsFmt = DateFormatter('%b')

def getemolt_latlon(site):
    """
    get lat, lon, and depth for a particular emolt site 
    """
    import numpy as np
    urllatlon = 'http://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?latitude,longitude,depth&SITE=%22'+str(site)+'%22'#&distinct()'
    df=read_csv(urllatlon,skiprows=[1])
    #dd=max(df["depth (m)"])
    return df['latitude (degrees_north)'][0], df['longitude (degrees_east)'][0]

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


# calculate min, max, and mean for each yearday
ta,tmin,tmax,tstdp,tstdm,ydg=[],[],[],[],[],[]
yda=np.array(yd)
for k in range(1,365):
  if list(temp[(yda>k-1)&(yda<=k)]):
    ydg.append(num2date(k).replace(2012)) #yearday with good data  
    ta.append(np.mean(temp[(yda>k-1)&(yda<=k)]))
    tstdp.append(ta[-1]+np.std(temp[(yda>k-1)&(yda<=k)]))
    tstdm.append(ta[-1]-np.std(temp[(yda>k-1)&(yda<=k)]))
    tmin.append(np.min(temp[(yd>k-1)&(yd<=k)]))
    tmax.append(np.max(temp[(yd>k-1)&(yd<=k)]))

#  calculate min, max, and mean for this most recent year 
tnowa,ydnowg=[],[]
print np.max(yr)
tnow=temp[yr.values==np.max(yr)-relyear].values
ydnow=yda[yr.values==np.max(yr)-relyear]
for k in set(ydnow.astype(int)):
    if [(ydnow>k-1)&(ydnow<=k)]:
      tnowa.append(np.nanmean(tnow[(ydnow>k-1)&(ydnow<=k)]))
      #ydnowg.append(num2date(k+1).replace(year=int(np.max(yr))))
      ydnowg.append(num2date(k+1).replace(year=2012))
 
# calculate polygon of temperature range
polyx=ydg
polyy=tmin
for k in range(len(ydg),-1,-1):
  polyx.append(ydg[k-1])
  polyy.append(tmax[k-1])
polyx.append(ydg[0])
polyy.append(tmin[0]) 

ydg=[]# had to redo this for some reason
for k in range(1,365):
  if list(temp[(yda>k-1)&(yda<=k)]):
    ydg.append(num2date(k).replace(2012)) #yearday with good data
    
# plot results
fig=plt.figure(1)
ax1 = fig.add_subplot(111)
ax1.fill(polyx,polyy,'0.75',edgecolor='none',label=numyrs+' Year Range')
ax1.plot(ydg,ta,'-',color='k',linewidth=3,label=numyrs+' Year Mean & Std')
ax1.plot(ydg,tstdp,'--',color='k',linewidth=3)
ax1.plot(ydg,tstdm,'--',color='k',linewidth=3)
ax1.plot(ydnowg,tnowa,'-',color='r',linewidth=3,label=str(int(np.max(yr)-relyear)))
#ax1.plot(ydnowg,tnowa,'-',color='r',linewidth=3,label=str(2013))
ax1.set_xlim(min(ydg),max(ydg))
ax1.set_ylim(min(tmin),max(tmax))
plt.legend(loc='best') 
if depth==1:
  dd='_surf'
else:
  dd=''
plt.title(site+dd+' daily averages (with 30 year research vessel climatology in blue)')
#plt.title('OC01 at 77 meters SNE Shelf')
ax1.grid(True)

c=ax1.axis()
ax2 = ax1.twinx()
ax2.set_ylabel('Celsius')
ax2.axis(ymin=f2c(c[2])[0],ymax=f2c(c[3])[0])
ax2.set_xlim(min(ydg),max(ydg))

# here we add the climatology curve by getting a value each month
print 'adding climatology ...'
clim_files_directory='/net/data5/jmanning/clim/'
climt,datett=[],[]
[lat1,lon1]=getemolt_latlon(site)
for k in range(12):
    datett.append(dt.datetime(2012,k+1,1,0,0,0))# note that it assumes year 2012
    climt.append(getclim(lat1,lon1,dt.datetime(2012,k+1,1,0,0,0)))
datett.append(dt.datetime(2013,1,1,0,0,0)) # adds one more point to close out the year
climt.append(climt[0])
ax2.plot(datett,climt,linewidth=4)

ax1.xaxis.set_major_locator(months)
ax1.xaxis.set_major_formatter(monthsFmt)
ax1.xaxis.set_minor_formatter(mondaysFmt) 

plt.show()

print "saving plot _raw file... "

plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'_ba_'+str(int(np.max(yr)-relyear))+dd+'.png')
plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'_ba_'+str(int(np.max(yr))-relyear)+dd+'.ps')# for postscript
#os.system('lpr /net/nwebserver/epd/ocean/MainPage/lob/'+site+'_ba_'+str(int(np.max(yr)))+dd+'.ps')
