import socket
import os
import mimetypes
import json
from datetime import datetime


class TCPServer:
    def __init__(self, host='127.0.0.1', port=8887):
        self.host = host
        self.port = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)

        print("Listening at", s.getsockname())

        while True:
            conn, addr = s.accept()
            print("Connected by", addr)
            data = conn.recv(1024)

            response = self.handle_request(data)

            conn.sendall(response)
            conn.close()

    def handle_request(self, data):
        return data

class HttpRequest:
    def __init__(self, data):
        self.metod = None
        self.uri = None
        self.http_version ='1.1'
        self.headers = {}
        self.parse(data)

    def parse(self,data):
        lines = bytes.decode(data).split('\r\n')
        request_line = lines[0]
        self.parse_request_line(request_line)
        if self.metod == 'POST':
            self.data = json.loads(lines[-1])

    def parse_request_line(self, request_line):
        words = request_line.split(' ')
        self.metod = words[0]
        self.uri = words[1]
        if len(words) > 2:
            self.http_version = words[2]

class HTTPServer(TCPServer):
    headers = {
        'Server': 'Track_Time',
        'Content-Type': 'text/html',
    }
    status_codes = {
        404: 'Not Found',
        200: ' OK',
    }


    def response_line(self, status_code):
        """Returns response line"""
        reason = self.status_codes[status_code]
        return "HTTP/1.1 %s %s\r\n" % (status_code, reason)

    def response_headers(self, extra_headers=None):
        """Returns headers
        The `extra_headers` can be a dict for sending
        extra headers for the current response
        """
        headers_copy = self.headers.copy()  # make a local copy of headers

        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ""

        for h in self.headers:
            headers += "%s: %s\r\n" % (h, self.headers[h])
        return headers

    def handle_request(self, request):
        request = HttpRequest(request)
        handler = getattr(self, 'handle_%s' % request.metod)
        response = handler(request)
        return response

    def handle_GET(self, request):
        def return_names(x):
            with open(x, "r") as jsonFile:
                data_json = json.load(jsonFile)

            return str(data_json)


        response_line = self.response_line(status_code=200)


        response_headers = self.response_headers()

        blank_line = "\r\n"

        response_body = f"""
            <html>
                <body>{return_names('track.json')}</body>
            </html>
        """
        response = response_line + response_headers + blank_line + response_body
        response_as_bytes = str.encode(response)
        return response_as_bytes

    def handle_POST(self, request):
        dict = request.data
        track_name = dict.get('name')
        driver = dict.get('driver')
        car = dict.get('car')
        lap_time = dict.get('time')
        if isinstance(track_name, str) and isinstance(driver, str) and isinstance(car, str) and isinstance(lap_time, (float, int)):
            with open("track.json", "r") as jsonFile:
                data_json = json.load(jsonFile)
            for i in data_json:
                if i['name'] == track_name:
                    del dict['name']
                    i['data'].append(dict)
                    break
            with open("track.json", "w") as jsonFile:
                json.dump(data_json, jsonFile)
        else:
            pass

if __name__ == '__main__':
    server = HTTPServer()
    server.start()
