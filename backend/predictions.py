import pandas as pd
from backend.models import train_ar_model, train_sarimax_model, kalman_filter

def make_predictions(data):
    ar_model = train_ar_model(data)
    sarimax_model = train_sarimax_model(data)
    kf = kalman_filter(data)

    return {
        "AR": ar_model.predict(10).tolist(),
        "SARIMAX": sarimax_model.forecast(10).tolist(),
        "Kalman": [kf.x]  # Exemple, à adapter
    }
