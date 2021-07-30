import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import seaborn as sns
import matplotlib.pyplot as plt
# Import stats from scipy library
from scipy import stats
import statsmodels.api as sm


from sklearn.model_selection import train_test_split,GridSearchCV,RandomizedSearchCV
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.linear_model import LinearRegression

from sklearn.preprocessing import PolynomialFeatures

from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
from sklearn.feature_selection import SequentialFeatureSelector

from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

import xgboost as xgb

import click
import logging



@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs modelling scripts to turn feature engineered data from (../interim/2_feature_engineered) into
        model ready to be predicted (saved in ../models/).
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