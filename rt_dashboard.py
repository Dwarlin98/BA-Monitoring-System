import streamlit as st
from datetime import datetime, timedelta
import socket
import json
from pymongo import MongoClient
import threading
import queue

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

# TBD es muss noch geändert werden das die daten die ganze Zeit geplotet werden irgendwie wird die Funktion add_row nichtmehr ausgeführt ...
# Ging jetzt aber muss beobachtet werden !!!

# Funktion für die Messungen-Seite
def rt_dashboard():
    
    # Definiere die Feldnamen entsprechend der ursprünglichen Spaltennamen
    field_names = ['rat', 'pci', 'rnti', 'DL_cqi', 'DL_ri', 'DL_mcs', 'DL_brate', 'DL_ok', 'DL_nok', 'DL_percent', 'UL_pusch', 'UL_pucch', 'UL_phr', 'UL_mcs', 'UL_brate', 'UL_ok', 'UL_nok', 'UL_percent', 'UL_bsr']

    st.image('HTWK.jpg', use_column_width=True)

    col1, col2 = st.columns(2)

    with col1:
        UL_brate = st.empty()
        DL_brate = st.empty()

    with col2:
        DL_ok = st.empty()
        UL_ok = st.empty()


    def add_row(data):
        current_time = datetime.now().strftime("%H:%M:%S")
        data_with_time = {"time": current_time}


        # Debugging-Ausgabe, um die empfangenen Daten zu überprüfen
        print(f"Empfangene Daten (entpackt): {data}")
        print(f"Anzahl empfangener Daten (entpackt): {len(data)}")
        print(f"Anzahl erwarteter Felder: {len(field_names)}")

        # Verwende zip, um Feldnamen und Daten zu kombinieren
        if len(data) == len(field_names):
            for field_name, value in zip(field_names, data):
                data_with_time[field_name] = value
        else:
            print("Daten und Feldnamen stimmen nicht überein")

        # Debugging-Ausgabe, um sicherzustellen, dass die Daten korrekt sind
        print(data_with_time)

        # Daten in die MongoDB einfügen
        collection.insert_one(data_with_time)


    def process_data():
        # Aktuelle Zeit und Zeit vor X Minuten bestimmen
        current_time = datetime.now()
        three_minutes_ago = current_time - timedelta(minutes=1)

        # Daten aus MongoDB lesen, die innerhalb der letzten 3 Minuten liegen
        all_data = list(collection.find({"time": {"$gte": three_minutes_ago.strftime("%H:%M:%S")}}, {"_id": 0}))

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

    # Socket erstellen und im Hintergrund laufen lassen
    if 'socket_started' not in st.session_state:
        st.session_state.socket_started = True

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
        

        threading.Thread(target=socket_thread, daemon=True).start()
        print('Socket-Thread gestartet')

    # Daten in regelmäßigen Abständen aktualisieren
    def update_data():
        while not data_queue.empty():
            data = data_queue.get()
            add_row(data)
        process_data()

    while True:
        update_data()

