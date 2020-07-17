# -*- coding: utf-8 -*-
'''
Created on Wed Jan 23 11:37:52 2013

@author: jmanning and Yacheng

Jan 2013
this program can read-in different formats files and plot 'Temp-TIME'or'Sali-TIME'or'Inti-TIME'figure, at the mean time generate output file.
step1:read-in data through 'pandas' using different loops depending on what type of data it is
step2:choose the approximate start-end points
step3:zoom-in the start-end figure and choose the exactly points
step4:show the final figure and generate the output file.

Nov 2015
added StarOddi data input option
Dec 2015
added Onset data input option (MX1101)
'''
import pylab
from pylab import *
import matplotlib.pyplot as plt
from pandas import *
import numpy as np
import datetime
from datetime import timedelta,datetime
from matplotlib.dates import num2date,date2num
import csv
import sys
sys.path.append('/net/home3/ocn/jmanning/py/mygit/modules') # this is where I store homegrown modules
from conversions import c2f,f2c
from utilities import my_x_axis_format
from mpl_toolkits.axes_grid1 import host_subplot
import string
import matplotlib.dates as dates
from matplotlib import mlab as ml

############## HARDCODES ##############
probe_type='minilog'
#Sc=raw_input("please input the sitecode:")
#dep=raw_input("please input the depth (fathoms) of instrument:")
#Ps=raw_input("please input the probsetting:")
#Sn=raw_input("please input the sErname:")
#diroutplt='/net/nwebserver/epd/ocean/MainPage/lob/'
diroutplt='/net/pubweb_html/epd/ocean/MainPage/lob/'
dirout='/net/data5/jmanning/'+probe_type+'/dat/'
#dirout='/net/data5/jmanning/minilog/dat/'
#dirout='/net/data5/jmanning/onset/dat/'
#dirout='/net/data5/jmanning/calprobe/mar13/'
#dirout='/net/data5/jmanning/hobo/'
#dirout='/net/data5/jmanning/staroddi/dat/'
#fn='Temp_Logger_Mar_to_Oct_2017.txt'
#fn='Data_Points_for_July-Nov_2015_Temp_Pressure_Logger.csv'
fn='mbn0118.csv'
direct='/net/data5/jmanning/'+probe_type+'/asc/'
#direct='/net/data5/jmanning/onset/'
#direct='/net/data5/jmanning/minilog/asc/'
#direct='/net/data5/jmanning/staroddi/'
#direct='/net/data5/jmanning/hobo/'
#direct='/net/home3/ocn/jmanning/py/yw/emolt/rawdata/'
#direct='/net/data5/jmanning/calprobe/mar13/'
Sc=fn[1:3].upper()+fn[3:5] # site code
#Sc='NARR'
dep='20' # fathoms
crit=1.0# number of standard deviations to check on 1 hour spikes
minsalt=20.0 # minimum allowable salinity
maxsalt=30.0
#Ps='99'
#Ps='01'
Ps=fn[5:7] # this is the "probe setting" or the consecutive time a probe was deployed at the site
#Ps=fn[10:14]

