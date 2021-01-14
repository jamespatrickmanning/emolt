# This is most of the routines for processing the non-realtime fixed gear temperature data.
The main routines are:
-emolt_pd.py  where "pd" stands for pandas is the routine that reads the raw data, plots it, cleans it, and exports .dat file for Oracle 
-emolt2_pd.py reads the ERDDAP data and plots multiple years at user specified site
-bill_adler.py plots specified year of data on the annual mean curve (based on the data at that site) and also plots the climatology(based on research vessel surveys)
-plt_emolt_annual.py plots annual average temperature time series at user specified site

There are also a set of other less-used routines to, for example:
-emolt_pd_dmr_consolidated.py to process Maine DMR ventless
-emolt_pd_cfrf.py to process CFRF
-plt_dmr_sites to plot them


Note: There is another repository to process data coming from Nicks instruments deployed, for example, in Cape Cod Bay in Summer of 2020. See "LFoM" repository which stands for Lobster Foundation of Massachusetts. There is also a separate FSRS repository.
