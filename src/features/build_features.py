import click
import logging

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import timedelta, datetime
from tqdm import tqdm


def airport_type(data):
    '''
    Returns a dataframe with two new columns - origin_airport_type, dest_airport_type.
    Airports are divided into 5 categories based on number of flights flying from each one from "Very Large" to "Very Small"

    Parameters
    ----------
    data : DataFrame
        Dataframe with origin_airport_id and dest_airport_id features

    Returns
    -------
    Returns a dataframe with types for airports: 'Very Large','Large','Medium','Small','Very Small'

    '''
    origin_airport = data["origin_airport_id"].value_counts()
    dest_airport = data["dest_airport_id"].value_counts()
    
    airports = pd.concat([origin_airport,dest_airport],axis=1)
    airports = airports.sort_values(by=["origin_airport_id"],ascending=False)
    
    df1, df2, df3, df4, df5 = np.array_split(airports, 5)
    
    df1["Type"] = "Very Large"
    df2["Type"] = "Large"
    df3['Type'] = "Medium"
    df4["Type"] = "Small"
    df5["Type"] = "Very Small"
    
    airport_type = pd.concat([df1,df2,df3,df4,df5]).drop(columns=["origin_airport_id","dest_airport_id"]).to_dict()['Type']
    
    data["origin_airport_type"] = data.origin_airport_id.map(lambda x: airport_type[x] )
    data["dest_airport_type"] = data.dest_airport_id.map(lambda x: airport_type[x] )
    
def _get_num_inbound_flights_carrier(data,df,minutes=-60):
    '''
    Finds out the number of inbound flights from same carrier are ariving in a time period of 60 minutes before departure.
    

    Parameters
    ----------
    data : Series
        Each row from original dataframe 
    df : Complete DataFrame
        original dataframe to be masked
    minutes : INT, optional
        Number of miutes to account for. The default is -60.
    percentages_to_print : FLOAT, optional
        Percentage of data processed.This value will only be used for display purposes. The default is [].
    num_row_processed : row number to track, optional
        Number of rows processed. This calue will only be used for display plurposes. The default is [0].

    Returns
    -------
    INT
        Returns count of the inbound flights

    '''
    
    carrier = data.mkt_unique_carrier
    airport = data.origin_airport_id
    date = data.dep_date_time
    fl_num = data.op_carrier_fl_num
    date_diff = date + timedelta(minutes=minutes)
    
    mask = ( 
    (df.mkt_unique_carrier==carrier) & (df.dest_airport_id==airport) & 
    (df.arr_date_time >= date_diff) & (df.arr_date_time <= date) & (df.op_carrier_fl_num != fl_num)
       )
    return len(df.loc[mask,:])


def _get_departing_flight_count(data,df,minutes=-30):
    '''
    
    Returns number of flights expected to depart in the provided timeframe from origin    

    Parameters
    ----------
    data : Series
        Single instance from the flights dataframe.
    df : DataFrame
        Flights dataframe.
    minutes : INT, optional
        Timeframe to look for. The default is 30.

    Returns
    -------
    INT
        Number of flights departing during the same departure time from a given airport and date.

    '''
    airport = data.origin
    date = data.dep_date_time
    date_diff = date + timedelta(minutes=minutes)

    mask = ( (df.origin ==airport) & (df.dep_date_time >= date_diff) & (df.dep_date_time <= date))
    
    return len(df[mask])-1

def _get_num_arr_flights(data,df,minutes=30):
    '''
    
    Returns number of flights expected to arrive in the provided timeframe at destination    

    Parameters
    ----------
    data : Series
        Single instance from the flights dataframe.
    df : DataFrame
        Flights dataframe.
    minutes : INT, optional
        Timeframe to look for. The default is 30.

    Returns
    -------
    INT
        Number of flights arriving during the same arrival time from a given airport and date.

    '''
    
    airport = data.dest
    date = data.arr_date_time + timedelta(minutes=minutes)
    date_diff = date - timedelta(minutes=minutes)

    mask = ( (df.dest ==airport) & (df.arr_date_time >= date_diff) & (df.arr_date_time <= date))
    
    return len(df[mask])-1
    

