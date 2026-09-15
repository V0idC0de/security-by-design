import os
import signal
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        recipient = os.environ.get("GREETED")
        self.wfile.write(f"Hello {recipient}!\n".encode())

signal.signal(signal.SIGTERM, lambda _1,_2: exit(1))

port = os.environ.get("PORT", 8000)
server = HTTPServer(
    ("0.0.0.0", int(port)),
    Handler
).serve_forever()
