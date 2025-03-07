import os
import sqlite3
import pandas as pd
import statsmodels.api as sm
from fastapi import FastAPI, UploadFile, File
import dash
from dash import dcc, html
import plotly.express as px
import uvicorn
import requests
from io import BytesIO

# FastAPI Backend
app = FastAPI()
DB_FILE = "forecast.db"
FILES = ["conso_mix_RTE_2023.xls", "conso_mix_RTE_2024.xls", "conso_mix_RTE_2025.xls"]

# Database Initialization
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        value REAL
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        predicted_value REAL
    )""")
    conn.commit()
    conn.close()
init_db()

# Load XLS Data
def load_xls_to_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for file in FILES:
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            cursor.execute("INSERT INTO data (date, value) VALUES (?, ?)", (row["date"], row["value"]))
    conn.commit()
    conn.close()
load_xls_to_db()

# Fetch Data
@app.get("/get-data")
def get_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM data", conn)
    conn.close()
    return df.to_dict(orient="records")

# Forecast API
@app.get("/forecast")
def forecast():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM data", conn)
    conn.close()
    
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    model = sm.tsa.AutoReg(df["value"], lags=3).fit()
    preds = model.predict(start=len(df), end=len(df)+10)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for i, val in enumerate(preds):
        cursor.execute("INSERT INTO forecasts (date, predicted_value) VALUES (?, ?)", (df.index[-1] + pd.Timedelta(days=i+1), val))
    conn.commit()
    conn.close()
    return {"forecast": preds.to_list()}

# Dash Frontend
dash_app = dash.Dash(__name__)
response = requests.get("http://127.0.0.1:8000/get-data")
data = pd.DataFrame(response.json())
fig = px.line(data, x='date', y='value', title='Consommation Historique')

dash_app.layout = html.Div([
    dcc.Graph(figure=fig),
    html.Button("Prédire", id="predict-btn", n_clicks=0)
])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    dash_app.run_server(debug=True)
