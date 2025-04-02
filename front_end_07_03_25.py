import pandas as pd
import re
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

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

# Chargement des fichiers Excel
conso_2023 = load_data("/Users/macos/Desktop/ProjetDataScience/data/energy_data2023.csv")
conso_2024 = load_data("/Users/macos/Desktop/ProjetDataScience/data/energy_data2024.csv")
conso_2025 = load_data("/Users/macos/Desktop/ProjetDataScience/data/energy_data2025.csv")

# Concaténation des données
df = pd.concat([conso_2023, conso_2024, conso_2025])
df = df.sort_values("date")  # Tri par date

# Initialisation de l'application Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Visualisation des données de consommation RTE"),
    
    dcc.DatePickerRange(
        id='date-picker',
        min_date_allowed=df['date'].min(),
        max_date_allowed=df['date'].max(),
        start_date=df['date'].min(),
        end_date=df['date'].max()
    ),
    
    dcc.Graph(id='time-series-graph'),

    # Ajout d'un menu déroulant pour choisir la variable à afficher
    dcc.Dropdown(
        id='variable-selector',
        options=[
            {'label': 'Consommation', 'value': 'consommation'},
            {'label': 'Prévision J-1', 'value': 'prevision_j_1'},
            {'label': 'Prévision J', 'value': 'prevision_j'}
        ],
        value='consommation',
        clearable=False
    )
])

@app.callback(
    Output('time-series-graph', 'figure'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('variable-selector', 'value')
)
def update_graph(start_date, end_date, selected_variable):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    fig = px.line(filtered_df, x='date', y=selected_variable, title=f"Évolution de {selected_variable}")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
