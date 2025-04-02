import pandas as pd
import os
from pathlib import Path
def load_consumption_data(path): 
    """
    Charge et combine les données de consommation énergétique depuis plusieurs fichiers CSV.

    Args:
        path (str): Chemin vers le répertoire contenant les fichiers de données.

    Returns:
        pd.Series: Série temporelle de la consommation énergétique triée par datetime.
    """
    files = [
        os.path.join(path, 'energy_data2023.csv'),
        os.path.join(path, 'energy_data2024.csv'),
        os.path.join(path, 'energy_data2025.csv')
    ]

    # Charger et combiner les fichiers
    dfs = [pd.read_csv(file, sep=';', parse_dates=['datetime'], dayfirst=True) for file in files]
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df = combined_df.sort_values(by='datetime')
    combined_df.set_index('datetime', inplace=True)

    # Retourner tout le DataFrame
    return combined_df

if __name__ == '__main__':
 PROJECT_ROOT = Path(__file__).parent.parent
 DATA_DIR = PROJECT_ROOT / "data"
 data_path = str(DATA_DIR)
 h = load_consumption_data(data_path)
 print (h.head())