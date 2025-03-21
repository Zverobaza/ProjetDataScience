import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import os
import joblib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Étape 1 : Définir les chemins d'accès aux fichiers CSV
data_dir = os.path.join(os.path.dirname(__file__), '../data')
files = [
    os.path.join(data_dir, 'energy_data2023.csv'),
    os.path.join(data_dir, 'energy_data2024.csv'),
    os.path.join(data_dir, 'energy_data2025.csv')
]

# Étape 2 : Lire les fichiers CSV
dataframes = []
for file in files:
    # Lire le fichier CSV avec la colonne 'datetime'
    df = pd.read_csv(file, sep=';', parse_dates=['datetime'], dayfirst=True)
    dataframes.append(df)

# Étape 3 : Combiner les données en un seul DataFrame
combined_df = pd.concat(dataframes, ignore_index=True)

# Étape 4 : Préparer les données pour l'analyse des séries temporelles
# Trier par datetime
combined_df = combined_df.sort_values(by='datetime')

# Définir la colonne 'datetime' comme index
combined_df.set_index('datetime', inplace=True)

# Sélectionner la colonne 'Consommation' pour l'analyse
consumption_series = combined_df['Consommation']

# Étape 5 : Entraîner un modèle ARMA (ARIMA avec d=0)
p = 1  # Ordre AR (AutoRegressive)
q = 1  # Ordre MA (Moving Average)
model = ARIMA(consumption_series, order=(p, 0, q))
results = model.fit()

# Afficher un résumé du modèle
print(results.summary())

# Prédictions
predictions = results.predict(start=0, end=len(consumption_series)-1)

# Étape 6 : Sauvegarder le modèle
joblib.dump(results, 'arima_model.pkl')
print("Modèle ARIMA sauvegardé sous 'arima_model.pkl'.")

# Étape 7 : Rééchantillonner les données par jour (moyenne quotidienne)
consumption_daily = consumption_series.resample('D').mean()
predictions_daily = predictions.resample('D').mean()

# Étape 8 : Créer une figure avec deux sous-graphiques côte à côte
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))

# Graphique 1 : Valeurs réelles (quotidiennes)
ax1.plot(consumption_daily.index, consumption_daily, label='Valeurs réelles', color='blue')
ax1.set_title('Valeurs réelles de la Consommation (Quotidiennes)')
ax1.set_xlabel('Date')
ax1.set_ylabel('Consommation')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
ax1.tick_params(axis='x', rotation=45)
ax1.legend()
ax1.grid()

# Graphique 2 : Prédictions (quotidiennes)
ax2.plot(predictions_daily.index, predictions_daily, label='Prédictions', color='red', linestyle='--')
ax2.set_title('Prédictions ARIMA de la Consommation (Quotidiennes)')
ax2.set_xlabel('Date')
ax2.set_ylabel('Consommation')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
ax2.tick_params(axis='x', rotation=45)
ax2.legend()
ax2.grid()

# Ajuster l'espace entre les sous-graphiques
plt.tight_layout()

# Afficher la figure
plt.show()