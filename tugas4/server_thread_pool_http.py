from socket import *
import socket
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = b""
    try:
        # LANGKAH 1: Baca sampai \r\n\r\n (header lengkap)
        while b"\r\n\r\n" not in rcv:
            data = connection.recv(1024)
            if not data:
                break
            rcv += data

        if b"\r\n\r\n" not in rcv:
            connection.close()
            return

        # Pisahkan header dan body
        header_raw, body = rcv.split(b"\r\n\r\n", 1)
        headers_text = header_raw.decode()
        headers_lines = headers_text.split("\r\n")

        # LANGKAH 2: Ambil Content-Length jika ada
        content_length = 0
        for line in headers_lines:
            if line.lower().startswith("content-length:"):
                try:
                    content_length = int(line.split(":")[1].strip())
                except:
                    content_length = 0

        # LANGKAH 3: Baca sisa body sampai lengkap
        while len(body) < content_length:
            data = connection.recv(1024)
            if not data:
                break
            body += data

        # Gabungkan ulang full request
        full_request = header_raw + b"\r\n\r\n" + body

        # LANGKAH 4: Proses & kirim respons
        hasil = httpserver.proses(full_request.decode(errors='ignore'))
        connection.sendall(hasil + b"\r\n\r\n")

    except Exception as e:
        print("ERROR:", e)
    finally:
        connection.close()

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8885))
    my_socket.listen(1)

    with ThreadPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)
            jumlah = ['x' for i in the_clients if i.running() == True]
            print(f"Aktif: {len(jumlah)}")

def main():
    Server()

if __name__ == "__main__":
    main()
