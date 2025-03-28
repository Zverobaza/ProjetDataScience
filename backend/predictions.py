import pandas as pd
from backend.models import train_ar_model, train_sarimax_model, kalman_filter

def make_predictions(data):
    ar_model = train_ar_model(data)
    sarimax_model = train_sarimax_model(data)
    kf = kalman_filter(data)

    # Appliquer le filtre de Kalman
    filtered_values = []
    for consommation in data:
        kf.predict()
        kf.update([[consommation]])
        filtered_values.append(kf.x[0, 0])

    return {
        "AR": ar_model.predict(10).tolist(),
        "SARIMAX": sarimax_model.forecast(10).tolist(),
        "Kalman": filtered_values
    }
