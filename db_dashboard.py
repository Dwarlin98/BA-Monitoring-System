import streamlit as st
from pymongo import MongoClient

clientDB = MongoClient("mongodb://localhost:27017/")
backupDB = clientDB["Messungen"]

def db_dashboard():

    container_DB = st.container()
    container_DB.empty()

    with container_DB:

        

        # Prüfen, welche Messungen bereits existieren, und die nächste Nummer bestimmen
        existing_collections = backupDB.list_collection_names()
        
        st.title("Andere Seite")
        st.write("Dies ist die andere Seite, die noch ausformuliert werden muss.")

        option = st.selectbox(
            "Wähle eine Messung aus!", (existing_collections)
        )
            
        st.write("Du hast: ", option)
        
        st.image('HTWK.jpg', use_column_width=True)

        col1, col2 = st.columns(2)

        with col1:
            UL_brate = st.empty()
            DL_brate = st.empty()

        with col2:
            DL_ok = st.empty()
            UL_ok = st.empty()

        collection = backupDB[option]

        all_data = list(collection.find({}, {"_id": 0}))

        # Daten in separate Listen für Streamlit umwandeln
        times = [record['time'] for record in all_data]
        UL_brate_values = [record['UL_brate'] for record in all_data]
        DL_brate_values = [record['DL_brate'] for record in all_data]
        UL_ok_values = [record['UL_ok'] for record in all_data]
        DL_ok_values = [record['DL_ok'] for record in all_data]

        # Daten in Streamlit anzeigen
        with UL_brate.container():
            st.header("UL_brate")
            st.line_chart({'time': times, 'UL_brate': UL_brate_values}, x = 'time', y = 'UL_brate')
            st.header("DL_brate")
            st.line_chart({'time': times, 'DL_brate': DL_brate_values}, x = 'time', y = 'DL_brate')

        with DL_ok.container():
            st.header("UL_ok")
            st.line_chart({'time': times, 'UL_ok': UL_ok_values}, x = 'time', y = 'UL_ok')
            st.header("DL_ok")
            st.line_chart({'time': times, 'DL_ok': DL_ok_values}, x = 'time', y = 'DL_ok')

