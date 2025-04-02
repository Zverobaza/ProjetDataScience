import os
import joblib
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from chargement_donnes import load_consumption_data
import pandas as pd 
import plotly.express as px
from pmdarima import auto_arima
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.metrics import mean_absolute_error
import numpy as np

# Filter data to handle missing values and seasonal decomposition
def filter_data(data, cutoff_date):
    """
    Filtre les données jusqu'à une date donnée et gère les valeurs manquantes.
    
    Args:
        data (pd.DataFrame): Données à filtrer.
        cutoff_date (str): Date limite pour le filtrage au format 'YYYY-MM-DD HH:MM:SS'.
    
    Returns:
        pd.DataFrame: Données filtrées et traitées.
    """
    # Convertir la colonne datetime en index
    if 'datetime' in data.columns:
        data['datetime'] = pd.to_datetime(data['datetime'])
        data.set_index('datetime', inplace=True)
    
    # Filtrer les données
    filtered_data = data.loc[:cutoff_date].copy()
    
    # Gérer les valeurs manquantes
    for col in ['PrévisionsJ-1', 'PrévisionsJ', 'Consommation']:
        if col in filtered_data.columns:
            filtered_data.loc[:, col] = filtered_data[col].interpolate(method='time').bfill().ffill()
    
    # Seasonal decomposition
    if 'Consommation' in filtered_data.columns:
        try:
            result = seasonal_decompose(filtered_data['Consommation'], model='additive', period=96)
        except ValueError as e:
            print(f"Decomposition failed: {e}")
    
    # Check for missing values
    print("Missing values after processing:")
    print(filtered_data.isnull().sum())
    
    return filtered_data
# Message for user input
def user_input():
    """
    Fonction pour obtenir une entrée utilisateur avec un message d'invite.
    Affiche les options de modèle ARIMA et SARIMA disponibles.    
    Returns:
        str: Réponse de l'utilisateur.
    """
    print("Sélectionnez le modèle à entraîner :")
    print("1. ARIMA (auto)")
    print("2. SARIMA (manual)")
    print("3. SARIMAX (with exog variables)")
    choice = input("Entrez le numéro correspondant à votre choix : ")
    return choice
# Training models
def train_model(choice, train_series, exog_data=None):
    """
    Entraîne le modèle sélectionné.
    
    Args:
        choice (str): Choix du modèle ('1', '2', ou '3')
        train_series (pd.Series): Série temporelle d'entraînement
        exog_data (pd.DataFrame): Données exogènes (pour SARIMAX)
    
    Returns:
        tuple: (modèle entraîné, nom du modèle, type de modèle)
    """
    if choice == "1":
        print("Recherche des meilleurs paramètres ARIMA...")
        model = auto_arima(
            train_series,
            seasonal=True,
            m=96,
            trace=True,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )
        model_name = "ARIMA Automatique"
        print(model.summary())
        return model, model_name, 'auto_arima'
    
    elif choice == "2":
        model_name = "SARIMA(1,1,1)(1,1,1,96)"
        print(f"Entraînement du modèle {model_name}...")
        model = SARIMAX(
            train_series,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 96),
            enforce_stationarity=False
        )
        results = model.fit()
        print(results.summary())
        return results, model_name, 'sarima'
    
    elif choice == "3":
        if exog_data is None:
            raise ValueError("Des données exogènes sont nécessaires pour SARIMAX")
            
        model_name = "SARIMAX avec variables exogènes"
        print(f"Entraînement du modèle {model_name}...")
        model = SARIMAX(
            train_series,
            exog=exog_data,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 96),
            enforce_stationarity=False
        )
        results = model.fit()
        print(results.summary())
        return results, model_name, 'sarimax'
    
    else:
        raise ValueError("Choix de modèle invalide")
# Evaluate the model 
def evaluate_model(model, test_data, model_type, exog_test=None):
    """
    Évalue le modèle sur les données de test.
    
    Args:
        model: Modèle entraîné
        test_data (pd.Series): Données de test
        model_type (str): Type de modèle ('auto_arima', 'sarima', 'sarimax')
        exog_test (pd.DataFrame): Données exogènes de test (pour SARIMAX)
    
    Returns:
        tuple: (prédictions, MAE)
    """
    if model_type == 'auto_arima':
        predictions = model.predict(n_periods=len(test_data))
    elif model_type == 'sarima':
        predictions = model.get_forecast(steps=len(test_data)).predicted_mean
    elif model_type == 'sarimax':
        if exog_test is None:
            raise ValueError("Des données exogènes sont nécessaires pour SARIMAX")
        predictions = model.get_forecast(steps=len(test_data), exog=exog_test).predicted_mean
    
    mae = mean_absolute_error(test_data, predictions)
    print(f"MAE on test set: {mae:.2f}")
    return predictions, mae
