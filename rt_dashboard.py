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

HOST2 = '127.0.0.1'  # localhost
PORT2 = 65423        # Port über 1023 wählen

# MongoDB-Verbindung herstellen
client = MongoClient("mongodb://admin:admin@localhost:27018/")
db = client["Messungen-Quelle-1"]
db2 = client["Messungen-Quelle-2"]

# Funktion zur Ermittlung der größten vorhandenen Collection-Nummer in beiden Datenbanken
def get_max_collection_number(existing_collections):
    max_number = 0
    for coll in existing_collections:
        if coll.startswith("Messung-"):
            try:
                # Entferne 'Messung-' und das Datum aus dem Namen, um nur die Nummer zu erhalten
                number_str = coll.replace("Messung-", "").split("-")[0].strip()
                number = int(number_str)
                if number > max_number:
                    max_number = number
            except ValueError:
                continue
    return max_number

# Listen der vorhandenen Collections für beide Datenbanken
existing_collections_Source_01 = db.list_collection_names()
existing_collections_Source_02 = db2.list_collection_names()

# Ermittlung der größten Collection-Nummer in beiden Datenbanken
max_number_source_01 = get_max_collection_number(existing_collections_Source_01)
max_number_source_02 = get_max_collection_number(existing_collections_Source_02)

# Datum im Format YYYYMMDD
current_date = datetime.now().strftime("%Y%m%d")

# Festlegung des neuen Collection-Namens als den höchsten Wert aus beiden Datenbanken plus 1 und dem aktuellen Datum
new_collection_number = max(max_number_source_01, max_number_source_02) + 1
new_collection_name = f"Messung-{new_collection_number}-{current_date}"

# Verwendung des neuen Collection-Namens für beide Datenbanken
collection = db[new_collection_name]
collection2 = db2[new_collection_name]

