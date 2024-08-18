import streamlit as st
import yaml
import subprocess
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
        st.divider()
        col11, col12 = st.columns([0.5,0.5])
        col3, col6 = st.columns([0.5,0.5])
        st.divider()
        col9, col10 = st.columns([0.5,0.5])
        col4, col5 = st.columns([0.5,0.5])
        st.divider()
        col7, col8 = st.columns([0.5,0.5])
        
        with col3:
            st.header("Command Quelle 1")
            st.text_area(label=" ", key="ta01",value="\n".join(config["field_names"]), 
                                    height=70, help="In dieser Box können die Namen für die einzelnen Spalten festgelegt werden. Jede einzelne Spaltenbezeichnung wird auf eine eigene Zeile geschrieben")
        
        with col6:
            st.header("Command Quelle 2")
            st.text_area(label=" ", key="ta02",value="\n".join(config["field_names"]), 
                                    height=70, help="In dieser Box können die Namen für die einzelnen Spalten festgelegt werden. Jede einzelne Spaltenbezeichnung wird auf eine eigene Zeile geschrieben")

        with col1:
            st.header("Konfigurationsseite")
        
        with col11:
            st.header("Konfiguration der Befehle")
                    
        with col2:
            if st.button("Streamlit beenden", type="primary", help="über diesen Button wird die Streamlit Anwendung beendet ohne dabei den Capturer zu beenden"):
                stop_streamlit()
        
        with col4:
            st.subheader("Quelle 1")
            field_names = st.text_area(label=" ", value="\n".join(config["field_names"]), 
                                    height=300, help="In dieser Box können die Namen für die einzelnen Spalten festgelegt werden. Jede einzelne Spaltenbezeichnung wird auf eine eigene Zeile geschrieben")
            if st.button("Spaltennamen speichern"):
                config["field_names"] = field_names.split("\n")
                save_config(config)
                st.success("Spaltennamen gespeichert und konfiguriert")
            st.header("Konfiguration des Terminal-Capturer Patterns")
        
        with col9:
            st.header("Konfiguration der Spaltennamen")

        with col5:
            st.subheader("Quelle 2")
            field_names2 = st.text_area(label=" ", value="\n".join(config["field_names2"]), 
                                    height=300, help="In dieser Box können die Namen für die einzelnen Spalten festgelegt werden. Jede einzelne Spaltenbezeichnung wird auf eine eigene Zeile geschrieben")
            if st.button("Spaltennamen 2 speichern"):
                config["field_names2"] = field_names2.split("\n")
                save_config(config)
                st.success("Spaltennamen 2 gespeichert und konfiguriert")
        
        with col7:
            st.subheader("Quelle 1")
            pattern = st.text_area(label=" ", value="\n".join(config["pattern"]), 
                                help="Hier wird das Pattern für den Terminal Capturer festgelegt")
            if st.button("Pattern speichern"):
                config["pattern"] = pattern.split("\n")
                save_config(config)
                st.success("Pattern gespeichert")
            
        with col8:
            st.subheader("Quelle 2")
            pattern2 = st.text_area(label=" ", value="\n".join(config["pattern2"]), 
                                help="Hier wird das Pattern für den Terminal Capturer festgelegt", key="pattern2TA")
            if st.button("Pattern 2 speichern"):
                config["pattern2"] = pattern2.split("\n")
                save_config(config)
                st.success("Pattern 2 gespeichert")

        st.header(" ")
        st.header("SRS-RAN Capturer starten")
        script_running = st.empty()  

        if st.button("Script starten"):
            start_script(script_running)  

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