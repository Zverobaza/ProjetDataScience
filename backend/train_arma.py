import os
import joblib
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from chargement_donnes import load_consumption_data  # Importer la fonction de chargement des données

# Charger les données
data_dir = os.path.join(os.path.dirname(__file__), '../data')
consumption_series = load_consumption_data(data_dir)

# Entraîner le modèle ARMA
def train_arma_model(data):
    """
    Entraîne un modèle ARMA (AutoRegressif Moyenne Mobile) et retourne le modèle entraîné.
    """
    model = ARIMA(data, order=(1, 0, 1))
    results = model.fit()
    return results

# Entraîner et sauvegarder le modèle
results = train_arma_model(consumption_series)
model_path = os.path.join(os.path.dirname(__file__), 'arma_model.pkl')
joblib.dump(results, model_path)
print(f"Modèle ARMA sauvegardé sous '{model_path}'.")

# Visualiser les prédictions
predictions = results.predict(start=0, end=len(consumption_series)-1)

plt.figure(figsize=(12, 6))
plt.plot(consumption_series, label='Consommation réelle', color='blue')
plt.plot(predictions, label='Prédictions ARMA', color='orange', linestyle='dashed')
plt.title('Prédictions ARMA vs Consommation réelle')
plt.xlabel('Date')
plt.ylabel('Consommation')
plt.legend()
plt.grid()
plt.show()