############ define a def######################
def chooseSE(start,end,skipr):#this function employed to zoom-in picture and choose exactly points
      '''
      def parse(datet):
        #print datet[0:10],datet[11:13],datet[14:16]
        dt=datetime.strptime(datet[0:10],'%Y-%m-%d')# normal format
        #dt=datetime.strptime(datet[0:10],'%d-%m-%Y') # Jerry Prezioso format
        delta=timedelta(hours=int(datet[11:13]),minutes=int(datet[14:16]))
        return dt+delta
      ''' 
      # JiM changes made 7/1020 to work with bn0118 file
      def parse(datet,hhmm):#added ',hhmm'
        dt=datetime.strptime(datet[0:10],'%m/%d/%Y')# 7/10/20 change
        split_hhmm=hhmm.split(':')
        delta=timedelta(hours=int(split_hhmm[0]),minutes=int(split_hhmm[1]))#7/10/20 change
        return dt+delta
      if num2date(end[0])-num2date(start[0])<timedelta(days=1):
        startfront=start[0]-.2 # looking 2 day either side of the point clicked
        startback=start[0]+.2
        inc=0.2
        sfforplot=(num2date(startfront)).isoformat(" ")
        sbforplot=(num2date(startback)).isoformat(" ")
      else:     
        startfront=start[0]-2 # looking 2 day either side of the point clicked
        startback=start[0]+2
        inc=2
        sfforplot=(num2date(startfront)).replace(minute=0,second=0,microsecond=0).isoformat(" ")#transfer number to date and generate a appropriate date format
        sbforplot=(num2date(startback)).replace(minute=0,second=0,microsecond=0).isoformat(" ")
      ZIF=df[sfforplot[0:19]:sbforplot[0:19]]#get the DataFrame for zoom-in figure.
      fig = plt.figure()
      plt.plot(ZIF.index.to_pydatetime(),ZIF.values)
      #sfinal=pylab.ginput(n=1)#choose an exactly point.
      sfinal=ginput(n=1)#choose an exactly point.
      sfinaltime=(num2date(sfinal[0][0])).replace(tzinfo=None)
      if inc>1:
        sfinalforplot=sfinaltime.replace(minute=0,second=0,microsecond=0).isoformat(" ") # 2/20
      else:
        sfinalforplot=sfinaltime.isoformat(" ")
      print sfinalforplot
      plt.clf()
     #####for end point zoom figure###########
      #below coding is very similar with the up one, it employed to choose exactly point at the end side.
      endfront=end[0]-inc # looking 2 day either side of the point clicked
      endback=end[0]+inc
      if inc>1:
        efforplot=(num2date(endfront)).replace(minute=0,second=0,microsecond=0).isoformat(" ")
        ebforplot=(num2date(endback)).replace(minute=0,second=0,microsecond=0).isoformat(" ")
      else:
        efforplot=(num2date(endfront)).isoformat(" ")
        ebforplot=(num2date(endback)).isoformat(" ")        
      ZIB=df[efforplot[0:19]:ebforplot[0:19]]
      fig = plt.figure()
      plt.plot(ZIB.index.to_pydatetime(),ZIB.values)
      efinal=ginput(n=1)
      efinaltime=(num2date(efinal[0][0])).replace(tzinfo=None)
      if inc>1:
        efinalforplot=efinaltime.replace(minute=0,second=0,microsecond=0).isoformat(" ")
      else:
        efinalforplot=efinaltime.isoformat(" ")
      print efinalforplot
      plt.clf()
     ######for the final figure################
      FF=df[sfinalforplot:efinalforplot]#FF is the DataFrame that include all the records you choosed to plot.
      criteria=crit*FF.values.std() # standard deviations
      # criteria=FF.values.std()
      a=0
      for i in range(len(FF)-2):#replace the record value which exceed 3 times standard deviations by 'Nan'.
         diff1=abs(FF.values[i+1]-FF.values[i])
         diff2=abs(FF.values[i+2]-FF.values[i+1])
         #print 'diff1'+str(diff1)+' diff2='+str(diff2)
         if diff1[0] > criteria and diff2[0] > criteria:
                print str(FF.index[i])+ ' is replaced by Nan'
                a+=1
                FF.values[i+1]=float('NaN')
      print 'There are ' +str(a)+ ' points have replaced'
      print mark,mark1
      #variables=['Date','Time','RawTemp','Depth']# Staroddi case??
      #variables=['Date','Time','RawTemp'] # 7/17/20 commented out for the following
      variables=['Date','Time','Temp']
      if mark=='*' or mark=='S' and mark2!='e':
          dt=read_csv(direct+fn,sep=',',skiprows=skipr,parse_dates={'datet':[0,1]},index_col='datet',date_parser=parse,names=['Date','Time','Temp'])#creat a new Datetimeindex
          #dt=read_csv(direct+fn,sep=',',skiprows=skipr,parse_dates={'datet':[0,1]},index_col='datet',date_parser=parse,names=variables)#creat a new Datetimeindex
          #dt=dt.drop('Depth',1)     
      elif mark=='S' and mark2=='e': # note that we had to do some special processing
          variables=['Date','RawTemp','Dum1','Dum2','Dum3','Dum4','Dum5']
          dt=read_csv(direct+fn,sep=',',skiprows=3,header=None,parse_dates={'datet':[0]},index_col='datet',date_parser=parse,names=variables)
          id=list(where(dt['RawTemp']!=' ')[0]) # finds rows where no temperature is reported
          dt=dt['RawTemp'][id] # df becomes a series
          dt=dt.to_frame() # back to frame
          tt=[]
          for k in range(len(dt)):
             tt.append(f2c(float(dt['RawTemp'][k]))[0]) # convert to Celcius in ONSET case
          dt['RawTemp']=tt
      elif mark=='P': # case of MX2204
          variables=['Dum','Date','Temp']
          dt=read_csv(direct+fn,sep=',',skiprows=2,header=None,parse_dates={'datet':[1]},index_col='datet',date_parser=parse,names=variables)
          dt=dt.drop('Dum',axis=1)# just gets rid of the 1st column
          tt=[]
          for k in range(len(dt)):
             tt.append(f2c(float(dt['Temp'][k]))[0]) # convert to Celcius in ONSET case
          dt['Temp']=tt
      elif mark1=='Intensity':
          dr=read_csv(direct+fn,sep=',',skiprows=2,parse_dates={'datet':[1]},index_col='datet',names=['NO','DataTime','RawTemp','Intensity','CouplerDetached','CouplerAttached','Stopped','EndOfFile'])
          dt=DataFrame(dr['RawTemp'],index=dr.index)
      elif mark=='#': # JiM added this in Nov 2017
         def parse(datet):
            dt=datetime.strptime(datet[0:16],'%d.%m.%y %H:%M:%S') # Jerry Prezioso format
            return dt
         dt=read_csv(direct+fn,sep='\t',skiprows=15,parse_dates={'datet':[1]},index_col='datet',date_parser=parse,names=['Dummy','Datetime','Temp','Depth'])
         temp=[]
         for k in range(len(dt)):
            tt=float(dt.Temp[k].replace(',','.'))
            temp.append(tt)
         dt['RawTemp']=temp
         dt=DataFrame(dt['RawTemp'],index=dt.index)
      else:
         #dr=read_csv(direct+fn,sep=',',skiprows=2,parse_dates={'datet':[1]},index_col='datet',names=['NO','DataTime','CondHighRng','RawTemp','Salinity','CouplerDetached','CouplerAttached','Stopped','EndOfFile'])
          dr=read_csv(direct+fn,sep=',',skiprows=2,parse_dates={'datet':[1]},index_col='datet',names=['NO','DataTime','CondHighRng','RawTemp','SpecConduct','Salinity','CouplerDetached','CouplerAttached','Stopped','EndOfFile'])
          dt=DataFrame(dr['RawTemp'],index=dr.index)
      draw=dt[sfinalforplot:efinalforplot]
      #print draw.values
      fig=plt.figure(figsize=(8,5))
      #TimeDelta=FF.index[-1]-FF.index[0]  2/20
      ax = fig.add_subplot(111)
      #my_x_axis_format(ax, TimeDelta)     2/20
      ax.set_ylim(min(FF.values),max(FF.values))
      ax.plot(draw.index.to_pydatetime(),draw.values,color='r',label="raw data")
      ax.set_ylabel('celsius')
      ax.xaxis.set_major_formatter(dates.DateFormatter('%M'))
      mins = dates.MinuteLocator(interval = 20)# 2/20
      m_fmt = dates.DateFormatter('%H:%M')# 2/20
      ax.xaxis.set_major_locator(mins)# 2/20
      ax.xaxis.set_major_formatter(m_fmt)# 2/20
      #fig.autofmt_xdate() #                2/20
      if FF.index[0].year<FF.index[-1].year:
         year=str(int(FF.index[0].year))+'-'+str(int(FF.index[-1].year))
      else:
         year=str(int(FF.index[0].year))
      if FF.index[-1]-FF.index[0]<timedelta(days=1):
        ax.set_xlabel(str(FF.index[0].month)+'/'+str(FF.index[0].day)+'/'+str(year))
      else:
        ax.set_xlabel(year)
      #ax.set_xlabel('Feb 9th, 2020') # 2/20
      #FT=[]
      # for k in range(len(FF.index)):#convert C to F
      #print type(FF),FF
      #FT=c2f(FF['tf'])
      FT=c2f(FF['Temp'])
      #FT.append(f)
      ax2=ax.twinx()
      #my_x_axis_format(ax2, TimeDelta) 2/20
      #print FT.min(0)
      ax2.set_ylim(min(FT[0]),max(FT[0]))
      ax2.plot(FT[0].index.to_pydatetime(),FT[0],color='b',label="clean data")
      ax2.set_ylabel('fahrenheit')
      #ax.xaxis.set_major_formatter(dates.DateFormatter('%M'))
      #fig.autofmt_xdate() #            2/20
      lines, labels = ax.get_legend_handles_labels()
      lines2, labels2 = ax2.get_legend_handles_labels()
      ax2.legend(lines + lines2, labels + labels2, loc=0)
      plt.show()
      # plt.tight_layout()
      return FF,FT
      
