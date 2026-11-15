from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from SQLite_class import SQLite


db = SQLite("mystore.db")
is_vulnerable = False

class LoginHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/login":
            self.send_response(404)
            self.end_headers()
            return
        # Read the request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()
        data = json.loads(body)

        username = data.get("username")
        password = data.get("password")
        if is_vulnerable:
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            result = db.execute_query(query)
        else:
            query = "SELECT * FROM users WHERE username=? AND password=?"
            args = (username,password)
            result = db.execute_query(query, args)
        if result and len(result) > 0:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Login Success")
        else:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Login failed")

if __name__ == "__main__":
    is_vulnerable = input("Enter yes if you want the server to be vulnerable to SQL injection: ") == "yes"

    # Start http server
    port = 8080
    httpd = HTTPServer(("", port), LoginHandler)
    print(f"Serving on http://localhost:{port}")
    httpd.serve_forever()
