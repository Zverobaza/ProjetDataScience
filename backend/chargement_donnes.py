import pandas as pd
import os

def load_consumption_data(data_dir):
    """
    Charge et combine les données de consommation énergétique depuis plusieurs fichiers CSV.

    Args:
        data_dir (str): Chemin vers le répertoire contenant les fichiers de données.

    Returns:
        pd.Series: Série temporelle de la consommation énergétique triée par datetime.
    """
    files = [
        os.path.join(data_dir, 'energy_data2023.csv'),
        os.path.join(data_dir, 'energy_data2024.csv'),
        os.path.join(data_dir, 'energy_data2025.csv')
    ]

    # Charger et combiner les fichiers
    dfs = [pd.read_csv(file, sep=';', parse_dates=['datetime'], dayfirst=True) for file in files]
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df = combined_df.sort_values(by='datetime')
    combined_df.set_index('datetime', inplace=True)

    # Retourner la colonne 'Consommation'
    return combined_df['Consommation']