data_queue = queue.Queue()
data_queue2 = queue.Queue()

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
    field_names2 = config["field_names2"]

    # Dictionaries für die Speicherung der Dropdown-Auswahlen und Checkbox-Zustände
    selected_fields = {}
    selected_fields2 = {}
    checkboxes = {}
    checkboxes02 = {}

    with st.expander("Graphen für Quellen deaktivieren und konfigurieren"):
        cols_expander = st.columns(2)
        
        # Linke Spalte für Quelle 1
        with cols_expander[0]:
            st.subheader("Quelle 1")
            for field in field_names:
                checkboxes[field] = st.checkbox(field, value=True)
                # Entferne das aktuelle Feld aus der Dropdown-Auswahl
                available_fields = ["None"] + [f for f in field_names if f != field]
                selected_fields[field] = st.selectbox(f"Zusätzliches Feld für {field}", available_fields, index=0)

                # Deaktiviere die Checkbox für das ausgewählte zusätzliche Feld
                if selected_fields[field] != "None":
                    checkboxes[selected_fields[field]] = False
        
        # Rechte Spalte für Quelle 2
        with cols_expander[1]:
            st.subheader("Quelle 2")
            for field in field_names2:
                checkboxes02[field] = st.checkbox(field, value=True, key=field)
                # Entferne das aktuelle Feld aus der Dropdown-Auswahl
                available_fields2 = ["None"] + [f for f in field_names2 if f != field]
                selected_fields2[field] = st.selectbox(f"Zusätzliches Feld für {field}", available_fields2, index=0, key=f"drop_{field}")

                # Deaktiviere die Checkbox für das ausgewählte zusätzliche Feld
                if selected_fields2[field] != "None":
                    checkboxes02[selected_fields2[field]] = False

    # Layout für die Graphen
    cols = st.columns(2)
    chart_containers = {}

    with cols[0]:
        st.subheader("Quelle 1")
    with cols[1]:
        st.subheader("Quelle 2")

    for idx, field in enumerate(field_names):
        with cols[0]:
            chart_containers[field] = st.empty()
    
    for idx2, field2 in enumerate(field_names2):
        with cols[1]:
            chart_containers[field2] = st.empty()

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

    def add_row(data, collectionIndex, fieldNames):
        current_time = datetime.now().strftime("%H:%M:%S")
        data_with_time = {"time": current_time}

        if len(data) == len(fieldNames):
            for field_name, value in zip(fieldNames, data):
                processed_value = process_value(value)
                data_with_time[field_name] = processed_value
        else:
            print("Daten und Feldnamen stimmen nicht überein")

        if collectionIndex == 1:
            collection.insert_one(data_with_time)
        else:
            collection2.insert_one(data_with_time)

    # Sockets erstellen und im Hintergrund laufen lassen
    def socket_thread():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print('Server für Quelle 01 wartet auf Verbindung...')
            connection, address = server_socket.accept()
            with connection:
                print('Mit Quelle 01 verbunden über:', address)
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    decoded_data = json.loads(data.decode())
                    print(f"Decodierte Daten: {decoded_data}")
                    data_queue.put(decoded_data)

    def socket_thread02():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket2:
            server_socket2.bind((HOST2, PORT2))
            server_socket2.listen()
            print('Server für Quelle 02 wartet auf Verbindung...')
            connection2, address2 = server_socket2.accept()
            with connection2:
                print('Mit Quelle 02 verbunden über:', address2)
                while True:
                    data2 = connection2.recv(1024)
                    if not data2:
                        break
                    decoded_data2 = json.loads(data2.decode())
                    print(f"Decodierte Daten Quelle 02: {decoded_data2}")
                    data_queue2.put(decoded_data2)

    def data_processor_thread():
        while True:
            while not data_queue.empty():
                data = data_queue.get()
                add_row(data, 1, field_names)
            time.sleep(1)

    def data_processor_thread2():
        while True:
            while not data_queue2.empty():
                data2 = data_queue2.get()
                add_row(data2, 2, field_names2)
            time.sleep(1)

    if 'threads_started' not in st.session_state:
        st.session_state.threads_started = True
        # Threads für beide Quellen starten
        threading.Thread(target=socket_thread, daemon=True).start()
        threading.Thread(target=socket_thread02, daemon=True).start()
        threading.Thread(target=data_processor_thread, daemon=True).start()
        threading.Thread(target=data_processor_thread2, daemon=True).start()

    def process_data():
        # Aktuelle Zeit und Zeit vor 1 Minute bestimmen
        current_time = datetime.now()
        one_minute_ago = current_time - timedelta(minutes=1)

        all_data = list(collection.find({"time": {"$gte": one_minute_ago.strftime("%H:%M:%S")}}, {"_id": 0}))

        if all_data:
            times = [record['time'] for record in all_data]
            data_dict = {field: [record[field] for record in all_data] for field in field_names}

            for field, values in data_dict.items():
                if checkboxes[field]:
                    chart_data = {"time": times, field: values}
                    additional_field = selected_fields[field]
                    if additional_field != "None":
                        additional_values = data_dict[additional_field]
                        chart_data[additional_field] = additional_values
                    chart_containers[field].line_chart(chart_data, x='time', y=[field, additional_field] if additional_field != "None" else field, height=300)

    def process_data2():
        current_time = datetime.now()
        one_minute_ago = current_time - timedelta(minutes=1)

        all_data2 = list(collection2.find({"time": {"$gte": one_minute_ago.strftime("%H:%M:%S")}}, {"_id": 0}))

        if all_data2:
            times2 = [record2['time'] for record2 in all_data2]
            data_dict2 = {field2: [record2[field2] for record2 in all_data2] for field2 in field_names2}

            for field2, values2 in data_dict2.items():
                if checkboxes02[field2]:
                    chart_data2 = {"time": times2, field2: values2}
                    additional_field2 = selected_fields2[field2]
                    if additional_field2 != "None":
                        additional_values2 = data_dict2[additional_field2]
                        chart_data2[additional_field2] = additional_values2
                    chart_containers[field2].line_chart(chart_data2, x='time', y=[field2, additional_field2] if additional_field2 != "None" else field2, height=300)

    while True:
        process_data()
        process_data2()