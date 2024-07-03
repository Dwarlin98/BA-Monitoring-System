import streamlit as st
from datetime import datetime, timedelta
import socket
import json
from pymongo import MongoClient
import threading
import queue
import time
import yaml
import ast


HOST = '127.0.0.1'  # localhost
PORT = 65432        # Port über 1023 wählen

# MongoDB-Verbindung herstellen
client = MongoClient("mongodb://admin:admin@localhost:27018/")
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

def rt_dashboard():

    st.title("Monitoring-System der Fakultät für Digitale Transformation")  

    st.header("Live-Dashboard")

    # Konfigurationsdatei laden
    def load_config():
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
        return config

    config = load_config()
    field_names = config["field_names"]

    with st.expander("Graphen deaktivieren"):
        # Checkboxen für die Auswahl der Graphen
        checkboxes = {field: st.checkbox(field, value=True) for field in field_names}

    # Layout für die Graphen
    cols = st.columns(2)
    chart_containers = {}

    # Leere Container für jedes Feld um die Container anzuzeigen
    for idx, field in enumerate(field_names):
        col_idx = idx % 2 
        with cols[col_idx]:
            st.subheader(field)
            chart_containers[field] = st.empty()


    def process_value(value):
        if value.endswith("k"):
            return int(float(value[:-1]) * 1000)
        elif value.endswith("M"):
            return int(float(value[:-1]) * 1000000)
        else:
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return value


    def add_row(data):
        current_time = datetime.now().strftime("%H:%M:%S")
        data_with_time = {"time": current_time}

        # Verwende zip, um Feldnamen und Daten zu kombinieren
        if len(data) == len(field_names):
            for field_name, value in zip(field_names, data):
                # Verarbeite den Wert entsprechend
                processed_value = process_value(value)
                data_with_time[field_name] = processed_value

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
            data_dict = {field: [record[field] for record in all_data] for field in field_names}

            # Daten in Streamlit anzeigen
            for field, values in data_dict.items():
                if checkboxes[field]:
                    chart_containers[field].line_chart({"time": times, field: values}, x='time', y=field)

    while True:
        process_data()
        time.sleep(1)