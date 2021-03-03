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

class Picks(object):
    def __init__(self,MySQLdb_dict):
        self.MySQLdb_dict= MySQLdb_dict

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

        pickquery = utq.PickQuery(initial_date, final_date, 
                              min_mag, max_mag, min_prof, max_prof,
                              event_type,station_list)
        codex = pickquery.query()
        simple_query = pd.read_sql_query(codex,self.MySQLdb)

        df = utq.get_fulltime(simple_query)
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

        pickquery = utq.PickQuery(initial_date, final_date, 
                              min_mag, max_mag, min_prof, max_prof,
                              event_type,station_list)
        codex = pickquery.id_query(loc_id)
        id_query = pd.read_sql_query(codex,self.MySQLdb)

        df = utq.get_fulltime(id_query)
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

        pickquery = utq.PickQuery(initial_date, final_date, 
                              min_mag, max_mag, min_prof, max_prof,
                              event_type,station_list)
        codex = pickquery.radial_query(lat, lon, ratio)
        radial_query = pd.read_sql_query(codex,self.MySQLdb)

        df = utq.get_fulltime(radial_query)
        if sort != None:   
            df = df.sort_values(by=sort,ascending=True)
        if to_csv != None:
            with open(to_csv,'w') as csv:   
                csv.write(f'#{self.info}\n')
            df.to_csv(to_csv, mode='a')
        return df


class Events(object):
    def __init__(self,MySQLdb_dict, lat, lon, ratio, 
        initial_date, final_date, min_mag, max_mag,
         min_prof, max_prof, sort=None ):
        self.MySQLdb_dict= MySQLdb_dict
        # self.MySQLdb= MySQLdb.connect(host=self.MySQLdb_dict['host'], user=self.MySQLdb_dict['user'], 
                                        # passwd=self.MySQLdb_dict['passwd'], db=self.MySQLdb_dict['db'])
        self.host= self.MySQLdb_dict['host']
        self.lat, self.lon, self.ratio = lat, lon, ratio
        self.initial_date, self.final_date= initial_date, final_date
        self.min_mag, self.max_mag= min_mag, max_mag
        self.min_prof, self.max_prof= min_prof, max_prof

        _codex = phpmyAdmin(os.path.join(os.getcwd(),"queries","query_by_param.txt"))
        self.codex= _codex.radial_query(lat, lon, ratio, initial_date, final_date, min_mag, max_mag, min_prof, max_prof)

    @property
    def MySQLdb(self):
        db= MySQLdb.connect(host=self.MySQLdb_dict['host'], user=self.MySQLdb_dict['user'], 
                              passwd=self.MySQLdb_dict['passwd'], db=self.MySQLdb_dict['db'])
        return db

    @property
    def SQL_Query(self):
        SQL_Query = pd.read_sql_query(self.codex,self.MySQLdb)
        return SQL_Query

    @property
    def info(self):
        info= f'lat={self.lat},lon={self.lon},ratio={self.ratio},initial_date={self.initial_date},final_date={self.final_date},min_mag={self.min_mag},max_mag={self.max_mag},min_prof={self.min_prof},max_prof={self.max_prof}'
        return info

    def to_DataFrame(self,sort=None):
        df = pd.DataFrame(self.SQL_Query)
        df.index+=1
        df.index.name= 'No'
        if sort != None:   
            df = df.sort_values(by=sort,ascending=True)
        return df

    def to_csv(self,csv_name,sort= None):
        df = self.to_DataFrame(sort)
        with open(csv_name,'w') as csv:   
            csv.write(f'#{self.info}\n')
        df.to_csv(csv_name, mode='a')
    
if __name__ == "__main__":

    # nido de los santos
    # 6.6 a 7.3  
    # -72.7 a -73.4
    # 6.81 y -73.1 radio 0.5°-> 60km
    # 5.2 y -73.7 radio 0.5°-> 60km
## GLOBAL VARIBALES
    picks = True
    events = False
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
        evs = Events(MySQLdb_dict, lat, lon, ratio, 
                    start, end, 
                    min_mag, max_mag, 
                    min_prof, max_prof )
        evs.to_csv(csv_path,['time_event'])
    if picks == True:
        name = f"{agency}_picks_{_startname}_{_endname}.csv"
        csv_path = os.path.join(output_path,name)
        # picks = Picks(MySQLdb_dict).simple_SQLquery(start, end, 
        #                                             min_mag, max_mag, 
        #                                             min_prof, max_prof,
        #                                             "earthquake", "sgc_public",
        #                                             ['time_event','time_pick_p'],
        #                                             csv_path)
        picks = Picks(MySQLdb_dict).id_SQLquery(    "SGC2021ceyptl",
                                                    start, end, 
                                                    min_mag, max_mag, 
                                                    min_prof, max_prof,
                                                    "earthquake", "sgc_public",
                                                    ['time_event','time_pick_p'],
                                                    csv_path)
        print(picks)