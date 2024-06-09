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


# Seitenleiste für die Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Gehe zu", ["Hauptseite", "Messungen", "Andere Seite"])


def main():
    content = st.container()
    content.empty()
    
    with content:   
        st.title("Willkommen auf der Hauptseite")   
        st.write("Hier können Sie allgemeine Informationen anzeigen oder Aktionen durchführen.")    
        
        st.header("Konfiguration der Feldnamen")
        field_names = st.text_area("Field Names", value="\n".join(config["field_names"]))
        if st.button("Save Configuration"):
            config["field_names"] = field_names.split("\n")
            save_config(config)
            st.success("Konfiguration gespeichert")

if page == "Hauptseite":
    main()
elif page == "Messungen":
    rt_dashboard()
elif page == "Andere Seite":
    db_dashboard()

if __name__ == main:
    main()