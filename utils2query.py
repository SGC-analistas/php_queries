import os 
import io
import pandas as pd
from obspy import UTCDateTime
from datetime import timedelta

ROOT_DIR = os.path.dirname(__file__)
pick_codex = os.path.join(ROOT_DIR,"query_picks.txt")
single_pick_codex = os.path.join(ROOT_DIR,"query_single_picks.txt")
event_codex = os.path.join(ROOT_DIR,"query_events.txt")

def get_text2php(from_text,rm_line=None, add_line=None):
    """
    Parameters:
    from_text: list 
        List of lines from readlines() method
    rm_line: int or None
        remove specific line in a text in txt file
    add_line: list of tuple (int,str)
        In the first place is the index number where you want to add a line.
        In the second place is the line of code that you need to add
    """
    
    text = from_text[0]  #line 1
    text_sketch = from_text[1:]
    for index,line in enumerate(text_sketch,2): # 2 because refers to line 2
        if rm_line != None:
            if rm_line == 1:
                raise Exception("Line 1 of text can't be removed.")
            if index == rm_line:
                pass
            else:
                text= f'{text}\
                        {line}'

        if add_line != None:
            ##count lines that will be added.
            count = 0
            for i in range(len(add_line)):
                if index == add_line[i][0]:
                    count += 1
                    
                    # if want to add in the last line, first write 
                    # the last line of the original text
                    if index == len(text_sketch)+count:
                        text= f'{text}\
                        {line}'

                    # Add text that you want to add.
                    text = f'{text}\
                                {add_line[i][1]}'

            # if it is not the last line add theline  of the 
            #  original text
            if index != len(text_sketch)+count: 
                text= f'{text}\
                        {line}'

        else:
            text= f'{text}\
                        {line}'

    return text

def get_fulltime(sql,single=False):
    df = pd.DataFrame(sql)
    df.index+=1
    df.index.name= 'No'

    if single:
        df['time_pick'] = df.apply(lambda x: get_timepick(x,None), axis=1).astype(str)
        df = df.drop(columns=['time_ms_pick'])
        df[f'time_pick'] = pd.to_datetime(df[f'time_pick'], format='%Y-%m-%dT%H:%M:%S.%f') 

    else:
        df['time_pick_p'] = df.apply(lambda x: get_timepick(x,'p'), axis=1).astype(str)
        df['time_pick_s'] = df.apply(lambda x: get_timepick(x,'s'), axis=1).astype(str)
        df = df.drop(columns=['time_ms_pick_p','time_ms_pick_s'])

        df[f'time_pick_p'] = pd.to_datetime(df[f'time_pick_p'], format='%Y-%m-%dT%H:%M:%S.%f') 
        df[f'time_pick_s'] = pd.to_datetime(df[f'time_pick_s'], format='%Y-%m-%dT%H:%M:%S.%f') 
    
    
    return df

def get_timepick(df,pick):

    if pick == None:
        pick = df[f'time_pick'] + \
            timedelta(milliseconds=float(df[f'time_ms_pick']/1000))
    else:
        pick = df[f'time_pick_{pick}'] + \
            timedelta(milliseconds=float(df[f'time_ms_pick_{pick}']/1000))
    return UTCDateTime(pick)

def str2datetime(mydatetime):
    date,hour = mydatetime.split()
    year,month,day,hour,minute,sec = date[0:4],date[4:6],date[6:8],hour[0:2],hour[2:4],hour[4:6]
    return f"{year}/{month}/{day} {hour}:{minute}:{sec}"
    
