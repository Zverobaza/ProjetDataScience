import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import pmdarima as pm  # Pour Auto-ARIMA
from pathlib import Path

sns.set_style("whitegrid")  # Amélioration visuelle des graphiques

def read_energy_data(file_path):
    """Lit et prépare le fichier CSV."""
    try:
        df = pd.read_csv(file_path, sep=";", encoding="utf-8", low_memory=False)
        df.columns = df.columns.str.strip()  # Nettoyage des noms de colonnes

        if "datetime" not in df.columns:
            print("\n❌ Erreur : La colonne 'datetime' n'a pas été trouvée.")
            return None

        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df.set_index("datetime", inplace=True)

        # Vérification des valeurs NaN
        if df.isna().sum().sum() > 0:
            print("\n⚠️ Avertissement : Données manquantes détectées, application d'un forward fill.")
            df.fillna(method="ffill", inplace=True)

        print("\n✅ Données chargées avec succès !")
        print(df.info())
        return df

    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        return None

def test_stationarity(series):
    """Effectue le test de stationnarité ADF."""
    result = adfuller(series.dropna())
    print("\n📊 Test de stationnarité ADF")
    print(f"Statistique ADF : {result[0]:.4f}")
    print(f"p-value : {result[1]:.4f}")
    print("Seuils critiques :", result[4])

    if result[1] <= 0.05:
        print("✅ La série est stationnaire.")
        return True
    else:
        print("❌ La série n'est pas stationnaire. Une différenciation peut être nécessaire.")
        return False

def apply_differencing(series):
    """Applique la différenciation si nécessaire et reteste la stationnarité."""
    series_diff = series.diff().dropna()
    if test_stationarity(series_diff):
        return series_diff, 1  # d = 1
    else:
        print("🔁 Nouvelle différenciation appliquée.")
        return series_diff.diff().dropna(), 2  # d = 2

def seasonal_analysis(series, period):
    """Effectue une décomposition saisonnière."""
    print("\n🔍 Décomposition saisonnière")
    decomposition = seasonal_decompose(series, model="additive", period=period)
    
    plt.figure(figsize=(12, 8))
    plt.subplot(411)
    plt.plot(series, label="Série originale", color="blue")
    plt.legend()

    plt.subplot(412)
    plt.plot(decomposition.trend, label="Tendance", color="orange")
    plt.legend()

    plt.subplot(413)
    plt.plot(decomposition.seasonal, label="Saisonnalité", color="green")
    plt.legend()

    plt.subplot(414)
    plt.plot(decomposition.resid, label="Résidu", color="red")
    plt.legend()

    plt.tight_layout()
    plt.show()

def plot_acf_pacf(series):
    """Affiche les graphiques ACF et PACF pour l'identification des paramètres (p, q)."""
    print("\n📊 Analyse des autocorrélations")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    plot_acf(series.dropna(), ax=axes[0], lags=40)
    axes[0].set_title("Autocorrelation Function (ACF)")

    plot_pacf(series.dropna(), ax=axes[1], lags=40)
    axes[1].set_title("Partial Autocorrelation Function (PACF)")

    plt.show()

def auto_arima_selection(series):
    """Automatise la sélection des hyperparamètres avec Auto-ARIMA."""
    print("\n🚀 Sélection automatique des hyperparamètres avec Auto-ARIMA")
    model = pm.auto_arima(series, seasonal=True, m=24, stepwise=True, trace=True)
    print("\n✅ Modèle optimal trouvé :", model)
    return model

# 📂 Chargement des données
#PROJECT_ROOT = Path(__file__).parent.parent
#DATA_DIR = PROJECT_ROOT / "data"
#data_path = str(DATA_DIR)

file_path = "/Users/macos/Desktop/ProjetDataScience/data/energy_data2023.csv"
df = read_energy_data(file_path)

if df is not None:
    target_column = "Consommation"  # ⚠️ Change selon tes données
    if target_column in df.columns:
        series = df[target_column]

        # 📊 1. Test de stationnarité et différenciation
        is_stationary = test_stationarity(series)
        if not is_stationary:
            series, d_value = apply_differencing(series)
        else:
            d_value = 0  # Pas de différenciation nécessaire

        # 🔍 2. Détection de la saisonnalité
        seasonal_analysis(series, period=24)  # ⚠️ Modifier selon les données

        # 📊 3. ACF et PACF
        plot_acf_pacf(series)

        # 🚀 4. Sélection des hyperparamètres avec Auto-ARIMA
        best_model = auto_arima_selection(series)

    else:
        print(f"\n❌ La colonne '{target_column}' n'existe pas dans les données.")
