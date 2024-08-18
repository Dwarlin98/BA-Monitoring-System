import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

# Verbindung zur MongoDB herstellen
client = MongoClient("mongodb://localhost:27017/")  # Ändern Sie dies auf Ihre MongoDB-URL
db = client["IhreDatenbank"]  # Ändern Sie dies auf Ihre Datenbank
collection = db["IhreSammlung"]  # Ändern Sie dies auf Ihre Sammlung

# Daten abrufen und in DataFrame konvertieren
data = pd.DataFrame(list(collection.find()))

# Optional: Überschrift (Spaltenname) anpassen
data.columns = [column_name.lower().replace(" ", "_") for column_name in data.columns]

# Streamlit Überschrift
st.title("MongoDB Daten Visualisierung")

# Spaltennamen für die Auswahl
columns = data.columns.tolist()

# Dropdown-Menü für Wert 1 (x-Achse)
x_value = st.selectbox("Wählen Sie die Spalte für Wert 1 (x-Achse) aus", columns)

# Dropdown-Menü für Wert 2 (y-Achse)
y_value = st.selectbox("Wählen Sie die Spalte für Wert 2 (y-Achse) aus", columns)

# Sicherstellen, dass unterschiedliche Spalten für x und y ausgewählt werden
if x_value != y_value:
    # Daten für das Plotting filtern
    filtered_data = data[[x_value, y_value]]

    # Plotly Graphen erstellen
    fig = px.line(filtered_data, x=x_value, y=y_value)
    st.plotly_chart(fig)
else:
    st.warning("Bitte wählen Sie unterschiedliche Spalten für Wert 1 und Wert 2 aus.")

# Optional: Rohdaten anzeigen
if st.checkbox("Rohdaten anzeigen"):
    st.write(data)
