#By Emmanuel David Castillo Taborda - ecastillo@sgc.gov.co
import MySQLdb
import csv
import os
import json
from datetime import timedelta
import pandas as pd
import utils2query as utq
from obspy import UTCDateTime

SGC_PUBLIC_STATIONS = ['APAC','AGCC','ARGC','ARMEC','BAR2','BBAC','BET','BOG',
                    'BRJC','CAP2','CCALA','CBETA','CBOC','CHI','CLBC','CLEJA','CPOP2',
                    'CPRAD','CRJC','CRU','CUM','DBB','EZNC','FLO2','GARC',
                    'GR1C','GRPC','GUA','GUY2C','HEL','JAMC','LCBC','MACC',
                    'MAL','MAN1C','MAP','MEDEC','NIZA','NOR','OCA','ORTC','PAL','PAM','PAS2','PDSC','PGA1B','PIZC',
                    'POP2','PRA','PRV','PTA','PTB','PTGC','PTLC','QUBC',
                    'RECRC','RNCC','RUS','SAIC','SERC','SJC','SMAR','SOL','SPBC',
                    'TAM','TUM','TUM3C','URE','URI','URMC','VIL','YOT',
                    'YPLC','ZAR','VMM05','VMM06','VMM07','VMM08',
                    'VMM09','VMM10','VMM11','VMM12']
                    

VMM_stations = ['AGCC','EZNC','SNPBC','MORC','OCNC','SML1C','VMM05','VMM06',
                'VMM07','VMM08','VMM09','VMM10','VMM11','VMM12','VMM13','BRR',
                'LL1C','LL5C','LL6C','LL7C','LL8C','OCA','PAM','BAR2','PTB','ZAR',
                'RUS','SPBC','NOR','HEL']

class Query(object):
    def __init__(self,MySQLdb_dict,query):
        self.MySQLdb_dict= MySQLdb_dict
        self.query = query

    @property
    def MySQLdb(self):
        db= MySQLdb.connect(host=self.MySQLdb_dict['host'], user=self.MySQLdb_dict['user'], 
                              passwd=self.MySQLdb_dict['passwd'], db=self.MySQLdb_dict['db'])
        return db

    def simple_SQLquery(self,initial_date, final_date,
                        min_mag, max_mag, min_prof, max_prof,
                        event_type=None,station_list=None,
                        sort = None,merge_picks="inner",to_csv=None):

        self.info = f'initial_date={initial_date},final_date={final_date},'+\
            f'min_mag={min_mag},max_mag={max_mag},'+\
            f'min_prof={min_prof},max_prof={max_prof},'+\
            f'event_type={event_type},station_list={station_list}'

        if station_list == "sgc_public":
            station_list = SGC_PUBLIC_STATIONS 

        if merge_picks == "inner":

            query = utq.QueryHelper(self.query,initial_date, final_date, 
                                min_mag, max_mag, min_prof, max_prof,
                                event_type,station_list)
            codex = query.simple_query()
            simple_query = pd.read_sql_query(codex,self.MySQLdb)
            df = utq.get_fulltime(simple_query)
        else:
            dfs = {}
            for phase in ['P','S']:

                query = utq.QueryHelper("single_picks",initial_date, final_date, 
                                    min_mag, max_mag, min_prof, max_prof,
                                    event_type,station_list,phase)
                codex = query.simple_query()
                simple_query = pd.read_sql_query(codex,self.MySQLdb)

                df = utq.get_fulltime(simple_query,True)
                # df.rename(columns={ 'time_pick':f'time_pick_{phase.lower()}',
                #                 'time_ms_pick':f'time_ms_pick_{phase.lower()}',
                #                 'pick':f'pick_{phase.lower()}'}, inplace=True)
                # df.to_csv(f"/home/ecastillo/tesis/catalog/manual/events/{phase}.csv")
                dfs[phase] = df
                # dfs.append(df)

            df = pd.merge(dfs["P"],dfs["S"],on=['agency','id','time_event','latitude','latitude_uncertainty',
            'longitude','longitude_uncertainty','depth','depth_uncertainty','rms','region','earth_model',
            'method','event_type','magnitude','magnitude_type','picker','network','station','location'],how='left',suffixes=("_p", "_s"))
            # df.to_csv("")

        if self.query in ("event","Event","EVENT","events","EVENTS"):
            df = simple_query

        if sort != None:   
            df = df.sort_values(by=sort,ascending=True,ignore_index=True)
        if to_csv != None:
            if os.path.isdir(os.path.dirname(to_csv)):
                pass
            else:
                os.makedirs(os.path.dirname(to_csv))

            with open(to_csv,'w') as csv:   
                csv.write(f'#{self.info}\n')
            df.to_csv(to_csv, mode='a')
        return df

    def id_SQLquery(self,loc_id, initial_date, final_date, 
                      min_mag, max_mag, min_prof, max_prof, 
                      event_type=None,station_list=None,
                      sort = None,to_csv=None):
        self.info = f'ID={loc_id}'+\
            f'initial_date={initial_date},final_date={final_date},'+\
            f'min_mag={min_mag},max_mag={max_mag},'+\
            f'min_prof={min_prof},max_prof={max_prof},'+\
            f'event_type={event_type},station_list={station_list}'

        if station_list == "sgc_public":
            station_list = SGC_PUBLIC_STATIONS 

        query = utq.QueryHelper(self.query,initial_date, final_date, 
                              min_mag, max_mag, min_prof, max_prof,
                              event_type,station_list)
        codex = query.id_query(loc_id)
        id_query = pd.read_sql_query(codex,self.MySQLdb)

        if self.query in ("pick","PICK","Pick","picks","Picks"):
            df = utq.get_fulltime(id_query)
        elif self.query in ("event","Event","EVENT","events","EVENTS"):
            df = id_query

        if sort != None:   
            df = df.sort_values(by=sort,ascending=True)
        if to_csv != None:
            if os.path.isdir(os.path.dirname(to_csv)):
                pass
            else:
                os.makedirs(os.path.dirname(to_csv))

            with open(to_csv,'w') as csv:   
                csv.write(f'#{self.info}\n')
            df.to_csv(to_csv, mode='a')
        return df

    def radial_SQLquery(self,lat, lon, ratio, initial_date, final_date, 
                      min_mag, max_mag, min_prof, max_prof, 
                      event_type=None,station_list=None,
                      sort = None,to_csv=None):

        self.info = f'lat={lat},lon={lon},ratio={ratio},'+\
            f'initial_date={initial_date},final_date={final_date},'+\
            f'min_mag={min_mag},max_mag={max_mag},'+\
            f'min_prof={min_prof},max_prof={max_prof},'+\
            f'event_type={event_type},station_list={station_list}'

        if station_list == "sgc_public":
            station_list = SGC_PUBLIC_STATIONS 

        query = utq.QueryHelper(self.query,initial_date, final_date, 
                              min_mag, max_mag, min_prof, max_prof,
                              event_type,station_list)
        codex = query.radial_query(lat, lon, ratio)
        radial_query = pd.read_sql_query(codex,self.MySQLdb)

        if self.query in ("pick","PICK","Pick","picks","Picks"):
            df = utq.get_fulltime(radial_query)
        elif self.query in ("event","Event","EVENT","events","EVENTS"):
            df = radial_query
            
        if sort != None:   
            df = df.sort_values(by=sort,ascending=True)
        if to_csv != None:
            if os.path.isdir(os.path.dirname(to_csv)):
                pass
            else:
                os.makedirs(os.path.dirname(to_csv))
                
            with open(to_csv,'w') as csv:   
                csv.write(f'#{self.info}\n')
            df.to_csv(to_csv, mode='a')
        return df

