import click
import logging

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import timedelta, datetime


def build_all_features(data):
    data = airport_type(data)
    data = get_inbound_flights(data)
    
    return data

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
    Returns a dataframe

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
    
def _get_num_inbound_flights_carrier(data,df,minutes=-60,percentages_to_print=[],num_row_processed=[0]):
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
    TYPE
        Returns count of the inbound flights

    '''
    
    total_num = df.shape[0]
    if num_row_processed[0] in percentages_to_print:
        print(f"{datetime.now().time()} : {100*num_row_processed[0]/total_num}% rows processed")
        
    num_row_processed[0] = num_row_processed[0]+1
    carrier = data.mkt_unique_carrier
    airport = data.origin_airport_id
    date = data.dep_date_time
    fl_num = data.op_carrier_fl_num
    date_diff = date + timedelta(minutes=minutes)

    mask = ( 
    (df.mkt_unique_carrier==carrier) & (df.dest_airport_id==airport) & 
    (df.arr_date_time >= date_diff) & (df.arr_date_time <= date) & (df.op_carrier_fl_num != fl_num)
       )
    return df[mask].shape[0]

def get_inbound_flights(data):
    num_row_processed = [0]
    total_num = data.shape[0]
    percentages = np.round(np.linspace(0,total_num,11))
    data["inbound_flights"] = data.apply(_get_num_inbound_flights_carrier,axis=1,args=(data),percentages_to_print=percentages,num_row_processed = num_row_processed)
    return data

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs feature engineering scripts to turn sampled data from (../interim/1_sampled) into
        sampled data ready to be analyzed (saved in ../interim/2_feature_engineered).
    """
    logger = logging.getLogger(__name__)
    logger.info('Building features')
    
    data = pd.read_csv(input_filepath)
    data = data.astype({'arr_date_time':'datetime64[ns]','dep_date_time':'datetime64[ns]'})
    
    
    
    logger.info('Completed sampling the provided data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()