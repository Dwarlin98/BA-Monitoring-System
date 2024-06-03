import numpy as np
import pandas as pd

import streamlit as st


from datetime import datetime
import socket
import json

HOST = '127.0.0.1'  # localhost
PORT = 65432        # Port über 1023 wählen

st.set_page_config(layout="wide")


st.image('HTWK.jpg', use_column_width=True)


col1, col2 = st.columns(2)

with col1:
    UL_brate = st.empty()
    DL_brate = st.empty()


with col2:
    DL_ok = st.empty()
    UL_ok = st.empty()


chart_data = pd.DataFrame(columns = ['rat', 'pci', 'rnti', 'DL_cqi', 'DL_ri', 'DL_mcs', 'DL_brate', 'DL_ok', 'DL_nok', 'DL_percent', 'UL_pusch', 'UL_pucch', 'UL_phr', 'UL_mcs', 'UL_brate', 'UL_ok', 'UL_nok', 'UL_percent', 'UL_bsr'])
chart_data.insert(0, 'time', datetime.now().strftime("%H:%M:%S"))

def add_row(data):
    # Füge eine Zeile zum DataFrame hinzu
    global chart_data
    newDF = pd.DataFrame(data, columns = ['rat', 'pci', 'rnti', 'DL_cqi', 'DL_ri', 'DL_mcs', 'DL_brate', 'DL_ok', 'DL_nok', 'DL_percent', 'UL_pusch', 'UL_pucch', 'UL_phr', 'UL_mcs', 'UL_brate', 'UL_ok', 'UL_nok', 'UL_percent', 'UL_bsr'])
    newDF.insert(0, 'time', datetime.now().strftime("%H:%M:%S"))
    chart_data = pd.concat([chart_data, newDF], axis=0, ignore_index=True)


def process_data(daten):
    # Datenverarbeitung
    add_row([daten])
    print(chart_data) 
 
    with UL_brate.container():
            st.header("UL_brate")
            st.line_chart(chart_data, x='time', y='UL_brate')
            st.header("DL_brate")
            st.line_chart(chart_data, x='time', y='DL_brate')

    with DL_ok.container():
            st.header("UL_ok")
            st.line_chart(chart_data, x='time', y='UL_ok')
            st.header("DL_ok")
            st.line_chart(chart_data, x='time', y='DL_ok')


# Socket erstellen
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Socket an Adresse und Port binden
    server_socket.bind((HOST, PORT))
    # Auf eingehende Verbindungen warten
    server_socket.listen()
    print('Server wartet auf Verbindung...')
    # Verbindung akzeptieren
    connection, address = server_socket.accept()
    with connection:
        print('Verbunden mit:', address)
        while True:
            # Daten empfangen
            data = connection.recv(1024)
            if not data:
                break
            # JSON-Daten decodieren
            decoded_data = json.loads(data.decode())
            # Daten verarbeiten
            process_data(decoded_data)