if __name__ == "__main__":

    # nido de los santos
    # 6.6 a 7.3  
    # -72.7 a -73.4
    # 6.81 y -73.1 radio 0.5°-> 60km
    # 5.2 y -73.7 radio 0.5°-> 60km
## GLOBAL VARIBALES
    picks =True 
    events = False
    start = "20160101 000000"
    # end =   "20200901 000000"
    end =   "20160102 000000"
    output_path = "/home/ecastillo/tesis/catalog/manual/events/"
    agency = "VMMmanual"

    lat = 6.81
    lon = -73.17
    ratio = 120
    min_mag =  -0.2
    max_mag = 10
    min_prof =  -5
    max_prof = 260

    # ## GLOBAL VARIBALES
    # picks = True
    # events = False
    # start = "20180101 000000"
    # end =   "20190101 000000"
    # output_path = "/home/ecastillo/tesis/manual_picks"
    # agency = "SGC"

    #### only for events
    # lat = 3.46
    # lon = -74.18
    # ratio = 30
    # min_mag =  2
    # max_mag = 3
    # min_prof =  0
    # max_prof = 10    

    ## phpmyadmin credentials
    host = "10.100.100.232"
    port_fdsn = "8091"
    user="consulta"
    passwd="consulta"
    db="seiscomp3"
    
    MySQLdb_dict= {'host':host, 'user':user, 'passwd':passwd, 'db': db}
    client_dict= {'ip_fdsn':f"http://{host}", 'port_fdsn':port_fdsn}
    _startname, _endname = start.replace(" ",""),end.replace(" ","")
    if events == True:
        name = f"{agency}_events_{_startname}_{_endname}.csv"
        csv_path = os.path.join(output_path,name)
        events = Query(MySQLdb_dict,"events").radial_SQLquery(lat,lon,ratio,
                                                    start, end, 
                                                    min_mag, max_mag, 
                                                    min_prof, max_prof,
                                                    "earthquake", "sgc_public",
                                                    ['time_event'],
                                                    csv_path)
        print(events)
        # (self,lat, lon, ratio, initial_date, final_date, 
        #               min_mag, max_mag, min_prof, max_prof, 
        #               event_type=None,station_list=None,
        #               sort = None,to_csv=None):



    if picks == True:
        name = f"{agency}_picks_{_startname}_{_endname}.csv"
        csv_path = os.path.join(output_path,name)
        

        picks = Query(MySQLdb_dict,"picks").simple_SQLquery(
                                                    start, end, 
                                                    min_mag, max_mag, 
                                                    min_prof, max_prof,
                                                    None, VMM_stations,
                                                    ['time_event'],"left",
                                                    csv_path)
        print(picks)