import subprocess
import sys
import re
import json
import socket
import yaml
import threading

# Host und Port definieren
HOST = '127.0.0.1'  # localhost
PORT = 65432        # Port, den der Server verwendet

HOST2 = '127.0.0.1'  # localhost
PORT2 = 65423        # Port, den der Server verwendet


def attach_to_container(redirect_output=True, pattern=None):
    command = ["docker", "container", "attach", "srsenb_zmq"]
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
            for line in iter(process.stdout.readline, ""):
                if pattern:
                    if re.search(pattern, line):
                        if redirect_output:
                            line = line.replace("|", "")
                            data_list = line.split()
                            data_list = [item.strip() for item in data_list]
                            sys.stdout.write(str(data_list))
                            sys.stdout.flush()
                            data_to_send = data_list
                            json_data = json.dumps(data_to_send)
                            client_socket.sendall(json_data.encode())
                            print(f'Datenpaket gesendet')
                else:
                    if redirect_output:
                        sys.stdout.write(line)
                        sys.stdout.flush()
    except KeyboardInterrupt:
        print("Abbruch: Docker-Container-Anhängen wurde unterbrochen.")


def attach_to_container2(redirect_output=True, pattern=None):
    command2 = ["docker", "container", "attach", "srsue_zmq"]
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket2:
            client_socket2.connect((HOST2, PORT2))
            process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
            for line in iter(process2.stdout.readline, ""):
                if pattern:
                    if re.search(pattern, line):
                        if redirect_output:
                            print("Ausgabe wird umgeleitet")
                            line = line.replace("|", "")
                            data_list2 = line.split()
                            data_list2 = [item.strip() for item in data_list2]
                            sys.stdout.write(str(data_list2))
                            sys.stdout.flush()
                            data_to_send = data_list2
                            json_data = json.dumps(data_to_send)
                            client_socket2.sendall(json_data.encode())
                            print(f'Datenpaket gesendet')
                else:
                    if redirect_output:
                        sys.stdout.write(line)
                        sys.stdout.flush()
    except KeyboardInterrupt:
        print("Abbruch: Docker-Container-Anhängen wurde unterbrochen.")


def read_pattern_from_yaml(file_path):
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
            pattern_list = config.get('pattern', [])
            if pattern_list:
                return pattern_list[0]
            print(f"Pattern nicht in der Datei {file_path} gefunden.")
            return None
    except FileNotFoundError:
        print(f"Datei {file_path} nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return None


def read_pattern_from_yaml2(file_path):
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
            pattern_list = config.get('pattern2', [])
            if pattern_list:
                return pattern_list[0]
            print(f"Pattern nicht in der Datei {file_path} gefunden.")
            return None
    except FileNotFoundError:
        print(f"Datei {file_path} nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return None


if __name__ == "__main__":
    pattern = read_pattern_from_yaml("config.yaml")
    pattern2 = read_pattern_from_yaml2("config.yaml")

    # Threads für paralleles Ausführen der Funktionen
    thread1 = threading.Thread(target=attach_to_container, args=(True, pattern))
    thread2 = threading.Thread(target=attach_to_container2, args=(True, pattern2))

    # Threads starten
    thread1.start()
    thread2.start()

    # Warten, bis beide Threads beendet sind
    thread1.join()
    thread2.join()
