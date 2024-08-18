import streamlit as st
from pymongo import MongoClient
import plotly.graph_objs as go

clientDB = MongoClient("mongodb://admin:admin@localhost:27018/")


def db_dashboard():

    backupDB = clientDB["Messungen-Quelle-1"]
    backupDB2 = clientDB["Messungen-Quelle-2"]

    container_DB = st.container()
    container_DB.empty()

    def modeCheck(dataType):
            if dataType == 'time':
                return('lines+markers')
            else:
                return('markers')

    with container_DB:

        # Prüfen, welche Messungen bereits existieren
        existing_collections = backupDB.list_collection_names()
        existing_collections2 = backupDB2.list_collection_names()

        existing_collections.extend(x for x in existing_collections2 if x not in existing_collections)
        existing_collections_sorted=sorted(existing_collections)
        
        st.title("Monitoring-System der Fakultät für Digitale Transformation")   
        st.header("Datenbank-Dashboard")

        option = st.selectbox(
            "Wähle eine Messung aus!", (existing_collections_sorted)
        )

        st.write("Es wurde ", option, " gewählt")
        st.divider()

        collection = backupDB[option]
        
        doc = collection.find_one()

        field_names = list(doc.keys())
        field_names.remove('_id')
        #field_names.remove('time')

        field_names_wo_time = field_names
        field_names_wo_time.remove('time')

        # Layout für die Charts
        cols = st.columns(2)
        
        all_data = list(collection.find({}, {"_id": 0}))
        columns = list(all_data[0].keys())  # Annahme: Alle Diktate haben dieselben Keys

        with cols[0]:
            st.subheader("Quelle 1")
            st.divider()

        with cols[1]:
            st.subheader("Quelle 2")
            st.divider()
        
        

        # Erstellen der leeren Container und hinzufügen von Dropdown-Menüs
        for idx, field in enumerate(field_names_wo_time):
            
            with cols[0]:  # Container in der entsprechenden Spalte platzieren
                st.subheader(f"Chart für {field}")

                # Zwei Dropdown-Menüs innerhalb des Containers hinzufügen
                col1, col2 = st.columns(2)
                with col1:
                    x_value = st.selectbox(
                        f"Wählen Sie die x-Achse für {field} aus", 
                        columns, 
                        index=columns.index('time') if 'time' in columns else 0,  # Standardmäßig 'time' auswählen
                        key=f"x_{field}"
                    )
                with col2:
                    y_value = st.selectbox(
                        f"Wählen Sie die y-Achse für {field} aus", 
                        columns, 
                        index=columns.index(field) if field in columns else 0,  # Standardmäßig das jeweilige Feld auswählen
                        key=f"y_{field}"
                    )

                # Sicherstellen, dass unterschiedliche Spalten für x und y ausgewählt werden
                if x_value != y_value:
                    # Daten für das Plotting filtern
                    x_data = [doc[x_value] for doc in all_data if x_value in doc]
                    y_data = [doc[y_value] for doc in all_data if y_value in doc]

                    # Plotly Graphen erstellen
                    fig = go.Figure(data=go.Scatter(x=x_data, y=y_data, mode = modeCheck(x_value)))
                    fig.update_layout(
                                      xaxis_title=x_value,
                                      yaxis_title=y_value)
                    st.plotly_chart(fig)
                else:
                    st.warning(f"Bitte wählen Sie unterschiedliche Spalten für x und y für {field} aus.")
                
        
        #############################################################


        collection2 = backupDB2[option]
        
        doc2 = collection2.find_one()

        field_names2 = list(doc2.keys())
        field_names2.remove('_id')
        #field_names.remove('time')

        field_names_wo_time2 = field_names2
        field_names_wo_time2.remove('time')
        
        all_data2 = list(collection2.find({}, {"_id": 0}))
        columns2 = list(all_data2[0].keys())  # Annahme: Alle Diktate haben dieselben Keys
        
        st.divider()

        for idx, field2 in enumerate(field_names_wo_time2):
            with cols[1]:  # Container in der entsprechenden Spalte platzieren
                st.subheader(f"Chart für {field2}")

                # Zwei Dropdown-Menüs innerhalb des Containers hinzufügen
                col1, col2 = st.columns(2)
                with col1:
                    x_value2 = st.selectbox(
                        f"Wählen Sie die x-Achse für {field2} aus", 
                        columns2, 
                        index = columns2.index('time') if 'time' in columns2 else 0,  # Standardmäßig 'time' auswählen
                        key=f"x2_{field2}"
                    )
                with col2:
                    y_value2 = st.selectbox(
                        f"Wählen Sie die y-Achse für {field2} aus", 
                        columns2, 
                        index=columns2.index(field2) if field2 in columns2 else 0,  # Standardmäßig das jeweilige Feld auswählen
                        key=f"y2_{field2}"
                    )

                # Sicherstellen, dass unterschiedliche Spalten für x und y ausgewählt werden
                if x_value2 != y_value2:
                    # Daten für das Plotting filtern
                    x_data2 = [doc2[x_value2] for doc2 in all_data2 if x_value2 in doc2]
                    y_data2 = [doc2[y_value2] for doc2 in all_data2 if y_value2 in doc2]

                    # Plotly Graphen erstellen
                    fig2 = go.Figure(data=go.Scatter(x=x_data2, y=y_data2, mode = modeCheck(x_value)))
                    fig2.update_layout(
                                      xaxis_title=x_value2,
                                      yaxis_title=y_value2)
                    st.plotly_chart(fig2)
                else:
                    st.warning(f"Bitte wählen Sie unterschiedliche Spalten für x und y für {field2} aus.")