class QueryHelper(object):
    def __init__(self,query,initial_date,final_date,  
                    min_mag,max_mag,min_prof,max_prof,
                    event_type=None,station_list=None,
                    pick="P"):
        """
        Parameters:
        -----------
        initial_date: str
            initial date in the next format : YYYYMMDD HHMMSS
        final_date: str 
            final date in the next format : YYYYMMDD HHMMSS
        min_mag: int
            minimum magnitude
        max_mag: int
            maximum magnitude
        min_prof: int
            minimum depth
        max_prof
            maximum depth
        event_type: list
            "earthquake" or "not locatable" etc
        station_list: list
            Only select stations located in station_list
        """
        self.query = query
        self.initial_date = str2datetime(initial_date)
        self.final_date = str2datetime(final_date)
        self.min_mag = min_mag
        self.max_mag = max_mag
        self.min_prof = min_prof
        self.max_prof = max_prof
        self.event_type = event_type
        self.station_list = station_list

        self.__singleP_eventtype_lines = [38] #42 in where
        self.__singleP_radialquery_lines = [15,41] #7 in select, 45 in where
        self.__singleP_stationlist_lines = [38] #42 in where
        self.__singleP_idquery_lines = [38] #40 in where

        self.__P_eventtype_lines = [46] #42 in where
        self.__P_radialquery_lines = [15,49] #7 in select, 45 in where
        self.__P_stationlist_lines = [46] #42 in where
        self.__P_idquery_lines = [46] #40 in where

        self.__E_eventtype_lines = [22] #42 in where
        self.__E_radialquery_lines = [7,26] #7 in select, 45 in where
        self.__E_stationlist_lines = [22] #42 in where
        self.__E_idquery_lines = [22] #40 in where

        if self.query in ("pick","PICK","Pick","picks","Picks"):
            query_text = open(pick_codex,"r", encoding="latin-1").readlines()
        elif self.query in ("single_pick","single_PICK","single_Pick","single_picks","single_Picks"):
            query_text = open(single_pick_codex,"r", encoding="latin-1").readlines()
        elif self.query in ("event","Event","EVENT","events","EVENTS"):
            self.station_list = None
            query_text = open(event_codex,"r", encoding="latin-1").readlines()
            pick = None
        else:
            raise Exception("query= 'pick' or 'Event'")
        
        query_text = get_text2php(query_text)
        self.query_text = str(query_text)%(f'{self.min_mag}',f'{self.max_mag}',
                                f'{self.min_prof}',f'{self.max_prof}',
                                f'"{self.initial_date}"',
                                f'"{self.final_date}"')

        if pick != None:
            self.query_text = self.query_text.replace("left join Arrival A_p on A_p._parent_oid=Origin._oid and A_p.phase_code = 'P'",
                                                      f"left join Arrival A_p on A_p._parent_oid=Origin._oid and A_p.phase_code = '{pick}'")
        # print(self.query_text)
        
    def __add_event_type(self,event_type):
        if len(event_type) == 1:
            event_type = f"('{event_type[0]}')"
        else:
            event_type = str(tuple(event_type))

        condition = ("Event.type in %s AND")%(event_type)

        if self.query in ("pick","PICK","Pick","picks","Picks"):
            lines = self.__P_eventtype_lines
        if self.query in ("single_pick","single_PICK","single_Pick","single_picks","single_Picks"):
            lines = self.__singleP_eventtype_lines
        elif self.query in ("event","Event","EVENT","events","EVENTS"):
            lines = self.__E_eventtype_lines

        return [(lines[0],condition)]

    def __add_radial_query(self,latitude,longitude,radio):
        select = "round(( 6371 * acos(cos(radians( %s)) * cos(radians(Origin.latitude_value)) * cos(radians(Origin.longitude_value) - radians(%s)) + sin(radians( %s)) * sin(radians(Origin.latitude_value)))),2) as radio,"
        select = select%(f'{latitude}',f'{longitude}',f'{latitude}')
        condition = "HAVING radio < %s;"
        condition = condition%(radio)
        if self.query in ("pick","PICK","Pick","picks","Picks"):
            lines = self.__P_radialquery_lines
        if self.query in ("single_pick","single_PICK","single_Pick","single_picks","single_Picks"):
            lines = self.__singleP_radialquery_lines
        elif self.query in ("event","Event","EVENT","events","EVENTS"):
            lines = self.__E_radialquery_lines
        return [(lines[0],select),(lines[1],condition)]

    def __add_station_list(self,station_list):
        if len(station_list) == 1:
            station_list = f"('{station_list[0]}')"
        else:
            station_list = str(tuple(station_list))

        condition = ("pick_p.waveformID_stationCode in %s AND")%(station_list)

        if self.query in ("pick","PICK","Pick","picks","Picks"):
            lines = self.__P_stationlist_lines
        elif self.query in ("single_pick","single_PICK","single_Pick","single_picks","single_Picks"):
            condition = ("pick.waveformID_stationCode in %s AND")%(station_list)
            lines = self.__singleP_stationlist_lines
        elif self.query in ("event","Event","EVENT","events","EVENTS"):
            lines = self.__E_stationlist_lines

        return [(lines[0],condition)]

    def __add_id_query(self,loc_id):

        if len(loc_id) == 1:
            loc_id = f"('{loc_id[0]}')"
        else:
            loc_id = str(tuple(loc_id))

        condition = "POEv.PublicID in %s AND"%(loc_id)
        if self.query in ("pick","PICK","Pick","picks","Picks"):
            lines = self.__P_stationlist_lines
        if self.query in ("single_pick","single_PICK","single_Pick","single_picks","single_Picks"):
            lines = self.__singleP_stationlist_lines
        elif self.query in ("event","Event","EVENT","events","EVENTS"):
            lines = self.__E_stationlist_lines
        return [(lines[0],condition)]

    def simple_query(self):
        text = self.query_text

        if self.event_type != None:
            text = io.StringIO(text).readlines()
            event_info = self.__add_event_type(self.event_type)
            text = get_text2php(from_text=text,
                                add_line=event_info)

        if self.station_list != None:
            text = io.StringIO(text).readlines()
            stalist_info = self.__add_station_list(self.station_list)
            text = get_text2php(from_text=text,
                                         add_line=stalist_info)
        return text
    
    def id_query(self,loc_id):
        """
        Parameters:
        -----------
        ID: str
            identification code
        results:
        --------
        text: str
            formatted text with ID
        """
        text = io.StringIO(self.query_text).readlines()
        id_text = self.__add_id_query(loc_id)
        text = get_text2php(from_text=text,
                                add_line=id_text)

        if self.event_type != None:
            text = io.StringIO(text).readlines()
            event_info = self.__add_event_type(self.event_type)
            text = get_text2php(from_text=text,
                                add_line=event_info)

        if self.station_list != None:
            text = io.StringIO(text).readlines()
            stalist_info = self.__add_station_list(self.station_list)
            text = get_text2php(from_text=text,
                                         add_line=stalist_info)
        return text

    def radial_query(self,lat, lon, radio):
        """
        Parameters:
        -----------
        lat: int
            latitude
        lon: int
            longitude
        radio: int
            radio in km
        
        Results:
        --------
            text: str
                formatted text with ID
        """
        text = io.StringIO(self.query_text).readlines()
        radial_text = self.__add_radial_query(lat, lon, radio)
        text = get_text2php(from_text=text,
                                add_line=radial_text)
                        
        if self.event_type != None:
            text = io.StringIO(text).readlines()
            event_info = self.__add_event_type(self.event_type)
            text = get_text2php(from_text=text,
                                add_line=event_info)

        if self.station_list != None:
            text = io.StringIO(text).readlines()
            stalist_info = self.__add_station_list(self.station_list)
            text = get_text2php(from_text=text,
                                         add_line=stalist_info)
        return text