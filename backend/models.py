import pandas as pd
import pmdarima as pm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from filterpy.kalman import KalmanFilter

# Exemple d'un modèle AutoRegressif (AR)
def train_ar_model(data):
    model = pm.auto_arima(data, seasonal=False)
    return model

# Exemple d'un modèle SARIMAX
def train_sarimax_model(data):
    model = SARIMAX(data, order=(1,1,1), seasonal_order=(1,1,1,12))
    return model.fit()

# Exemple d'un filtre de Kalman simple
def kalman_filter(data):
    kf = KalmanFilter(dim_x=1, dim_z=1)
    kf.x = data[0]  # État initial
    return kf