def chooseSE2(start,end):#this function employed to zoom-in picture and choose exactly points (only used in case of salinity present)
      startfront=start[0]-2 # looking 2 day either side of the point clicked
      startback=start[0]+2
      sfforplot=(num2date(startfront)).replace(minute=0,second=0,microsecond=0).isoformat(" ")#transfer number to date and generate a appropriate date format
      sbforplot=(num2date(startback)).replace(minute=0,second=0,microsecond=0).isoformat(" ")
      ZIF=df[sfforplot[0:19]:sbforplot[0:19]]#get the DataFrame for zoom-in figure.
      fig = plt.figure()
      plt.plot(ZIF.index.to_pydatetime(),ZIF.values)
      #sfinal=pylab.ginput(n=1)#choose an exactly point.
      sfinal=ginput(n=1)#choose an exactly point.
      sfinaltime=(num2date(sfinal[0][0])).replace(tzinfo=None)
      sfinalforplot=sfinaltime.replace(minute=0,second=0,microsecond=0).isoformat(" ")
      print sfinalforplot
      #plt.close()
      plt.clf()
      #####for end point zoom figure###########
      #below coding is very similar with the up one, it employed to choose exactly point at the end side.
      endfront=end[0]-2 # looking 2 day either side of the point clicked
      endback=end[0]+2
      efforplot=(num2date(endfront)).replace(minute=0,second=0,microsecond=0).isoformat(" ")
      ebforplot=(num2date(endback)).replace(minute=0,second=0,microsecond=0).isoformat(" ")
      ZIB=df[efforplot[0:19]:ebforplot[0:19]]
      fig = plt.figure()
      plt.plot(ZIB.index.to_pydatetime(),ZIB.values)
      efinal=ginput(n=1)
      efinaltime=(num2date(efinal[0][0])).replace(tzinfo=None)
      efinalforplot=efinaltime.replace(minute=0,second=0,microsecond=0).isoformat(" ")
      print efinalforplot
      #plt.close()
      plt.clf()
      ######for the final figure################
      FF=df[sfinalforplot:efinalforplot]#FF is the DataFrame that include all the records you choosed to plot.
      criteria=crit*FF.values.std() # standard deviations
      #print criteria
      a=0
      print FF.values[1],FF.values[0]
      for i in range(len(FF)-2):#replace the record value which exceed 3 times standard deviations by 'Nan'.
         diff1=abs(FF.values[i+1]-FF.values[i])
         diff2=abs(FF.values[i+2]-FF.values[i+1])
         if (diff1 > criteria) and (diff2 > criteria):
              print str(FF.index[i])+ ' is replaced by Nan'
              a+=1
              FF.values[i+1]=float('NaN')
         if i==0:
             print 'now '+str(diff1)
         if (diff1 >criteria) and (i==0):       
              print str(FF.index[i])+ ' is replaced by Nan'
              a+=1
              FF.values[i]=float('NaN')
         if  FF.values[i]<minsalt:
             FF.values[i]=float('NaN')
         if  FF.values[i]>maxsalt:
             FF.values[i]=float('NaN')
      print 'There are ' +str(a)+ ' points have replaced'
      fig=plt.figure(figsize=(8,5))
      TimeDelta=FF.index[-1]-FF.index[0]
      ax = fig.add_subplot(111)
      my_x_axis_format(ax, TimeDelta)
      ax.set_ylim(min(FF['Salinity'].values),max(FF['Salinity'].values))
      ax.plot(FF.index.to_pydatetime(),FF.values,color='r',label="raw data")
      ax.set_ylabel('Salinity')
      #ax.set_ylim(min(FF['Intensity'].values),max(FF['Intensity'].values))
      #ax.plot(FF.index.to_pydatetime(),FF.values,color='r',label="raw data")
      #ax.set_ylabel('Intensity')
      if FF.index[0].year<FF.index[-1].year:
         year=str(int(FF.index[0].year))+'-'+str(int(FF.index[-1].year))
      else:
         year=str(int(FF.index[0].year))
      ax.set_xlabel(year)
      #FF.plot()
      return FF
