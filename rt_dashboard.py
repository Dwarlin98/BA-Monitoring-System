import streamlit as st
from datetime import datetime, timedelta
import socket
import json
from pymongo import MongoClient
import threading
import queue
import time
import yaml

HOST = '127.0.0.1'  # localhost
PORT = 65432        # Port über 1023 wählen

# MongoDB-Verbindung herstellen
client = MongoClient("mongodb://localhost:27017/")
db = client["Messungen"]

# Prüfen, welche Messungen bereits existieren, und die nächste Nummer bestimmen
existing_collections = db.list_collection_names()
max_number = 0
for coll in existing_collections:
    if coll.startswith("Messung"):
        try:
            number = int(coll.replace("Messung", ""))
            if number > max_number:
                max_number = number
        except ValueError:
            continue

new_collection_name = f"Messung{max_number + 1}"
collection = db[new_collection_name]

data_queue = queue.Queue()

# Funktion für die Messungen-Seite
def rt_dashboard():

    st.title("Monitoring-System der Fakultät für Digitale Transformation")  
        #st.write("Hier können Sie allgemeine Informationen anzeigen oder Aktionen durchführen.")    

    st.header("Live-Dashboard")

    # Konfigurationsdatei laden
    def load_config():
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
        return config

    config = load_config()
    field_names = config["field_names"]
    

    col1, col2 = st.columns(2)

    with col1:
        ul_brate_chart = st.empty()
        dl_brate_chart = st.empty()

    with col2:
        dl_ok_chart = st.empty()
        ul_ok_chart = st.empty()

    def add_row(data):
        current_time = datetime.now().strftime("%H:%M:%S")
        data_with_time = {"time": current_time}

        # Verwende zip, um Feldnamen und Daten zu kombinieren
        if len(data) == len(field_names):
            for field_name, value in zip(field_names, data):
                data_with_time[field_name] = value
        else:
            print("Daten und Feldnamen stimmen nicht überein")

        # Daten in die MongoDB einfügen
        collection.insert_one(data_with_time)

    # Socket erstellen und im Hintergrund laufen lassen
    def socket_thread():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print('Server wartet auf Verbindung...')
            connection, address = server_socket.accept()
            with connection:
                print('Verbunden mit:', address)
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    decoded_data = json.loads(data.decode())
                    print(f"Decodierte Daten: {decoded_data}")
                    data_queue.put(decoded_data)

    def data_processor_thread():
        while True:
            while not data_queue.empty():
                data = data_queue.get()
                add_row(data)
            time.sleep(1)

    if 'threads_started' not in st.session_state:
        st.session_state.threads_started = True
        threading.Thread(target=socket_thread, daemon=True).start()
        threading.Thread(target=data_processor_thread, daemon=True).start()

    def process_data():
        # Aktuelle Zeit und Zeit vor 1 Minute bestimmen
        current_time = datetime.now()
        one_minute_ago = current_time - timedelta(minutes=1)

        # Daten aus MongoDB lesen, die innerhalb der letzten Minute liegen
        all_data = list(collection.find({"time": {"$gte": one_minute_ago.strftime("%H:%M:%S")}}, {"_id": 0}))

        if all_data:
            # Daten in separate Listen für Streamlit umwandeln
            times = [record['time'] for record in all_data]
            ul_brate_values = [record['UL_brate'] for record in all_data]
            dl_brate_values = [record['DL_brate'] for record in all_data]
            ul_ok_values = [record['UL_ok'] for record in all_data]
            dl_ok_values = [record['DL_ok'] for record in all_data]

            # Daten in Streamlit anzeigen
            ul_brate_chart.line_chart({"time": times, "UL_brate": ul_brate_values}, x = 'time', y = 'UL_brate')
            dl_brate_chart.line_chart({"time": times, "DL_brate": dl_brate_values}, x = 'time', y = 'DL_brate')
            ul_ok_chart.line_chart({"time": times, "UL_ok": ul_ok_values}, x = 'time', y = 'UL_ok')
            dl_ok_chart.line_chart({"time": times, "DL_ok": dl_ok_values}, x = 'time', y = 'DL_ok')

    while True:
        process_data()
        time.sleep(1)