def _get_weather(data,weather_kaggle):
    '''
    Returns weather Type and Severity details for each instance in the flights dataframe

    Parameters
    ----------
    data : Series
        Series passed should contain following features to get weather: 'arr_date_time','dep_date_time','origin','dest'
    weather_kaggle: DataFrame
        Send weather dataframe to search for the exact weather type and severity

    Returns
    -------
    weather_details : Series
        returns a series with 2 new weather features(Type and Severity) for origin and dest

    '''

    
    arr_time = data.arr_date_time
    dep_time = data.dep_date_time
    origin_id = data.origin
    dest_id = data.dest
    
    weather_details = pd.Series(dtype='string')
    
    try:
        weather_details["arr_type"] ,weather_details["arr_severity"] = weather_kaggle[(weather_kaggle["StartTime(UTC)"]<arr_time)&
                  (weather_kaggle["AirportCode"]=="K"+dest_id)].sort_values(by='StartTime(UTC)',ascending=False).iloc[0][['Type','Severity']]
    except IndexError:
        weather_details["arr_type"] ,weather_details["arr_severity"] = np.nan,np.nan
        
    try:
          weather_details["dep_type"] ,weather_details["dep_severity"] = weather_kaggle[(weather_kaggle["StartTime(UTC)"]<dep_time)&
                  (weather_kaggle["AirportCode"]=="K"+origin_id)].sort_values(by='StartTime(UTC)',ascending=False).iloc[0][['Type','Severity']]
    except IndexError:
        weather_details["dep_type"] ,weather_details["dep_severity"] = np.nan, np.nan
    
    return weather_details

def _get_population():
    data = pd.read_csv(r"../../data/external/census_data.csv")
    population = data.groupby("STNAME").sum()
    codes = pd.read_csv(r"../../data/external/state codes.csv")
    population = pd.merge(left=population,right=codes,right_on='Name',left_index=True)
    population = population.set_index('State or Region Code')
    population.loc["DC","POPESTIMATE2019"] = 705749
    population.loc["VI","POPESTIMATE2019"] = 104578
    population.loc["PR","POPESTIMATE2019"] = 3654474
    population.loc["TT","POPESTIMATE2019"] = 1394969
    return population

def _get_airport_info():
    airport_details = pd.read_csv(r"../../data/external/faa_airport_details.csv")
    airport_details = airport_details.set_index("airport_code")
    airport_details.area = airport_details.area.replace({"":np.nan})
    return airport_details

def _get_enplanements():
    enplanemntes = pd.read_excel("../../data/external/preliminary-cy20-commercial-service-enplanements.xlsx")
    enplanemntes = enplanemntes[["Locid","CY 19 Enplanements"]]
    return enplanemntes

def _get_weather_source():
    weather_kaggle = pd.read_csv(r"../../data/external/WeatherEvents_Jan2016-Dec2020.csv")
    weather_kaggle = weather_kaggle.astype({'StartTime(UTC)':'datetime64[ns]',
                                    'EndTime(UTC)':'datetime64[ns]'})
    weather_kaggle = weather_kaggle[(weather_kaggle["StartTime(UTC)"]>datetime(year=2019,month=1,day=1))&
                            (weather_kaggle["EndTime(UTC)"]<datetime(year=2020,month=2,day=1))]
   
    return weather_kaggle