def getyearday(FF):#generating 'yd1' which is a number from 0-366.
      y=[]
      m=[]
      d=[]
      hh=[]
      mm=[]
      yd=[]
      #for i in range(len(FF[0])):#get the separate year,month,day,hour,minute
      for i in range(len(FF)):#get the separate year,month,day,hour,minute
          #strindex=str(FF.index[i])
          strindex=str(FF.index[i])
          y.append(strindex[0:4])
          m.append(strindex[5:7])
          d.append(strindex[8:10])
          hh.append(strindex[11:13])
          mm.append(strindex[14:16])
      for j in range(len(FF)):#minus to get the number 0-366
          a=date2num(datetime(int(y[j]),int(m[j]),int(d[j]),int(hh[j]),int(mm[j])))
          b=date2num(datetime(int(y[j]),1,1,0,0))
          yd.append(a-b)
      del y,m,d,hh,mm
      return yd
def outfomat(PFDATA):#generating the format of output file
      output_fmt=['sitecode','sernum','probsetting','Datet','yearday','Temp','Salinity','depth']
      PFDATADF=DataFrame(PFDATA)#convert Series to DataFrame
      PFDATADFNEW=PFDATADF.reindex(columns=output_fmt)
      # PFDATADFNEW.to_csv(fn[0:-4]+'.csv',float_format='%10.2f',index=False)
      print "output file is ready!"
      return PFDATADFNEW
