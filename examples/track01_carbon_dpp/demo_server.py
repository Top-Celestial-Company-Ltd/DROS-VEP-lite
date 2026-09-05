"""
DROS-VEP-lite | Track 01 Demo Server (Carbon DPP Data Flow Control)
Run this script to launch the local HTTP server for interactive Demo showcase.
"""
import http.server
import socketserver
import webbrowser
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    print(f"==========================================================")
    print(f"🛡️ DROS-VEP-lite Track 01 Demo Server Running!")
    print(f"🔗 URL: http://localhost:{PORT}/index.html")
    print(f"==========================================================")
    
    # Try opening browser automatically
    try:
        webbrowser.open(f"http://localhost:{PORT}/index.html")
    except Exception as e:
        print(f"Note: Please open http://localhost:{PORT}/index.html manually in your browser.")
        
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
