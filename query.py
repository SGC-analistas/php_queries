#By Emmanuel David Castillo Taborda - ecastillo@sgc.gov.co
import MySQLdb
import csv
import os
import json
from datetime import timedelta
import pandas as pd
import utils2query as utq
from obspy import UTCDateTime

SGC_PUBLIC_STATIONS = ['APAC','ARGC','BAR2','BBAC','BET',
                    'BRJC','CAP2','CBETA','CBOC','CHI','CPOP2',
                    'CPRAD','CRJC','CRU','CUM','DBB','FLO2','GARC',
                    'GR1C','GRPC','GUA','GUY2C','HEL','JAMC','LCBC','MACC',
                    'MAL','MAP','NOR','OCA','ORTC','PAL','PAM','PIZC',
                    'POP2','PRA','PRV','PTA','PTB','PTGC','PTLC','QUBC',
                    'RNCC','RUS','SAIC','SERC','SJC','SMAR','SOL','SPBC',
                    'TAM','TUM','TUM3C','URE','URI','URMC','VIL','YOT',
                    'YPLC','ZAR']

def read_params(par_file='phaseNet.inp'):
    lines = open(par_file).readlines()
    par_dic = {}
    for line in lines:
        if line[0] == '#' or line.strip('\n').strip() == '':
            continue
        else:
            l = line.strip('\n').strip()
            key, value = l.split('=')
            par_dic[key.strip()] = value.strip()
    return par_dic

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
                        sort = None,to_csv=None):

        self.info = f'initial_date={initial_date},final_date={final_date},'+\
            f'min_mag={min_mag},max_mag={max_mag},'+\
            f'min_prof={min_prof},max_prof={max_prof},'+\
            f'event_type={event_type},station_list={station_list}'

        if station_list == "sgc_public":
            station_list = SGC_PUBLIC_STATIONS 

        query = utq.QueryHelper(self.query,initial_date, final_date, 
                              min_mag, max_mag, min_prof, max_prof,
                              event_type,station_list)
        codex = query.query()
        simple_query = pd.read_sql_query(codex,self.MySQLdb)

        if self.query in ("pick","PICK","Pick","picks","Picks"):
            df = utq.get_fulltime(simple_query)
        elif self.query in ("event","Event","EVENT","events","EVENTS"):
            df = simple_query

        if sort != None:   
            df = df.sort_values(by=sort,ascending=True)
        if to_csv != None:
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
    picks = False
    events = True
    start = "20210201 000000"
    end =   "20210228 000000"
    output_path = "/home/ecastillo/repositories/gprieto"
    agency = "SGC_cucunuba"

    lat = 5.2
    lon = -73.4
    ratio = 60
    min_mag =  0.1
    max_mag = 10
    min_prof =  0
    max_prof = 200

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
        events = Query(MySQLdb_dict,"events").id_SQLquery("SGC2021ceyptl",
                                                    start, end, 
                                                    min_mag, max_mag, 
                                                    min_prof, max_prof,
                                                    "earthquake", "sgc_public",
                                                    ['time_event'],
                                                    csv_path)
        print(events)
    if picks == True:
        name = f"{agency}_picks_{_startname}_{_endname}.csv"
        csv_path = os.path.join(output_path,name)
        
        picks = Query(MySQLdb_dict,"picks").id_SQLquery(    "SGC2021ceyptl",
                                                    start, end, 
                                                    min_mag, max_mag, 
                                                    min_prof, max_prof,
                                                    "earthquake", "sgc_public",
                                                    ['time_event','time_pick_p'],
                                                    csv_path)
        print(picks)