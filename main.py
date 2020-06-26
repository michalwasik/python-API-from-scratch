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
        self.data = None
        self.http_version ='1.1'
        self.headers = {}
        self.parse(data)

    def parse(self,data):
        lines = bytes.decode(data).split('\r\n')
        request_line = lines[0]
        self.parse_request_line(request_line)
        if self.metod == 'POST':
            self.data = dict(param.split('=') for param in lines[-1].split('&'))

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
        400: 'Bad Request',
        501: 'Not Implemented',
    }

    def send_response(self, response_line, response_headers, blank_line, response_body):
        response = f'{response_line}{response_headers}{blank_line}{response_body}'
        return str.encode(response)


    def response_line(self, status_code):
        """Returns response line"""
        reason = self.status_codes[status_code]
        return f"HTTP/1.1 {status_code} {reason}\r\n"

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
            headers += f"{h}: {self.headers[h]}\r\n"
        return headers

    def load_templates(self, file):
        return open(f'templates/{file}').read()

    def lines_format(self, data):
        lines = []
        for user in data:
            lines.append(
                f'<tr>'
                f'<td>{user["driver"]}</td>'
                f'<td>{user["car"]}</td>'
                f'<td>{user["time"]}</td>'
                f'<td>{user["added_time"]}</td>'
                f'</tr>'
            )
        return ''.join(lines)
    def handle_request(self, request):
        request = HttpRequest(request)
        if request.metod == "GET":
            response = self.handle_GET(request)
        elif request.metod == "POST":
            response = self.handle_POST(request)
        else:
            response = self.HTTP_501_handler(request)
        return response

    def HTTP_501_handler(self, request):
        response_line = self.response_line(status_code=501)
        response_headers = self.response_headers()
        blank_line = '\r\n'
        response_body = '<h1>501 Not Implemented</h1>'
        return self.send_response(response_line, response_headers, blank_line, response_body)


    def handle_GET(self, request):
        if str(request.uri) != '/':
            track_name = str(request.uri.split('/')[1])
            response_line = self.response_line(status_code=200)
            response_headers = self.response_headers()
            blank_line = "\r\n"
            requested_track ={}
            with open('track.json', "r") as jsonFile:
                for track in json.load(jsonFile):
                    if track['slug_name'].lower() == track_name.lower():
                        requested_track = track
                        break
                else:
                    response_body = self.load_templates('track_not_found.html')

            if 'data' in requested_track and requested_track['data'] != []:
                lines_string = self.lines_format(requested_track['data'])
                template = self.load_templates('track_laptime.html')
                track_site = template.format(
                    track_name=requested_track['name'],
                    lines=lines_string
                )

                response_body = track_site
            elif 'name' in requested_track:
                template = self.load_templates('empty_track.html')
                track_site = template.format(track_name=requested_track['name'])
                response_body = track_site
            return self.send_response(response_line, response_headers, blank_line, response_body)
        else:
            response_line = self.response_line(status_code=200)
            response_headers = self.response_headers()
            blank_line = "\r\n"
            with open('track.json', "r") as jsonFile:
                data_json = json.load(jsonFile)
            track_href = '<br>\n'.join(f'<a href = {i["slug_name"]}>{i["name"]}</a>' for i in data_json)
            response_body = f"""
            <html>
                <body>
                    <p>{track_href}</p>
                </body>
            </html>
                            """
            return self.send_response(response_line, response_headers, blank_line, response_body)

    def handle_POST(self, request):
        add_dict = request.data
        track_name = request.uri.split('/')[1]
        add_dict['added_time'] = datetime.now().__str__()

        if (
                isinstance(track_name, str) and
                isinstance(add_dict['driver'], str) and
                isinstance(add_dict['car'], str)
                #isinstance(add_dict['time'], (float, int))
            ):

            requested_data = {}
            requested_name = ''
            with open("track.json", "r") as jsonFile:
                data_json = json.load(jsonFile)
            for tracks in data_json:
                if tracks['slug_name'] == track_name:
                    tracks['data'].append(add_dict)
                    requested_data = tracks['data']
                    requested_name = tracks['name']
                    break

            with open("track.json", "w") as jsonFile:
                json.dump(data_json, jsonFile, indent=4)

            response_line = self.response_line(status_code=200)
            response_headers = self.response_headers()
            blank_line = "\r\n"
            lines_string = self.lines_format(requested_data)
            template = self.load_templates('track_laptime.html')
            track_site = template.format(
                track_name=requested_name,
                lines=lines_string
            )

            response_body = track_site
        else:
            response_line = self.response_line(status_code=400)
            response_headers = self.response_headers()
            blank_line = "\r\n"
            response_body = """
            <html>
                <body>400 Bad Request</body>
            </html>
            """
        return self.send_response(response_line, response_headers, blank_line, response_body)


if __name__ == '__main__':
    server = HTTPServer()
    server.start()