import http.server
import socketserver
import os
import time
import threading

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)

clients = []
lock = threading.Lock()

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/__livereload__':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            with lock:
                clients.append(self.wfile)
            try:
                while True:
                    time.sleep(30)
                    self.wfile.write(b': keepalive\n\n')
                    self.wfile.flush()
            except:
                pass
            finally:
                with lock:
                    clients.remove(self.wfile)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass

def watcher():
    last = os.path.getmtime(os.path.join(DIR, 'index.html'))
    while True:
        time.sleep(1)
        try:
            mtime = os.path.getmtime(os.path.join(DIR, 'index.html'))
            if mtime != last:
                last = mtime
                with lock:
                    for w in clients[:]:
                        try:
                            w.write(b'data: reload\n\n')
                            w.flush()
                        except:
                            clients.remove(w)
        except:
            pass

t = threading.Thread(target=watcher, daemon=True)
t.start()

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'Live at http://localhost:{PORT}')
    httpd.serve_forever()
