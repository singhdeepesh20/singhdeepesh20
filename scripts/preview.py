"""Open the generated SVG cards in a local static preview."""
from __future__ import annotations

import http.server
import socketserver
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with ReusableServer(("127.0.0.1", 8000), http.server.SimpleHTTPRequestHandler) as server:
        import os
        os.chdir(ROOT)
        url = "http://127.0.0.1:8000/preview/"
        print(f"Preview: {url}  (Ctrl+C to stop)")
        webbrowser.open(url)
        server.serve_forever()
