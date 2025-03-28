import os
import joblib
from statsmodels.tsa.arima.model import ARIMA
from chargement_donnes import load_consumption_data  # Importer la fonction de chargement des données

# Charger les données
data_dir = os.path.join(os.path.dirname(__file__), '../data')
consumption_series = load_consumption_data(data_dir)

# Entraîner le modèle AR
def train_ar_model(data):
    """
    Entraîne un modèle AR (AutoRegressif) et retourne le modèle entraîné.
    """
    model = ARIMA(data, order=(1, 0, 0))
    results = model.fit()
    return results

# Entraîner et sauvegarder le modèle
results = train_ar_model(consumption_series)
model_path = os.path.join(os.path.dirname(__file__), 'ar_model.pkl')
joblib.dump(results, model_path)
print(f"Modèle AR sauvegardé sous '{model_path}'.")