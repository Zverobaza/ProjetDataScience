import pandas as pd
from datetime import datetime, time  # Correction 1: importer le type time

def read_special_excel(file_path):
    df = pd.read_excel(file_path, header=None, engine='openpyxl')
    
    current_date = None
    data = []
    daily_data = []
    
    for index, row in df.iterrows():
        # Détection de la date
        if str(row[0]).startswith('Journée du'):
            try:
                current_date = datetime.strptime(row[0].split('du ')[1], '%d/%m/%Y')
            except ValueError:
                current_date = None
            continue
        
        # Correction 2: Vérification du type time correctement
        if (isinstance(row[0], time) or (isinstance(row[0], str) and ':' in str(row[0]))):
            try:
                # Gestion du format heure
                if isinstance(row[0], str):
                    time_value = datetime.strptime(row[0], '%H:%M').time()
                else:
                    time_value = row[0].time() if isinstance(row[0], datetime) else row[0]
                
                # Création du datetime complet
                dt = datetime.combine(current_date, time_value)
                
                daily_data.append({
                    'datetime': dt,
                    'PrévisionsJ-1': row[1],
                    'PrévisionsJ': row[2],
                    'Consommation': row[3]
                })
            except Exception as e:
                print(f"Erreur ligne {index}: {e}")
                continue
        
        # Correction 3: Vérification des lignes vides avec sécurité
        if pd.isna(row[0]):
            # Vérifier qu'on n'est pas à la dernière ligne
            if index + 1 < len(df) and pd.isna(df.iloc[index + 1][0]):
                if daily_data and current_date:
                    data.extend(daily_data)
                    daily_data = []
                current_date = None
    
    return pd.DataFrame(data).set_index('datetime') if data else pd.DataFrame()

# Test
try:
    df = read_special_excel('conso_mix_RTE_2023.xlsx')
    print("Affichage des premières lignes :")
    print(df.head(300))
    print("\nTest réussi !")
    print(f"Nombre de points de données : {len(df)}")
except Exception as e:
    print(f"Erreur principale : {e}")

print("test")