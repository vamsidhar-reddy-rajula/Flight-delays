# Goal of the project is to predict **arrival delays** of domestic flights in USA.

# How to work with this repo:

- Copy credentials.py file into the [data](src/data) folder. Refer [credentials_sample.py](src/data/credentials_sample.py) for the details and format expected.
- Run the files in following order (refer documentation of each module for futher instructions):

  - Fetch the raw data from server - [fetch_data.py](src/data/fetch_data.py)
  - Sample the dataset - [make_dataset.py](src/data/make_dataset.py)
    ```
    python .\make_dataset.py --percentage=3 "..\..\data\raw\flights_2019.csv" "..\..\data\interim\1_sampled\3_percent.csv"
    ```
  - Build Features - [build_features.py](src/features/build_features.py)
    ```
    python .\build_features.py --inbound_flights=30 --scheduled_departing_flights=30 --scheduled_arriving_flights=30 --weather --state_names --population --enplanements --airport_info --timings "..\..\data\interim\1_sampled\1_percent.csv" "..\..\data\interim\2_feature_engineered\1_percent.csv"
    ```
    -Full set of options to build various features and the values they accept can be found with:
    ```
    python .\build_features.py --help
    ```
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

The top contributor for delays was "Late Airlines" accounting to almost 37% of delays. Features were chosen which were thought to be the underlying cause for five delays outlined above.

## Feature Creation and Extraction

To correctly predict the traget variable, following features have been generated from multiple sources:

- Weather in 2019 [US Weather Events (2016 - 2020)](https://www.kaggle.com/sobhanmoosavi/us-weather-events)
- Airport details such as Number of runways, Latitude and Logitude, ownership type, Area hub type etc., [FAA Website](https://adip.faa.gov/agis/public/#/airportSearch)
- City population in 2019 [US Census 2019](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html)
- Number of Enplanements from airports in 2019 [passenger Boarding](https://www.faa.gov/airports/planning_capacity/passenger_allcargo_stats/passenger/)
- Number of connecting flights expected to arrive before scheduled departure time
- Number of competing flights to land or depart from an airport

## Preprocessing

- Missing values were dealt with appropriately by either filling in the values with frequently occuring category or mean (if appropriate)
- Extreme outliers were dropped from target variable
- Transformed the features into normal distribution before Regression analysis
- Scaled the features before modelling
- Investigated the effect of reducing components, selecting k-best features on accuracy of the model

# Model

The data has been trained with multiple regression models such as **Linear Regression, PolynomialRegression, RandomForestRegression and XGBoostRegression**.

## Regression

The best score we could attain was 0.070 with XGboostRegressor and 10% of 2019 flights data.
Predictions for the first week of 2020 can be seen at [predictions.csv\*](reports/predictions.csv).

\*Weather was not included in predictions due to time constraints and the performance of the predictions will be slightly affected due to the absence of this feature.

## Classification

Multinomial Classification - based on 5 types of the delays provided in data incl. weather_delay, nas_delay, security_delay, late_aircraft_delay, carrier_delay - used SMOTE for oversampling - 13k-26k rows - best score XGBClassifier with 0.6744 F1_score

Binary Classification - based on Cancelled flights data - used SMOTE for oversampling on minority, which is "flight cancelled" in this case - 150k-300k rows - best score XGBClassifier with 0.9907 F1_score
