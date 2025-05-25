import socket
import json
import base64
import logging
import os

server_address = ('127.0.0.1', 5555)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"Connecting to {server_address}")
    try:
        sock.sendall(command_str.encode())
        data_received = ""
        while True:
            data = sock.recv(4096)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = json.loads(data_received.strip())
        logging.warning("Data received from server:")
        return hasil
    except Exception as e:
        logging.warning("Error receiving data")
        return dict(status="ERROR", data=str(e))

def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print("Daftar file:")
        for f in hasil['data']:
            print("-", f)
    else:
        print("Gagal LIST")

def remote_get(filename):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        with open(hasil['data_namafile'], 'wb') as f:
            f.write(base64.b64decode(hasil['data_file']))
        print(f"File {filename} berhasil diunduh")
    else:
        print("Gagal GET")

def remote_upload(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        b64data = base64.b64encode(data).decode()
        filename = os.path.basename(filepath)
        command_str = f"UPLOAD {filename} {b64data}"
        hasil = send_command(command_str)
        print("UPLOAD:", hasil)
    except Exception as e:
        print("UPLOAD ERROR:", str(e))

def remote_delete(filename):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    print("DELETE:", hasil)

if __name__ == '__main__':
    remote_list()
    remote_upload("donalbebek.jpg")
    remote_list()
    remote_get("donalbebek.jpg")
    remote_delete("donalbebek.jpg")
    remote_list()
