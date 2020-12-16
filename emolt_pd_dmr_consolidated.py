# routine to read in MaineMDR's "consolidated" temperature data and export as eMOLT .dat file as follows:
# MS10,5651,01,2013-06-21 08:07:00,    171.34,     43.81,99.999,26.
#
# Jim Manning March 2017
# modified in Dec 2020 to work in Python 3, deal with 2017-2020 data
import pandas as pd
from conversions import dd2dm,c2f
from datetime import datetime,timedelta
import dateutil.parser as dparser
import numpy as np
import netCDF4

##### FUNCTIONS
def parse(datet):
     dd=dparser.parse(datet)
     return dd
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
#### HARDCODES##############################
# The following three lines were the input in the MArch 2017 code
#dirout='/net/data5/jmanning/tidbit/dmr/'
#in_outputfile='/net/data5/jmanning/tidbit/dmr/2016VTSConsolidatedTemps'
#df=pd.read_csv('/net/data5/jmanning/dmr/2016_VTS_Tidbits.csv') # reads in site information with columns: Fisherman, Onset SN, Date Initialized, Start Recording Date,Start Recording Time,Recording Frequency,Downloaded,Deployment Date,Deployment Time,Retrieval Date,Retrieval Time,Site,Mean Latitude,Mean Longitude,Mean Depth (fm),Depth Stratum (fm),Comments
dirout=''
in_outputfile='VTStemps_locations07_19BPJ120820'# csv file sent from Blaise on 8 Dec 2020 that already has lat/lon
input_header_filename='VTSsites07_19 BPJ_020420.xlsx'
year=2019 #processing one year at a time
mindist_allowed=0.4# minimum distance from nearest NGDC depth in km
################################################

# read input header files
df=pd.read_excel(input_header_filename) # reads in site/header information with columns: Fisherman, Onset SN, Date Initialized, Start Recording Date,Start Recording Time,Recording Frequency,Downloaded,Deployment Date,Deployment Time,Retrieval Date,Retrieval Time,Site,Mean Latitude,Mean Longitude,Mean Depth (fm),Depth Stratum (fm),Comments
# df now has NOAA_SITE', 'LAT', 'LON', 'DEPTH', 'FISHER', 'VTS_SITE', 'Probe #','YEAR']
df=df[df['YEAR']==year]# delimits header to one year

# read data file
print('reading '+in_outputfile+' ...')
dfd=pd.read_csv(in_outputfile+'.csv',parse_dates=['date'],index_col='date',date_parser=parse)
# dfd now has 'ID', 'site', 'year', 'month', 'day', 'yrdy', 'temp', 'lat','lon' with datetime index
dfd=dfd[dfd['year']==year]# data header to one year

# open output files
fout=open(in_outputfile+'_fixed_'+str(year)+'.dat','w')
fheader=open(in_outputfile+'_header_'+str(year)+'.dat','w')
#scodes=['TJ03','TJ04','ID02','SM01','SH01','ID13','SM02','SH02','TO01','BB01','YN01','UP01','TL04','YN02','UP02','TL05']
scodes={'Dustin Delano':'UD','Peter Miller':'ZM','Trevor Jessiman':'RJ','Mike Dawson':'ID','Josh Miller':'SM',\
        'Sam Hyler':'SH','Travis Otis':'TO','BillyBob':'BB','Ryder Noyes':'YN','Justin Papkee':'UP','Terry Lagasse':'TL',\
        'Brian Tripp':'IT','Jordan Drouin':'OD','Joe Locurto':'JL'}
