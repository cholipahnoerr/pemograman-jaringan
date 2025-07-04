from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

#untuk menggunakan processpoolexecutor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def ProcessTheClient(connection, address):
    rcv = b""
    try:
        # 1. Baca hingga header lengkap (ada \r\n\r\n)
        while b"\r\n\r\n" not in rcv:
            data = connection.recv(1024)
            if not data:
                break
            rcv += data

        if b"\r\n\r\n" not in rcv:
            connection.close()
            return

        # 2. Pisahkan header dan body
        header_raw, body = rcv.split(b"\r\n\r\n", 1)
        headers_text = header_raw.decode()
        headers_lines = headers_text.split("\r\n")

        # 3. Ambil Content-Length
        content_length = 0
        for line in headers_lines:
            if line.lower().startswith("content-length:"):
                try:
                    content_length = int(line.split(":")[1].strip())
                except:
                    content_length = 0

        # 4. Baca body hingga sesuai Content-Length
        while len(body) < content_length:
            data = connection.recv(1024)
            if not data:
                break
            body += data

        # 5. Gabungkan ulang dan proses
        full_request = header_raw + b"\r\n\r\n" + body
        hasil = httpserver.proses(full_request.decode(errors='ignore'))
        connection.sendall(hasil)

        time.sleep(0.1)  # beri waktu supaya data terkirim
        connection.shutdown(socket.SHUT_WR)
      
    except Exception as e:
        print("ERROR:", e)
    finally:
        connection.close()

def Server():
	the_clients = []
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	my_socket.bind(('0.0.0.0', 8889))
	my_socket.listen(1)

	with ProcessPoolExecutor(20) as executor:
		while True:
				connection, client_address = my_socket.accept()
				#logging.warning("connection from {}".format(client_address))
				p = executor.submit(ProcessTheClient, connection, client_address)
				the_clients.append(p)
				#menampilkan jumlah process yang sedang aktif
				jumlah = ['x' for i in the_clients if i.running()==True]
				print(jumlah)
      
def main():
	Server()

if __name__=="__main__":
	main()

