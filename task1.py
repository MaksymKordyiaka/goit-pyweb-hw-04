from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import socket
import multiprocessing
from datetime import datetime
import json
import urllib.parse

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/index.html']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/message.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('message.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('style.css', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/logo.png':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open('logo.png', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('error.html', 'rb') as f:
                self.wfile.write(f.read())

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            username = parsed_data.get('username', [''])[0]
            message = parsed_data.get('message', [''])[0]
            if username and message:
                timestamp = str(datetime.now())
                data = {timestamp: {'username': username, 'message': message}}
                with open('storage/data.json', 'a') as f:
                    json.dump(data, f, indent=2)
                    f.write('\n')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Bad request')

def http_server():
    httpd = ThreadingHTTPServer(('localhost', 3000), SimpleHTTPRequestHandler)
    print('HTTP server started...')
    httpd.serve_forever()

def socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('localhost', 5001))
        print('Socket server started...')
        while True:
            data, addr = s.recvfrom(1024)
            parsed_data = json.loads(data.decode('utf-8'))
            timestamp = str(datetime.now())
            with open('storage/data.json', 'a') as f:
                json.dump({timestamp: parsed_data}, f, indent=2)
                f.write('\n')
            print('Received data:', parsed_data)

if __name__ == '__main__':
    http_process = multiprocessing.Process(target=http_server)
    socket_process = multiprocessing.Process(target=socket_server)
    http_process.start()
    socket_process.start()
