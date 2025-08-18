import http.server
import socketserver
import os
import sys
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.webroot = webroot
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        # Use pathlib to build the full path relative to webroot
        safe_path = Path(path).resolve()
        fullpath = (self.webroot / safe_path.relative_to(safe_path.anchor)).resolve()
        # Check blocklist
        for b in blocked:
            abs_blocked_path = (self.webroot / b).resolve()
            if str(fullpath).startswith(str(abs_blocked_path)):
                return str((self.webroot / "error.html").resolve())
        return str(fullpath)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        settings_file = sys.argv[1]
    else:
        settings_file = 'settings.json'
    settings_file = (Path(__file__).parent / settings_file).resolve()
    with open(settings_file, mode="r") as f:
        settings = json.load(f)

    webroot = (Path(__file__).parent / settings["webroot"]).resolve()
    blocked = settings["blocklist"]
    port = int(settings.get("port", 8000))
    
    server = ThreadingHTTPServer(('', port), Handler)
    server.serve_forever()
