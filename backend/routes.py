from fastapi import APIRouter
from backend.services import load_data
from backend.predictions import make_predictions

router = APIRouter()

# Route pour récupérer les données
@router.get("/data")
def get_data():
    df = load_data("data/conso_mix_RTE_2025.xlsx")
    return df.to_dict(orient="records")

# Route pour faire des prédictions
@router.post("/predict/")
def predict():
    df = load_data("data/conso_mix_RTE_2025.xlsx")
    data = df.iloc[:, 3].dropna().tolist()  # Colonne "Consommation"
    predictions = make_predictions(data)
    
    return {"predictions": predictions}
