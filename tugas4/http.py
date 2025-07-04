import os
import base64
from datetime import datetime

class HttpServer:
    def __init__(self):
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }

    def response(self, code=200, message='OK', body=b'', headers={}):
        tanggal = datetime.now().strftime('%c')
        if not isinstance(body, bytes):
            body = body.encode()

        response_lines = [
            f"HTTP/1.0 {code} {message}",
            f"Date: {tanggal}",
            "Connection: close",
            "Server: myserver/1.0",
            f"Content-Length: {len(body)}"
        ] + [f"{k}:{v}" for k, v in headers.items()] + ["", ""]
        response = '\r\n'.join(response_lines).encode() + body
        return response

    def proses(self, data):
        try:
            # AMBIL header + body
            if "\r\n\r\n" not in data:
                return self.response(400, 'Bad Request', 'Malformed request')
            header_data, body_data = data.split("\r\n\r\n", 1)

            lines = header_data.split("\r\n")
            request_line = lines[0]
            method, path, _ = request_line.split()

            if method.upper() == 'GET':
                return self.http_get(path)
            elif method.upper() == 'POST':
                return self.http_post(path, body_data)
            elif method.upper() == 'DELETE':
                return self.http_delete(path)
            else:
                return self.response(405, 'Method Not Allowed')
        except Exception as e:
            return self.response(500, 'Internal Server Error', str(e))

    def http_get(self, path):
        if path == '/list':
            files = os.listdir('.')
            filelist = [f for f in files if os.path.isfile(f) and not f.endswith('.py')]
            return self.response(200, 'OK', '\n'.join(filelist))


        filename = path.lstrip('/')
        if not os.path.exists(filename):
            return self.response(404, 'Not Found', 'File not found')
        with open(filename, 'rb') as f:
            content = f.read()
        ext = os.path.splitext(filename)[1]
        return self.response(200, 'OK', content, {
            'Content-Type': self.types.get(ext, 'application/octet-stream')
        })

    def http_post(self, path, body):
        if path != '/upload':
            return self.response(404, 'Not Found')

        try:
            if "\r\n" not in body:
                return self.response(400, 'Bad Request', 'Missing filename or body')
            filename, encoded = body.split("\r\n", 1)
            filename = filename.strip()
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(encoded))
            return self.response(200, 'OK', f"{filename} uploaded.")
        except Exception as e:
            return self.response(400, 'Bad Request', str(e))

    def http_delete(self, path):
        filename = path.lstrip('/')
        if not os.path.exists(filename):
            return self.response(404, 'Not Found', 'File not found')
        os.remove(filename)
        return self.response(200, 'OK', f"{filename} deleted.")