def save_file(data,output_filepath):
    data.to_csv(output_filepath)

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
@click.option('--inbound_flights',help="How long back would you like to consider?")
@click.option('--scheduled_departing_flights',help="How many minutes before departure would you like to consider?")
@click.option('--scheduled_arriving_flights',help="Howmany minutes before and after arrivaltime would you like to consider?")
@click.option('--weather',is_flag=True)
@click.option('--state_names', is_flag=True)
@click.option('--population',is_flag=True)
@click.option('--enplanements',is_flag=True)
@click.option('--airport_info',is_flag=True)
@click.option('--timings',is_flag=True)
@click.option('--cont',is_flag=True)
def main(input_filepath, output_filepath,weather,
         state_names,population,enplanements,airport_info,timings,cont,
         inbound_flights=0,scheduled_departing_flights=0,scheduled_arriving_flights=0):
    """ Runs feature engineering scripts to turn sampled data from (../interim/1_sampled) into
        sampled data ready to be analyzed (saved in ../interim/2_feature_engineered).
    """
    logger = logging.getLogger(__name__)
    logger.info('Building features')
    
    if cont:
        data = pd.read_csv(output_filepath)
    else:
        data = pd.read_csv(input_filepath)
        
    data = data.astype({'arr_date_time':'datetime64[ns]','dep_date_time':'datetime64[ns]'})
    tqdm.pandas()
    if inbound_flights:
        logger.info('Started generating the feature: "inbound_flights"')
        data["inbound_flights"] = data.progress_apply(_get_num_inbound_flights_carrier,axis=1,args=(data,-1*int(inbound_flights)))
        save_file(data,output_filepath)
        logger.info('Completed generating the feature: "inbound_flights"')
    if scheduled_departing_flights:
        logger.info('Started generating the feature: "dep_flight_count"')
        data.loc[:,"dep_flights_count"] = data.progress_apply(_get_departing_flight_count,axis=1,args=(data,-1*int(scheduled_departing_flights)))
        save_file(data,output_filepath)
        logger.info('Completed generating the feature: "dep_flight_count"')
    if scheduled_arriving_flights:
        logger.info('Started generating the feature: "arr_flights_count"')
        data.loc[:,"arr_flights_count"] = data.progress_apply(_get_num_arr_flights,axis=1,args=(data,int(scheduled_arriving_flights)))
        save_file(data,output_filepath)
        logger.info('Completed generating the feature: "arr_flights_count"')
    if weather:
        data.origin = data.origin.replace({'FCA':'GPI','SCE':'UNV','BKG':'BBG','AZA':'IWA','USA':'JQF',
                      'MQT':'SAW','YUM':'NYL','HHH':'HXD'})
        data.dest = data.dest.replace({'FCA':'GPI','SCE':'UNV','BKG':'BBG','AZA':'IWA','USA':'JQF',
                      'MQT':'SAW','YUM':'NYL','HHH':'HXD'})
        logger.info('Started generating the feature: "arr_type","arr_severity","dep_type","dep_severity"')
        weather_kaggle = _get_weather_source()
        weather_details = data.progress_apply(_get_weather,axis=1,args=(weather_kaggle,))
        data = pd.merge(left=data,right=weather_details,left_index=True,right_index=True,how='left')
        save_file(data,output_filepath)
        logger.info('Completed generating the feature: "arr_type","arr_severity","dep_type","dep_severity"')
    if state_names:
        data["origin_state"] = data.origin_city_name.map(lambda x: x.split(", ")[1])
        data["dest_state"] = data.dest_city_name.map(lambda x: x.split(", ")[1])
        save_file(data,output_filepath)
    if population:
        population = _get_population()
        data["origin_population"] = data.origin_state.map(lambda x: population.loc[x]["POPESTIMATE2019"])
        data["dest_population"] = data.origin_state.map(lambda x: population.loc[x]["POPESTIMATE2019"])
        save_file(data,output_filepath)
    if enplanements:
        enplanements = _get_enplanements()
        data = pd.merge(left=data,right=enplanements,how="left",left_on="origin",right_on="Locid")
        save_file(data,output_filepath)
    if airport_info:
        airport_details = _get_airport_info()
        data = pd.merge(left=data,right=airport_details,right_index=True,left_on='origin',how='left')
        data = pd.merge(left=data,right=airport_details,right_index=True,left_on='dest',suffixes=("_or","_des"),how='left')
        save_file(data,output_filepath)
    if timings:
        data['arr_month'] = data['arr_date_time'].dt.month
        data['arr_day_of_week'] = data['arr_date_time'].dt.day_of_week
        data['arr_hour'] = data['arr_date_time'].dt.hour
        data['dep_month'] = data['dep_date_time'].dt.month
        data['dep_day_of_week'] = data['dep_date_time'].dt.day_of_week
        data['dep_hour'] = data['dep_date_time'].dt.hour
        save_file(data,output_filepath)
        
    logger.info('Completed building all the features specified!')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()