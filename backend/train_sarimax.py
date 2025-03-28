import os
import joblib
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from chargement_donnes import load_consumption_data  # Importer la fonction de chargement des données

# Charger les données
data_dir = os.path.join(os.path.dirname(__file__), '../data')
consumption_series = load_consumption_data(data_dir)

# Entraîner le modèle SARIMAX
def train_sarimax_model(data):
    """
    Entraîne un modèle SARIMAX (Saisonnalité AutoRegressif Moyenne Mobile) et retourne le modèle entraîné.
    """
    model = SARIMAX(data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))  # SARIMAX(p=1, d=1, q=1)(P=1, D=1, Q=1, s=12)
    results = model.fit()
    return results

# Entraîner et sauvegarder le modèle
results = train_sarimax_model(consumption_series)
model_path = os.path.join(os.path.dirname(__file__), 'sarimax_model.pkl')
joblib.dump(results, model_path)
print(f"Modèle SARIMAX sauvegardé sous '{model_path}'.")

# Visualiser les prédictions
predictions = results.predict(start=0, end=len(consumption_series)-1)

plt.figure(figsize=(12, 6))
plt.plot(consumption_series, label='Consommation réelle', color='blue')
plt.plot(predictions, label='Prédictions SARIMAX', color='orange', linestyle='dashed')
plt.title('Prédictions SARIMAX vs Consommation réelle')
plt.xlabel('Date')
plt.ylabel('Consommation')
plt.legend()
plt.grid()
plt.show()