def saveTemFig(diroutplt):
     plt.savefig(diroutplt+fn[0:-4]+'.png')
     plt.savefig(diroutplt+fn[0:-4]+'.ps')
#################################################################################################
f=open(direct+fn)
print direct,fn
lines=f.readlines()
#Note: by reading the first line, we detect what type of data it is and the specific format expected to follow
mark=lines[0][0]
mark2=lines[0][1]
mark1=lines[1][39:48]
Sn=lines[1][18:22]# changed from 16:20 on oct 27, 2016 and again on may 2, 2017
#Sn=lines[1][19:23] # needed this for logger 6032 on Dec 13, 2018
#Sn=lines[1][16:20]# changed from [18:22] on Nov 6, 2017 when reading an old probe
print Sn
print lines[1][:]
#Sn=lines[1][16:20]# changed temporarlity back to 16:20 on Jan 23, 2017 for cases of old loggers
Sn1=lines[0][17:21] #
Sn2=lines[0][13:21]
if mark=='*' or mark=='S' and mark2!='e':#if the input file start with the character '*',choose the first (most common) method to read-in data.
      # JiM changes made 7/1020 to work with bn0118 file
      def parse(datet,hhmm):#added ',hhmm'
        #print datet[0:10],datet[11:13],datet[14:16]
        #dt=datetime.strptime(datet[0:10],'%Y-%m-%d')# normal format
        dt=datetime.strptime(datet[0:10],'%m/%d/%Y')# 7/10/20 change
        #dt=datetime.strptime(datet[0:10],'%d-%m-%Y') # Jerry Prezioso format
        #delta=timedelta(hours=int(datet[11:13]),minutes=int(datet[14:16]))
        #print hhmm
        split_hhmm=hhmm.split(':')
        #delta=timedelta(hours=int(hhmm[0:2]),minutes=int(hhmm[3:5]))#7/10/20 change
        delta=timedelta(hours=int(split_hhmm[0]),minutes=int(split_hhmm[1]))#7/10/20 change
        return dt+delta
      variables=['Date','Time','Temp']
      if mark=='*': # case of old minilog program output
          skipr=7
          print 'old minilog output'
      else: # case of new LoggerVue output
          skipr=8
          if lines[1][15:25]=='Minilog-II':
             Sn=lines[1][30:34]
          elif lines[1][15:25]=='Minilog-TD':
             Sn=lines[1][26:30]
             variables=['Date','Time','Temp','Depth']
          else:   
             Sn=lines[1][25:29] # serieal number is reassigned  uncommented mAR 28, 2017 FOR SPECIAL CASE OF 2013 dmr
             #Sn=lines[1][30:34] # serieal number is reassigned
      print 'Sn='+Sn
      df=read_csv(direct+fn,sep=',',skiprows=skipr,parse_dates={'datet':[0,1]},index_col='datet',date_parser=parse,names=['Date','Time','Temp'])#creat a new Datetimeindex
      #df=read_csv(direct+fn,sep=',',skiprows=skipr,parse_dates={'datet':[0,1]},index_col='datet',date_parser=parse,names=variables)#creat a new Datetimeindex
      if lines[1][15:25]=='Minilog-TD':
         df=df.drop('Depth',1)
      #print df
      default=0
      fixtime=raw_input('Enter the number of hours to shift: ')
      if not fixtime:
          fixtime=default
      df.index=df.index+timedelta(hours=int(fixtime))
      fig = plt.figure(figsize=(12,4))
      plt.plot(df.index.to_pydatetime(),df.values)
      print "click on start and stop times to save date"
      [start,end]=ginput(n=2)
      plt.clf()
      FF,FT=chooseSE(start,end,skipr)#calling the chooseSE function.
      plt.title(Sc+' deployment '+fn[5:7]+' in '+str(int(eval(dep)))+' fathoms')
      #saveTemFig(diroutplt)#dirout
      ############generate the yeardays##############
      FF=FF[isnull(FF['Temp'])==False] # gets rid of NaNs
      FT=c2f(FF['Temp'])
      yd=getyearday(FF)#calling the getyearday function.
      #############c to f##################
      # FT=[]
      # for k in range(len(FF.index)):#convert C to F
      # f=c2f(FF['Temp'][k])
      # FT.append(f)
      ############output file###################
      PFDATA={'sitecode':Series(Sc,index=FF.index),#creat the format
              'depth':Series(dep,index=FF.index),
              'sernum':Series(Sn,index=FF.index),
              'probsetting':Series(Ps,index=FF.index),
              'Temp':Series(FT[0],index=FF.index),
              'Salinity':Series('99.999',index=FF.index),
              'Datet':Series(FF.index,index=FF.index),
              'yearday':Series(yd,index=FF.index)}
      PFDATADFNEW=outfomat(PFDATA)
      PFDATADFNEW.to_csv(dirout+string.upper(fn[1:5])+'m'+Sn+Ps.zfill(2)+fn[3:5]+'.dat',float_format='%10.2f',index=False,header=False)

      plt.show()

