import pydash as dash
from dash import dcc, html, Input, Output, Dash
import pandas as pd
import plotly.express as px
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

        # Vérifie si la ligne contient les données horaires
        elif isinstance(row[0], str) and re.match(r"\d{2}:\d{2}", row[0]):  # Format "HH:MM"
            if current_date:
                data_list.append([
                    pd.to_datetime(f"{current_date} {row[0]}", format="%d/%m/%Y %H:%M"),
                    row[1],  # PrévisionJ-1
                    row[2],  # PrévisionJ
                    row[3]   # Consommation
                ])

    # Création du DataFrame
    df_clean = pd.DataFrame(data_list, columns=["date", "prevision_j-", "prevision_j", "consommation"])
    
    return df_clean

# Chargement des fichiers Excel
conso_2023 = load_data("conso_mix_RTE_2023.xlsx")
conso_2024 = load_data("conso_mix_RTE_2024.xlsx")
conso_2025 = load_data("conso_mix_RTE_2025.xlsx")

# Concaténation des données
df = pd.concat([conso_2023, conso_2024, conso_2025])

df = df.sort_values("date")  # Tri par date

# Initialisation de l'application Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Visualisation des données de consommation RTE"),
    
    dcc.DatePickerRange(
        id='date-picker',
        min_date_allowed=df['date'].min(),
        max_date_allowed=df['date'].max(),
        start_date=df['date'].min(),
        end_date=df['date'].max()
    ),
    
    dcc.Graph(id='time-series-graph')
])

@app.callback(
    Output('time-series-graph', 'figure'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date')
)
def update_graph(start_date, end_date):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    fig = px.line(filtered_df, x='date', y='consommation', title="Consommation Électrique RTE")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


