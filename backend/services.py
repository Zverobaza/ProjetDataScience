import pandas as pd
import re

# Fonction pour charger et structurer les données
def load_data(file_path):
    df = pd.read_excel(file_path, engine='openpyxl', header=None)  # Lecture brute du fichier sans en-tête
    data_list = []  # Liste pour stocker les données finales
    current_date = None  # Variable pour suivre la date courante

    for i in range(len(df)):
        row = df.iloc[i]

        # Vérifie si la ligne contient la date avec le format "Journée du XX/XX/XXXX"
        if isinstance(row[0], str) and "Journée du" in row[0]:
            match = re.search(r"(\d{2}/\d{2}/\d{4})", row[0])
            if match:
                current_date = match.group(1)  # Extraire la date au format XX/XX/XXXX

        # Vérifie si la ligne contient les données horaires (ex: "0:00", "12:15")
        elif isinstance(row[0], str) and re.match(r"\d{1,2}:\d{2}", row[0]):  # Format "H:MM" ou "HH:MM"
            if current_date:
                try:
                    full_datetime = pd.to_datetime(f"{current_date} {row[0]}", format="%d/%m/%Y %H:%M")
                    data_list.append([
                        full_datetime,
                        row[1],  # PrévisionJ-1
                        row[2],  # PrévisionJ
                        row[3]   # Consommation
                    ])
                except Exception as e:
                    print(f"Erreur de parsing à la ligne {i}: {e}")

    # Création du DataFrame
    df_clean = pd.DataFrame(data_list, columns=["date", "prevision_j_1", "prevision_j", "consommation"])
    
    return df_clean

