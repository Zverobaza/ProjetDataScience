import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import os
import joblib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

file_paths = ["data_2023.csv", "data_2024.csv", "data_2025.csv"]
dfs = [pd.read_csv(file, sep=";") for file in file_paths]

df = pd.concat(dfs, ignore_index=True)  
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])  
df = df.sort_values("datetime")  
#  Initialiser le Filtre de Kalman
kf = KalmanFilter(dim_x=2, dim_z=1)  

kf.F = np.array([[1, 1],  
                 [0, 1]])  

kf.H = np.array([[1, 0]])  

kf.P *= 1000  
kf.Q = np.array([[1, 0],  
                 [0, 1]])  

kf.R = np.array([[5]])  

kf.x = np.array([[df["Consommation"].iloc[0]],  
                 [0]])  

# Appliquer le filtre
filtered_values = []
for consommation in df["Consommation"]:
    kf.predict()
    kf.update(np.array([[consommation]]))  
    filtered_values.append(kf.x[0, 0])

df["Kalman_Filtré"] = filtered_values
df["Erreur"] = df["Consommation"] - df["Kalman_Filtré"]

# Visualisation avec 2 graphiques
fig, axs = plt.subplots(2, 1, figsize=(15, 8), sharex=True)

# Graphique 1 : Consommation réelle vs Kalman
axs[0].plot(df["datetime"], df["Consommation"], label="Consommation réelle", alpha=0.6)
axs[0].plot(df["datetime"], df["Kalman_Filtré"], label="Kalman Filtré", linestyle="dashed")
axs[0].set_ylabel("Consommation (MW)")
axs[0].legend()
axs[0].set_title("Filtrage de Kalman sur les données de consommation")

# Graphique 2 : Erreur entre la consommation réelle et filtrée
axs[1].plot(df["datetime"], df["Erreur"], color="red", label="Erreur (Réel - Kalman)")
axs[1].set_xlabel("Date")
axs[1].set_ylabel("Erreur (MW)")
axs[1].legend()
axs[1].set_title("Erreur entre la consommation réelle et le modèle filtré")

plt.tight_layout()
plt.show()
