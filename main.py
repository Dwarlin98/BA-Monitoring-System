import streamlit as st
import yaml


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

        st.header("Konfigurationsseite")
        st.header(" ")

        st.header("Konfiguration der Spaltennamen")
        field_names = st.text_area(label=" ", value="\n".join(config["field_names"]), 
                                   height=300, help="In dieser Box können die Namen für die einzelnen Spalten festgelegt werden. Jede einzelene Spaltenbezeichnung wird auf eine eigene Zeile geschrieben")
        if st.button("Spaltennamen speichern"):
            config["field_names"] = field_names.split("\n")
            save_config(config)
            st.success("Spaltennamen gespeichert und konfiguriert")

if page == "Konfigurationsseite":
    main()
elif page == "Live-Dashboard":
    rt_dashboard()
elif page == "Datenbank-Dashboard":
    db_dashboard()

if __name__ == main:
    main()