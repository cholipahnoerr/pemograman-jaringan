import socket
import base64

SERVER_ADDRESS = ('localhost', 8889)

def send_raw(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(SERVER_ADDRESS)
        s.sendall(request.encode())
        response = b""
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            response += chunk
        print("[DEBUG] Raw response bytes length:", len(response))
        print(response.decode(errors="ignore"))

def list_files():
    request = "GET /list HTTP/1.0\r\n\r\n"
    send_raw(request)

def upload_file(local_path, remote_filename):
    with open(local_path, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    body = f"{remote_filename}\r\n{encoded}"
    request = f"POST /upload HTTP/1.0\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    send_raw(request)

def delete_file(filename):
    request = f"DELETE /{filename} HTTP/1.0\r\n\r\n"
    send_raw(request)

if __name__ == '__main__':
    # print("\n=== LIST FILES ===")
    # list_files()

    # print("\n=== UPLOAD FILE ===")
    # upload_file('testing.txt', 'testing1.txt')

    # print("\n=== LIST FILES AFTER UPLOAD ===")
    # list_files()

    print("\n=== DELETE FILE ===")
    delete_file('testing1.txt')

    print("\n=== LIST FILES AFTER DELETE ===")
    list_files()