#below is the repeat code for ONSET MX1101 instruments used by DATISSYSTEMS.
elif (mark=='S') and (mark2=='e'):# this less common method.
      def parse(datet):
         dt=datetime.strptime(datet[0:19],'%Y-%m-%d %H:%M:%S') # 
         return dt
      Sn=lines[0][18:22]
      variables=['Date','Temp','Dum1','Dum2','Dum3','Dum4','Dum5']
      df=read_csv(direct+fn,sep=',',skiprows=3,header=None,parse_dates={'datet':[0]},index_col='datet',date_parser=parse,names=variables)
      fig = plt.figure(figsize=(12,4))
      id=list(where(df['Temp']!=' ')[0]) # finds rows where no temperature is reported
      df=df['Temp'][id] # df becomes a series
      df=df.to_frame() # back to frame
      tt=[]
      for k in range(len(df)):
         tt.append(f2c(float(df['Temp'][k]))[0]) # converting to celcius in ONSET case
      df['Temp']=tt
      plt.plot(df.index.to_pydatetime(),df.values)
      print "click on start and stop times to save date"
      [start,end]=pylab.ginput(n=2)
      #plt.close()
      plt.clf()
      #df=df.drop(['Dum1','Dum2','Dum3','Dum4'],1)
      skipr=2
      FF=chooseSE(start,end,skipr)
      saveTemFig(diroutplt)
      ############generate the yeardays##############
      yd=getyearday(FF[0])
     #############c to f##################
      FT=[]
      f=c2f(FF[0]['Temp']) 
      #FT.append(f)
     ############output file###################
      PFDATA={'sitecode':Series(Sc,index=FF[0].index),
              'depth':Series(dep,index=FF[0].index),
              'sernum':Series(Sn1,index=FF[0].index),
              'probsetting':Series(Ps,index=FF[0].index),
              'Temp':Series(f[0],index=FF[0].index),
              'Salinity':Series('99.999',index=FF[0].index),
              'Datet':Series(FF[0].index,index=FF[0].index),
              'yearday':Series(yd,index=FF[0].index)}
      PFDATADFNEW=outfomat(PFDATA)
      PFDATADFNEW.to_csv(dirout+fn[0:-4]+'.dat',float_format='%10.2f',index=False)
      plt.show()

#below is the repeat code for ONSET MX2204 instruments 
elif (mark=='P'):# this less common method added in Feb 2020 when Jim Ford sent first file
      def parse(datet):
         dt=datetime.strptime(datet[0:19],'%Y-%m-%d %H:%M:%S') # 
         return dt
      Sn=lines[0][16:24]
      variables=['Dum','Date','Temp']
      df=read_csv(direct+fn,sep=',',skiprows=2,header=None,parse_dates={'datet':[1]},index_col='datet',date_parser=parse,names=variables)
      df=df.drop('Dum',axis=1)# just gets rid of the 1st column
      fig = plt.figure(figsize=(12,4))
      #id=list(where(df['Temp']!=' ')[0]) # finds rows where no temperature is reported
      #df=df['Temp'][id] # df becomes a series
      #df=df.to_frame() # back to frame
      tt=[]
      for k in range(len(df)):
         tt.append(f2c(float(df['Temp'][k]))[0]) # converting to celcius in ONSET case
      df['Temp']=tt
      plt.plot(df.index.to_pydatetime(),df.values)
      print "click on start and stop times to save date"
      [start,end]=pylab.ginput(n=2)
      #plt.close()
      plt.clf()
      #df=df.drop(['Dum1','Dum2','Dum3','Dum4'],1)
      skipr=2
      FF=chooseSE(start,end,skipr)
      saveTemFig(diroutplt)
      ############generate the yeardays##############
      yd=getyearday(FF[0])
     #############c to f##################
      FT=[]
      f=c2f(FF[0]['Temp']) 
      #FT.append(f)
     ############output file###################
      PFDATA={'sitecode':Series(Sc,index=FF[0].index),
              'depth':Series(dep,index=FF[0].index),
              'sernum':Series(Sn1,index=FF[0].index),
              'probsetting':Series(Ps,index=FF[0].index),
              'Temp':Series(f[0],index=FF[0].index),
              'Salinity':Series('99.999',index=FF[0].index),
              'Datet':Series(FF[0].index,index=FF[0].index),
              'yearday':Series(yd,index=FF[0].index)}
      PFDATADFNEW=outfomat(PFDATA)
      PFDATADFNEW.to_csv(dirout+fn[0:-4]+'.dat',float_format='%10.2f',index=False)
      plt.show()
