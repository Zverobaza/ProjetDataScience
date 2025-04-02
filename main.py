from fastapi import FastAPI
import pandas as pd
from backend.predictions import make_predictions

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API de prévision de consommation"}

@app.post("/predict/")
def predict():
    # Charger les données
    df = pd.read_csv("energy_data2023.csv")

    # Sélectionner les données de consommation
    data = df.iloc[:, 3].dropna().tolist()  # Colonne "Consommation"

    # Faire les prédictions
    predictions = make_predictions(data)
    
    return {"predictions": predictions}
