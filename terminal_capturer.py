import subprocess
import sys
import re
import streamlit

import json
import socket

# Host und Port definieren
HOST = '127.0.0.1'  # localhost
PORT = 65432        # Port, den der Server verwendet


def run_docker_compose():
    # Terminalbefehl als Liste von Strings definieren
    command = ["docker", "compose", "-f", "srsenb_zmq.yaml", "up", "-d"]

    # Befehl ausführen und Output abfangen
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        print("Docker Compose gestartet und Output gespeichert.")
    except subprocess.CalledProcessError as e:
        # Fehlerbehandlung, falls der Befehl fehlschlägt
        print("Fehler beim Ausführen des Docker-Compose-Befehls:")
        print(e.output.decode())  # Fehlermeldung ausgeben

def attach_to_container(redirect_output=True, output_file="container_output.txt", pattern=None):
    # Terminalbefehl als Liste von Strings definieren
    command = ["docker", "container", "attach", "srsenb_zmq"]

    # Befehl ausführen und Output zeilenweise lesen
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            with open(output_file, "w") as f:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
                for line in iter(process.stdout.readline, ""):
                    if pattern:
                        if re.search(pattern, line):
                            if redirect_output:
                                    line = line.replace("|", "")
                                    data_list = line.split()
                                    data_list = [item.strip() for item in data_list]
                                    #sys.stdout.write(line)  # Output im Terminal anzeigen
                                    sys.stdout.write(str(data_list))  # Output im Terminal anzeigen
                                    sys.stdout.flush()
                                    data_to_send = data_list
                                    json_data = json.dumps(data_to_send)
                                    client_socket.sendall(json_data.encode())
                                    print(f'Datenpaket gesendet')
                            f.write(line)  # Output in Datei schreiben
                    else:
                        if redirect_output:
                            sys.stdout.write(line)  # Output im Terminal anzeigen
                            sys.stdout.flush()
                        f.write(line)  # Output in Datei schreiben
    except KeyboardInterrupt:
        print("Abbruch: Docker-Container-Anhängen wurde unterbrochen.")

if __name__ == "__main__":
    run_docker_compose()
    attach_to_container(redirect_output=True, output_file="container_output.txt", pattern = "^lte")



# Changes:
# MongoDB (not loose DATA)
# MongoDB or SQL