#below is the repeat code for StarOddi instruments used by Narragansett Lab.
elif mark=='#':# if input file have the character'Intensity',call this less common method.
      def parse(datet):
         dt=datetime.strptime(datet[0:16],'%d.%m.%y %H:%M:%S') # Jerry Prezioso format
         return dt
      Sn=lines[1][16:19]
      df=read_csv(direct+fn,sep='\t',skiprows=15,parse_dates={'datet':[1]},index_col='datet',date_parser=parse,names=['Dummy','Datetime','Temp','Depth'])
      temp=[]
      for k in range(len(df)):
        tt=float(df.Temp[k].replace(',','.'))
        temp.append(tt)
      df['tf']=temp
      fig = plt.figure(figsize=(12,4))
      plt.plot(df.index.to_pydatetime(),df.tf.values)
      print "click on start and stop times to save date"
      [start,end]=pylab.ginput(n=2)
      #plt.close()
      plt.clf()
      df=df.drop(['Dummy','Temp','Depth'],1)
      skipr=2
      FF=chooseSE(start,end,skipr)
      saveTemFig(diroutplt)
      ############generate the yeardays##############
      yd=getyearday(FF[0])
     #############c to f##################
      FT=[]
      #f=c2f(FF[0]['Temp'])
      f=c2f(FF[0]['tf'])# JiM Nov 2017
      #FT.append(f)
     ############output file###################
      PFDATA={'sitecode':Series(Sc,index=FF[0].index),
              'depth':Series(dep,index=FF[0].index),
              'sernum':Series(Sn1,index=FF[0].index),
              'probsetting':Series(Ps,index=FF[0].index),
              'Temp':Series(f[0],index=FF[0].index),
              'Salinity':Series('99.999',index=FF[0].index),
              'Datet':Series(FF[0].index,index=FF[0].index),
              'yearday':Series(yd,index=FF[0].index)}
      PFDATADFNEW=outfomat(PFDATA)
      PFDATADFNEW.to_csv(dirout+fn[0:-4]+'.dat',float_format='%10.2f',index=False)
      plt.show()
      

      '''Q=raw_input("Do you want to plot Intensity figrue? y/n")
      if Q=='y'or'Y':
          df=DataFrame(dr['Intensity'],index=dr.index)
          fig = plt.figure(figsize=(12,4))
          # fig = plt.figure()
          plt.plot(df.index.to_pydatetime(),df.values)
          print "click on start and stop times to save date"
          [start,end]=pylab.ginput(n=2)
          #plt.close()
          plt.clf()
          FF=chooseSE2(start,end)
          plt.savefig(diroutplt+fn[0:-4]+'Intensity.png')
          plt.show()
      '''
#below is the repeat code for YSI instruments used by SMCC.
elif mark1=='Intensity':# if input file have the character'Intensity',call this less common method.
      dr=read_csv(direct+fn,sep=',',skiprows=2,parse_dates={'datet':[1]},index_col='datet',names=['NO','DataTime','Temp','Intensity','CouplerDetached','CouplerAttached','Stopped','EndOfFile'])
      df=DataFrame(dr['Temp'],index=dr.index)
      fig = plt.figure(figsize=(12,4))
      # fig = plt.figure()
      plt.plot(df.index.to_pydatetime(),df.values)
      print "click on start and stop times to save date"
      [start,end]=pylab.ginput(n=2)
      #plt.close()
      plt.clf()
      skipr=2
      FF=chooseSE(start,end,skipr)
      saveTemFig(diroutplt)
      ############generate the yeardays##############
      yd=getyearday(FF[0])
     #############c to f##################
      FT=[]
      f=c2f(FF[0]['Temp'])
      #FT.append(f)
     ############output file###################
      PFDATA={'sitecode':Series(Sc,index=FF[0].index),
              'depth':Series(dep,index=FF[0].index),
              'sernum':Series(Sn1,index=FF[0].index),
              'probsetting':Series(Ps,index=FF[0].index),
              'Temp':Series(f[0],index=FF[0].index),
              'Salinity':Series('99.999',index=FF[0].index),
              'Datet':Series(FF[0].index,index=FF[0].index),
              'yearday':Series(yd,index=FF[0].index)}
      PFDATADFNEW=outfomat(PFDATA)
      PFDATADFNEW.to_csv(dirout+fn[0:-4]+'.dat',float_format='%10.2f',index=False)
      plt.show()
      

      Q=raw_input("Do you want to plot Intensity figrue? y/n")
      if Q=='y'or'Y':
          df=DataFrame(dr['Intensity'],index=dr.index)
          fig = plt.figure(figsize=(12,4))
          # fig = plt.figure()
          plt.plot(df.index.to_pydatetime(),df.values)
          print "click on start and stop times to save date"
          [start,end]=pylab.ginput(n=2)
          #plt.close()
          plt.clf()
          FF=chooseSE2(start,end)
          plt.savefig(diroutplt+fn[0:-4]+'Intensity.png')
          plt.show()
