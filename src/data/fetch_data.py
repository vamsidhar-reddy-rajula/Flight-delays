# -*- coding: utf-8 -*-
import click
import logging


import psycopg2
import sys, os
import numpy as np
import pandas as pd
# import example_psql as creds
import pandas.io.sql as psql

import credentials
import sql_helper



def get_num_rows(tables):
    '''
        Returns number of rows available

    Parameters
    ----------
    tables : list
        List of table names

    Returns
    -------
    row_count : TYPE
        Returns number of rows available as a map.

    '''
    con = psycopg2.connect(database=credentials.REMOTE["PGDATABASE"], user=credentials.REMOTE["PGUSER"], password=credentials.REMOTE["PGPASSWORD"], 
                           host=credentials.REMOTE["PGHOST"], port=credentials.REMOTE["PGPORT"])
    
    if con!=None:
        row_count = sql_helper.get_number_of_rows(tables,con,date_range=['20190101','20191231'])
        
    con.close()
    
    return row_count

def fetch_databases(tables):
    '''
    Returns all tables as a list of databases

    Parameters
    ----------
    tables : list
       List of table names

    Returns
    -------
    List of dataframes

    '''
    con = psycopg2.connect(database=credentials.REMOTE["PGDATABASE"], user=credentials.REMOTE["PGUSER"], password=credentials.REMOTE["PGPASSWORD"], 
                       host=credentials.REMOTE["PGHOST"], port=credentials.REMOTE["PGPORT"])

    if con!=None:
        dataframes = sql_helper.get_df_from_sql(tables,con,number_of_rows=None, date_range=["20190101","20191231"])
        
    con.close()
    
    return dataframes


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data fetching scripts to fetch data from server  (saved in ../raw/).
    """
    logger = logging.getLogger(__name__)
    logger.info('Fetching Raw data')
    
    
    tables = ["flights","passengers","fuel_comsumption","flights_test"]
    
    dataframes = fetch_databases(tables)
    
    for table_name,data in zip(tables,dataframes):
        data.to_csv(f"{table_name}.csv")
    
    logger.info('Completed Fetching Raw data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()