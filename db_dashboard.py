import streamlit as st
from pymongo import MongoClient
import plotly.graph_objs as go

clientDB = MongoClient("mongodb://localhost:27017/")
backupDB = clientDB["Messungen"]

def db_dashboard():

    container_DB = st.container()
    container_DB.empty()

    with container_DB:


        # Prüfen, welche Messungen bereits existieren, und die nächste Nummer bestimmen
        existing_collections = backupDB.list_collection_names()
        
        st.title("Monitoring-System der Fakultät für Digitale Transformation")   
        st.header("Datenbank-Dashboard")

        option = st.selectbox(
            "Wähle eine Messung aus!", (existing_collections)
        )

        st.write("Du hast: ", option)

        collection = backupDB[option]
        
        doc = collection.find_one()

        field_names = list(doc.keys())
        field_names.remove('_id')
        field_names.remove('time')

        # Layout für die Charts
        cols = st.columns(2)
        chart_containers = {}

        # Create empty containers for each field to store charts
        for idx, field in enumerate(field_names):
            col_idx = idx % 2  # Alternate columns
            with cols[col_idx]:
                #st.subheader(field)
                chart_containers[field] = st.empty()
        

        all_data = list(collection.find({}, {"_id": 0}))


        if all_data:
            # Daten in separate Listen für Streamlit umwandeln
            times = [record['time'] for record in all_data]
            data_dict = {field: [record[field] for record in all_data] for field in field_names}

            # Daten in Streamlit anzeigen
            for field, values in data_dict.items():
                # Plotly chart erstellen
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=times, y=values, mode='lines+markers', name=field))
                fig.update_layout(title=f"{field} über die Zeit", xaxis_title="Zeit", yaxis_title=field)
                chart_containers[field].plotly_chart(fig)
