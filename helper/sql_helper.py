import pandas as pd

def _get_values(table_name,con,limit=None,date_range=None):
    '''
        Return values from the given table
        
    '''
    cur = con.cursor()
    query =  (f"SELECT * from {table_name} WHERE fl_date>='{date_range[0]}' AND fl_date<='{date_range[1]}'" if limit==None else f"SELECT * from {table_name} LIMIT {limit}") if ((date_range!=None) and (table_name=="flights")) else  (f"SELECT * from {table_name}" if limit==None else f"SELECT * from {table_name} LIMIT {limit}")
    print(query)
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    return rows

def _get_column_names(table_name,con):
    '''
    Return column names for a given table
    
    '''
    columns = []  
    cur = con.cursor()
    col_names_str = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE "
    col_names_str += "table_name = '{}';".format( table_name )
    try:
        cur.execute(col_names_str)
        col_names = ( cur.fetchall() )
        for tup in col_names:
            columns += [ tup[0] ]
        cur.close()
    except Exception as err:
        print ("get_columns_names ERROR:", err)
    return columns

def get_df_from_sql(table_names,con,number_of_rows=None,date_range = None):
    
    dataframes = []
    if number_of_rows != None:
        if len(number_of_rows)==1 and len(number_of_rows)!=len(table_names):
            number_of_rows = number_of_rows*len(table_names)
        for table_name,row_count in zip(table_names,number_of_rows):
            column_names = _get_column_names( table_name,con)
            rows = _get_values(table_name,con,row_count,date_range)
            dataframes.append(pd.DataFrame(data=rows,columns=column_names))      
    else:
        for table_name in table_names:
            column_names = _get_column_names( table_name,con)
            rows = _get_values(table_name,con,number_of_rows,date_range)
            dataframes.append(pd.DataFrame(data=rows,columns=column_names))
        
        
    return dataframes


def get_number_of_rows(table_names,con,date_range=None):
    
    row_count = {}
    
    cur = con.cursor()
    for table_name in table_names:
        if table_name != "flights":
            query = f"SELECT COUNT(*) FROM {table_name}"
        else:
            query = f"SELECT COUNT(*) FROM {table_name} WHERE fl_date >= '{date_range[0]}' AND fl_date < '{date_range[1]}'"
            
        cur.execute(query)
        row_count[table_name] = cur.fetchall()[0][0]
    cur.close()
    
    return row_count