import os 
import io
import pandas as pd
from obspy import UTCDateTime
from datetime import timedelta

pick_codex = os.path.join(os.getcwd(),"query_picks.txt")
# event_codex = 

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

def get_fulltime(sql):
    df = pd.DataFrame(sql)
    df.index+=1
    df.index.name= 'No'
    df['time_pick_p'] = df.apply(lambda x: get_timepick(x,'p'), axis=1).astype(str)
    df['time_pick_s'] = df.apply(lambda x: get_timepick(x,'s'), axis=1).astype(str)
    df = df.drop(columns=['time_ms_pick_p','time_ms_pick_s'])

    df[f'time_pick_p'] = pd.to_datetime(df[f'time_pick_p'], format='%Y-%m-%dT%H:%M:%S.%f') 
    df[f'time_pick_s'] = pd.to_datetime(df[f'time_pick_s'], format='%Y-%m-%dT%H:%M:%S.%f') 
    return df

def get_timepick(df,pick):
        pick = df[f'time_pick_{pick}'] + \
             timedelta(milliseconds=float(df[f'time_ms_pick_{pick}']/1000))
        return UTCDateTime(pick)

def add_event_type(event_type):
        condition = ("Event.type = '%s' AND")%(event_type)
        return [(42,condition)]
        
def add_radial_query(latitude,longitude,radio):
    select = "round(( 6371 * acos(cos(radians( %s)) * cos(radians(Origin.latitude_value)) * cos(radians(Origin.longitude_value) - radians(%s)) + sin(radians( %s)) * sin(radians(Origin.latitude_value)))),2) as radio,"
    select = select%(f'{latitude}',f'{longitude}',f'{latitude}')
    condition = "HAVING radio < %s;"
    condition = condition%(radio)
    return [(7,select),(45,condition)]

def add_station_list(station_list):
    if len(station_list) == 1:
        station_list = f"('{station_list[0]}')"
    else:
        station_list = str(tuple(station_list))
    condition = ("pick_p.waveformID_stationCode in %s AND")%(station_list)
    return [(42,condition)]

def add_id_query(loc_id):
    condition = "POEv.PublicID = '%s' AND"%(loc_id)
    return [(40,condition)]

def str2datetime(mydatetime):
    date,hour = mydatetime.split()
    year,month,day,hour,minute,sec = date[0:4],date[4:6],date[6:8],hour[0:2],hour[2:4],hour[4:6]
    return f"{year}/{month}/{day} {hour}:{minute}:{sec}"
    
class PickQuery(object):
    def __init__(self,initial_date,final_date,  
                    min_mag,max_mag,min_prof,max_prof,
                    event_type=None,station_list=None):
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
        event_type: str
            "earthquake" or "not locatable" etc
        station_list: list
            Only select stations located in station_list
        """
        self.initial_date = str2datetime(initial_date)
        self.final_date = str2datetime(final_date)
        self.min_mag = min_mag
        self.max_mag = max_mag
        self.min_prof = min_prof
        self.max_prof = max_prof
        self.event_type = event_type
        self.station_list = station_list

        pick_text = open(pick_codex,"r", encoding="latin-1").readlines()
        pick_text = get_text2php(pick_text)
        self.pick_text = str(pick_text)%(f'{self.min_mag}',f'{self.max_mag}',
                                f'{self.min_prof}',f'{self.max_prof}',
                                f'"{self.initial_date}"',
                                f'"{self.final_date}"')
    

    def query(self):
        text = self.pick_text

        if self.event_type != None:
            text = io.StringIO(text).readlines()
            event_info = add_event_type(self.event_type)
            text = get_text2php(from_text=text,
                                add_line=event_info)

        if self.station_list != None:
            text = io.StringIO(text).readlines()
            stalist_info = add_station_list(self.station_list)
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
        text = io.StringIO(self.pick_text).readlines()
        id_text = add_id_query(loc_id)
        text = get_text2php(from_text=text,
                                add_line=id_text)

        if self.event_type != None:
            text = io.StringIO(text).readlines()
            event_info = add_event_type(self.event_type)
            text = get_text2php(from_text=text,
                                add_line=event_info)

        if self.station_list != None:
            text = io.StringIO(text).readlines()
            stalist_info = add_station_list(self.station_list)
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
        text = io.StringIO(self.pick_text).readlines()
        radial_text = add_radial_query(lat, lon, radio)
        text = get_text2php(from_text=text,
                                add_line=radial_text)
                        
        if self.event_type != None:
            text = io.StringIO(text).readlines()
            event_info = add_event_type(self.event_type)
            text = get_text2php(from_text=text,
                                add_line=event_info)

        if self.station_list != None:
            text = io.StringIO(text).readlines()
            stalist_info = add_station_list(self.station_list)
            text = get_text2php(from_text=text,
                                         add_line=stalist_info)
        return text