#2017 case    
#inc_start={'Dustin Delano':1,'Peter Miller':1,'Trevor Jessiman':3,'Mike Dawson':14,'Josh Miller':3,\
#        'Sam Hyler':3,'Travis Otis':2,'BillyBob':2,'Ryder Noyes':3,'Justin Papkee':1,'Terry Lagasse':6,
#        'Brian Tripp':1,'Jordan Drouin':9}# incremental site code for this individual determined by lookin at their sites from previous years using "select first)name,last_name from emoltdbs.emolt_site where site like 'XX%';"
#2018 case    
inc_start={'Dustin Delano':3,'Peter Miller':3,'Trevor Jessiman':5,'Mike Dawson':14,'Josh Miller':3,\
        'Sam Hyler':3,'Travis Otis':2,'BillyBob':2,'Ryder Noyes':3,'Justin Papkee':2,'Terry Lagasse':8,
        'Brian Tripp':3,'Jordan Drouin':9}# incremental site code for this individual determined by lookin at their sites from previous years using "select first)name,last_name from emoltdbs.emolt_site where site like 'XX%';"
#2019 case    
inc_start={'Dustin Delano':5,'Peter Miller':5,'Trevor Jessiman':5,'Mike Dawson':14,'Josh Miller':3,\
        'Sam Hyler':3,'Travis Otis':4,'BillyBob':2,'Ryder Noyes':5,'Justin Papkee':4,'Terry Lagasse':10,
        'Brian Tripp':5,'Jordan Drouin':11,'Joe Locurto':1}# incremental site code for this individual determined by lookin at their sites from previous years using "select first)name,last_name from emoltdbs.emolt_site where site like 'XX%';"
# loop through each line in the header file w/fishermen's name  and generate lines in the output header file
fn,ln=[],[]

for k in range(len(df)):
  if np.isnan(df['LAT'].values[k]): # needed this in the case of one record in 2018 where Justin Papkee had no lat/lon
        continue
  [lat,lon]=dd2dm(float(df['LAT'].values[k]),float(df['LON'].values[k]))
  if df['FISHER'].values[k]=='BillyBob': 
     fn='Billy';ln='Bob'
  else:
     [fn,ln]=df['FISHER'].values[k].split()
  inc=inc_start[df['FISHER'].values[k]]+len(list(np.where(df['FISHER'].values[0:k]==df['FISHER'].values[k]))[0])
  #if df['FISHER'].values[k]==df['FISHER'].values[k-1]:
  #        inc=len(np.where(df['FISHER'].values[0:k-1]==df['FISHER'].values[k][0]))+1
  print(scodes[df['FISHER'].values[k]],inc,fn,ln,lat,lon,df['DEPTH'].values[k]) # writing these out in case we already have a site for him
  #Sc=raw_input('4-digit eMOLT sitecode? ')
  Sc=scodes[df['FISHER'].values[k]]+str(inc).zfill(2)
  #Ps=raw_input('Probe setting?')
  Ps='01'
  if Sc=='ID02':
    Ps='02';
  site=str(int(df['VTS_SITE'].values[k]))
  SN=str(df['Probe #'].values[k])
  sal='99.999'
  dep=df['DEPTH'].values[k]
  if np.isnan(dep): # in this where the header file did not have depth, get it from NGDC given position info
      dep=get_depth(df['LON'].values[k],df['LAT'].values[k],mindist_allowed)
  fheader.write(Sc+","+'%0.2f'%lat+","+'%0.2f'%lon+","+'%0.1f'%dep+","+fn+","+ln+","+site+"\n")

  # loop through data and write out to .dat
  for j in range(len(dfd)):
    if dfd['site'][j]==int(site):
      dtime=dfd.index[j] 
      yd=(dtime-datetime(dtime.year,1,1,0,0,0)).total_seconds()/86400.
      fout.write(Sc+","+SN[-5:-1]+","+Ps+","+str(dtime)+","+'%0.4f'%(yd)+","+'%0.2f'%dfd['temp'][j]+","+sal+","+'%0.1f'%dep+"\n")
      #fout.write(Sc+","+SN[-5:-1]+","+Ps+","+str(dtime)+","+'%0.4f'%(yd)+","+'%0.2f'%c2f(dfd['temp'][j])[0]+","+sal+","+'%0.1f'%dep+"\n")
fout.close()
fheader.close()