# Make future predictions
def make_future_predictions(model, model_type, steps, last_exog=None):
    """
    Fait des prédictions futures.
    
    Args:
        model: Modèle entraîné
        model_type (str): Type de modèle
        steps (int): Nombre de pas à prédire
        last_exog (pd.DataFrame): Dernières données exogènes (pour SARIMAX)
    
    Returns:
        pd.Series: Prédictions futures
    """
    if model_type == 'auto_arima':
        return model.predict(n_periods=steps)
    elif model_type == 'sarima':
        return model.get_forecast(steps=steps).predicted_mean
    elif model_type == 'sarimax':
        if last_exog is None:
            raise ValueError("Des données exogènes sont nécessaires pour SARIMAX")
        if len(last_exog) < steps:
            raise ValueError(f"Besoin d'au moins {steps} observations exogènes")
        return model.get_forecast(steps=steps, exog=last_exog.iloc[:steps]).predicted_mean
# Visualize predictions
def visualize_predictions(actual_series, predictions, model_name, freq='15T'):
    """
    Visualise les résultats.
    
    Args:
        actual_series (pd.Series): Série temporelle réelle
        predictions (pd.Series): Prédictions
        model_name (str): Nom du modèle
        freq (str): Fréquence des données
    """
    future_dates = pd.date_range(
        start=actual_series.index[-1], 
        periods=len(predictions)+1, 
        freq=freq
    )[1:]

    predictions_df = pd.DataFrame({
        'Date': future_dates,
        'Consommation': predictions,
        'Type': f'Prédictions {model_name}'
    })

    real_data_df = pd.DataFrame({
        'Date': actual_series.index,
        'Consommation': actual_series.values,
        'Type': 'Consommation réelle'
    })

    combined_df = pd.concat([real_data_df, predictions_df])

    fig = px.line(
        combined_df,
        x='Date',
        y='Consommation',
        color='Type',
        markers=True,
        title=f'Prédictions {model_name} vs Consommation réelle'
    )
    fig.show()
# Save model
#def save_model(model, model_name, save_dir):
 #   """
  #  Sauvegarde le modèle.
   # 
   # Args:
    #    model: Modèle à sauvegarder
     #   model_name (str): Nom du modèle
      #  save_dir (str/Path): Répertoire de sauvegarde
    #"""
    #os.makedirs(save_dir, exist_ok=True)
    #filename = f"{model_name.replace(' ', '_')}.joblib"
    #joblib.dump(model, Path(save_dir) / filename)
    #print(f"Modèle sauvegardé sous {filename}")

# Main function to run the training and evaluation (initialization of all parameters))
def main():
    # Charger et préparer les données
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    data = load_consumption_data(str(DATA_DIR))
    
    # Sauvegarder les données brutes
    data.to_csv(DATA_DIR / "combined_energy_data.csv")
    
    # Filtrer et prétraiter les données
    cutoff_date = pd.to_datetime("2025-02-24 10:15:00")
    filtered_data = filter_data(data, cutoff_date)
    filtered_data.to_csv(DATA_DIR / "filtered_energy_data.csv")
    
    # Préparer les séries pour l'entraînement
    consumption_series = filtered_data['Consommation']
    train_size = int(len(consumption_series) * 0.9)
    train, test = consumption_series[:train_size], consumption_series[train_size:]
    
    # Préparer les données exogènes si nécessaire
    exog_train = exog_test = None
    if 'PrévisionsJ-1' in filtered_data.columns and 'PrévisionsJ' in filtered_data.columns:
        exog_train = filtered_data[['PrévisionsJ-1', 'PrévisionsJ']].iloc[:train_size]
        exog_test = filtered_data[['PrévisionsJ-1', 'PrévisionsJ']].iloc[train_size:train_size+len(test)]
    
    # Sélection du modèle
    choice = user_input()
    
    try:
        # Entraînement du modèle
        model, model_name, model_type = train_model(choice, train, exog_train)
        
        # Évaluation du modèle
        test_predictions, mae = evaluate_model(
            model, 
            test, 
            model_type,
            exog_test if model_type == 'sarimax' else None
        )
        
        # Prédictions futures
        future_steps = 10
        future_pred = make_future_predictions(
            model,
            model_type,
            future_steps,
            filtered_data[['PrévisionsJ-1', 'PrévisionsJ']].iloc[-future_steps:] if model_type == 'sarimax' else None
        )
        
        # Visualisation
        freq = pd.infer_freq(consumption_series.index) or '15T'
        visualize_predictions(consumption_series, future_pred, model_name, freq)
        
        # Sauvegarde du modèle
        #save_model(model, model_name, DATA_DIR)
        
    except Exception as e:
        print(f"Erreur: {e}")
        return

if __name__ == "__main__":
    main()