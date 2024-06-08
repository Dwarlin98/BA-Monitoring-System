import streamlit as st


# Seiten-Funktionen importieren
from rt_dashboard import rt_dashboard
from db_dashboard import db_dashboard

# Konfiguration der Seite
st.set_page_config(layout="wide")


# Seitenleiste für die Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Gehe zu", ["Hauptseite", "Messungen", "Andere Seite"])

content = st.container()

content.empty()

# Seite anzeigen basierend auf der Auswahl in der Seitenleiste

with content:
    if page == "Hauptseite":
        st.title("Willkommen auf der Hauptseite")
        st.write("Hier können Sie allgemeine Informationen anzeigen oder Aktionen durchführen.")
    elif page == "Messungen":
        rt_dashboard()
    elif page == "Andere Seite":
        db_dashboard()
