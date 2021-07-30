# -*- coding: utf-8 -*-
import click
import logging


import pandas as pd


def sample_data(data, location_to_save=None, percentage=1):
    """
    Reduce the size of raw data by given percentage. 
    The sampling method preserves the data variablity by making sure all carrier and airports are proportionally represented in each month.

    Parameters
    ----------
    data : DataFrame
        Raw dataframe to be sampled.
    percentage : INT, optional
        The percentage of original data to be retained.

    Returns
    -------
    sampled_df : Returns the sampled data as sampled_df. Adds two

    """
    
    data.loc[:,["fl_date","crs_arr_time","crs_dep_time"]] = data[["fl_date","crs_arr_time","crs_dep_time"]].astype('string')

    arr_time = pd.to_datetime(data["fl_date"]+" "+ data["crs_arr_time"].str.zfill(4).replace({'2400':'0000'}))
    dep_time = pd.to_datetime(data["fl_date"]+" "+ data["crs_dep_time"].str.zfill(4).replace({'2400':'0000'}))

    data["arr_date_time"] = arr_time
    data["dep_date_time"] = dep_time

    data['arr_month'] = data['arr_date_time'].dt.month
    
    sampled_data = data.groupby(by=["op_unique_carrier","arr_month","dest_airport_id"]).apply(_reduce_size,fraction=percentage/100).reset_index(drop=True)
    
    sampled_data = sampled_data.drop(columns=["Unnamed: 0","arr_month"])
    
    sampled_data.to_csv(location_to_save,index=False)
    
    return sampled_data
    
def _reduce_size(data,fraction):
    '''
    Returns fraction of data provided

    Parameters
    ----------
    data : DataFrame
        DataFrame to be sampled from
    fraction : FLOAT
        Fraction of the data to be returned

    Returns
    -------
    DataFrame
        returns the sampled dataset

    '''
    return data.sample(frac=fraction,random_state=3245)


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data sampling scripts to turn raw data from (../raw) into
        sampled data ready to be analyzed (saved in ../interim/1_sampled).
    """
    logger = logging.getLogger(__name__)
    logger.info('making sampled data set from raw data')
    
    data = pd.read_csv(input_filepath)
    intial_shape = data.shape[0]
    final_shape = sample_data(data,location_to_save=output_filepath,percentage=1).shape[0]
    
    print(f"Reduced the row count from {intial_shape} to {final_shape}")
    
    logger.info('Completed sampling the provided data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()



    