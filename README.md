# The goal of the project is to predict the arrival delays of domestic flights.

# How to work with this repo:

- Copy credentials.py file into the [data](src/data) folder. Refer credentials_sample.py for the details and format expected.
- Run the files in following order (refer documentation of each module for futher instructions):
  - Fetch the raw data - [fetch_data.py](src/data/fetch_data.py)
  - Sample the dataset - [make_dataset.py](src/data/make_dataset.py)
  - Build Features - [build_features.py](src/features/build_features.py)
  - Train the model [train_model.py](src/models/train_model.py) \*
  - Predict the model [predict_model.py](src/models/predict_model.py)\*
    \*The last two files are not finished yet and are being translated from the notebooks. Refer the [Jupyter notebooks](notebooks/) avaialble to reproduce the results for now.

# Dataset

The dataset is comprised of 4 tables.

- flights
- passengers
- fuel_consumption
- test

# Feature Engineering

The majority of delays were related to the following 5 categories:

1. Weather
2. Security
3. Carrier
4. NAS
5. Late Airlines

## Feature Extraction

To correctly predict the traget variable, following features have been extracted from multiple sources:

- Weather in 2019 (Kaggle datasource)
- Airport details such as Number of runways, (faa website)
- City population (US Census 2019)
- Number of Enplanements fromairports in 2019 (website)
- Number of connecting flights, Number of competing flights to land or depart from an airport

## Missing values and Outlier Treatment

- There were

# Model

The data has been trained with multiple regression models such as Linear Regression, PolynomialRegression, RandomForestRegression and XGBoostRegression.

## Regression

The best score we could attain was 0.068 with XGboostRegressor and 10% of 2019 flights data

## Classification
