import streamlit as st
import yaml
import subprocess
import threading
import queue
import time
import os
import signal

# Seiten-Funktionen importieren
from rt_dashboard import rt_dashboard
from db_dashboard import db_dashboard

# Konfigurationsdatei laden
def load_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

def save_config(config):
    with open("config.yaml", "w") as file:
        yaml.dump(config, file)

config = load_config()

# Konfiguration der Seite
st.set_page_config(layout="wide")

st.html("""
  <style>
    [alt=Logo] {
      height: 3rem;
    }
  </style>
""")

# Seitenleiste für die Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Gehe zu", ["Konfigurationsseite", "Live-Dashboard", "Datenbank-Dashboard"])
st.logo("HTWK.png")

def main():
    content = st.container()
    content.empty()

    with content:
        st.title("Monitoring-System der Fakultät für Digitale Transformation")

        col1, col2 = st.columns([0.9,0.1])

        with col1:
            st.header("Konfigurationsseite")
        
        with col2:
            if st.button("Streamlit beenden", type="primary", help="über diesen Button wird die Streamlit Anwendung beendet ohne dabei den Capturer zu beenden"):
                stop_streamlit()
        
        st.header(" ")

        st.header("Konfiguration der Spaltennamen")
        field_names = st.text_area(label=" ", value="\n".join(config["field_names"]), 
                                   height=300, help="In dieser Box können die Namen für die einzelnen Spalten festgelegt werden. Jede einzelne Spaltenbezeichnung wird auf eine eigene Zeile geschrieben")
        if st.button("Spaltennamen speichern"):
            config["field_names"] = field_names.split("\n")
            save_config(config)
            st.success("Spaltennamen gespeichert und konfiguriert")

        st.header("Konfiguration des Terminal-Capturer Patterns")
        pattern = st.text_area(label=" ", value="\n".join(config["pattern"]), 
                               help="Hier wird das Pattern für den Terminal Capturer festgelegt")
        if st.button("Pattern speichern"):
            config["pattern"] = pattern.split("\n")
            save_config(config)
            st.success("Pattern gespeichert")

        st.header(" ")
        st.header("SRS-RAN Capturer starten")
        script_running = st.empty()  # Placeholder for script running status

        if st.button("Script starten"):
            start_script(script_running)  # Passing placeholders

        st.header(" ")

        

def start_script(output_placeholder):
    output_placeholder.text("Das Script wurde gestartet das die Graphen werden im Live-Dashboard angezeigt.")
    subprocess.Popen(['python', 'terminal_capturer.py'])


def stop_streamlit():
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)
    os.kill(pid, signal.SIGTERM)

if page == "Konfigurationsseite":
    main()
elif page == "Live-Dashboard":
    rt_dashboard()
elif page == "Datenbank-Dashboard":
    db_dashboard()