else:# this is the third also not common method to read-in data where both temp & salinity are involved.
      skipr=5
      dr=read_csv(direct+fn,sep=',',skiprows=2,parse_dates={'datet':[1]},index_col='datet',names=['NO','DataTime','CondHighRng','Temp','SpecConduct','Salinity','CouplerDetached','CouplerAttached','Stopped','EndOfFile'])
      df=DataFrame(dr['Temp'],index=dr.index)
      fig = plt.figure(figsize=(12,4))
      # fig = plt.figure()
      plt.plot(df.index.to_pydatetime(),df.values)
      print "click on start and stop times to save date"
      [start,end]=pylab.ginput(n=2)
      #plt.close()
      plt.clf()
      FF=chooseSE(start,end,skipr)
      saveTemFig(diroutplt)

      ############generate the yeardays##############
      print FF
      yd=getyearday(FF[0])

      #############c to f##################
      #FT=[]
      FT=c2f(FF[0]['Temp'])

      ### rid of bad salts
      dr['Salinity'].ix[dr['Salinity']>maxsalt]=99.999
      dr['Salinity'].ix[dr['Salinity']<minsalt]=99.999
      
      ############output file###################

      PFDATA={'sitecode':Series(Sc,index=FF[0].index),
              'depth':Series(dep,index=FF[0].index),
              'sernum':Series(Sn1,index=FF[0].index),
              'probsetting':Series(Ps,index=FF[0].index),
              'Temp':Series(FT[0].values,index=FF[0].index),
              'Salinity':Series(dr['Salinity'],index=FF[0].index),
              'Datet':Series(FF[0].index,index=FF[0].index),
              'yearday':Series(yd,index=FF[0].index)}
      PFDATADFNEW=outfomat(PFDATA)
      PFDATADFNEW.to_csv(dirout+string.upper(fn[1:5])+'h'+Sn1+Ps.zfill(2)+fn[3:5]+'.dat',float_format='%10.3f',index=False,header=False)
      #PFDATADFNEW.to_csv(dirout+fn[0:-4]+'.csv',float_format='%10.2f',index=False)
      plt.show()
      
      Q=raw_input("Do you want to plot Salinity figrue? y/n: ")
      
      if Q=='y'or'Y':
          df=DataFrame(dr['Salinity'],index=dr.index)
          fig = plt.figure(figsize=(12,4))
          # fig = plt.figure()
          plt.plot(df.index.to_pydatetime(),df.values)
          print "click on start and stop times to save date"
          [start,end]=pylab.ginput(n=2)
          #plt.close()
          plt.clf()
          FF=chooseSE2(start,end)
          plt.savefig(diroutplt+fn[0:-4]+'Salinity.png')
          plt.savefig(diroutplt+fn[0:-4]+'Salinity.ps')
          plt.show()
################################################################################
#this section extracts data for calibration purposes 
# need to modify to deal with dataframes created above
scp=datetime(2013,3,27,13,0)
ecp=datetime(2013,3,28,19,0)
sn,yr,yd,t=[],[],[],[]
#save /data5/jmanning/calprobe/mar13/calprobe13.dat yycal -ascii -append;
fid=open('/net/data5/jmanning/calprobe/mar13/calprobe13.dat','a')
#id=np.argwhere((PFDATADFNEW.index>=scp) and (PFDATADFNEW.index<=ecp))
#id=ml.find((PFDATADFNEW.index>=scp) and (PFDATADFNEW.index<=ecp))
PFDATADFNEWCAL=PFDATADFNEW.ix[scp:ecp]
if len(PFDATADFNEWCAL)>0:
   for kk in range(len(PFDATADFNEWCAL)):
     fid.write(str(Ps)+" 2013 "+'%7.3f'%(date2num(PFDATADFNEWCAL.index[kk])-date2num(datetime(2013,1,1,0,0)))+" "+str(PFDATADFNEWCAL.Temp[kk])+"\n")
    # quick plot of calibration period result
   fig=plt.figure(53)
   ax5=fig.add_subplot(111)
   ax5.plot(PFDATADFNEWCAL.index,PFDATADFNEWCAL.Temp)
   ax5.set_xlabel('2013')
   ax5.set_ylabel('degC')
   plt.title([Ps, 'Calibration actually conducted Mar 2013']);
   #plt.close()
   print 'Saved calibration results in  /data5/jmanning/calprobe/mar13/calprobe13.dat'
else: 
   print 'No data during 2013 calibration session'
fid.close()
