# backend/app.py
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from students import StudentRegistry
from courses import CourseScheduler
from fees import FeeTracker
from library import LibrarySystem
from analytics import Analytics

DATA_DIR = Path(__file__).parent / "data"

# Initialize modules with JSON data
students = StudentRegistry(DATA_DIR / "students.json")
courses = CourseScheduler(DATA_DIR / "courses.json")
fees = FeeTracker(DATA_DIR / "fees.json")
library = LibrarySystem(DATA_DIR / "library.json")
analytics = Analytics(DATA_DIR / "performance.json", students, courses, fees)

def parse_body(length, rfile, content_type):
    raw = rfile.read(length) if length else b""
    if not raw:
        return {}
    if content_type.startswith("application/x-www-form-urlencoded"):
        return {k: v[0] for k, v in urllib.parse.parse_qs(raw.decode()).items()}
    if content_type.startswith("application/json"):
        return json.loads(raw.decode())
    return {}

class Handler(BaseHTTPRequestHandler):
    def _json(self, payload, status=200):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _html(self, html, status=200):
        data = html.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        # API JSON endpoints
        if path == "/api/students":
            q = query.get("q", [""])[0]
            return self._json(students.search(q))
        if path.startswith("/api/students/"):
            sid = path.split("/")[-1]
            found = students.get(sid)
            return self._json(found if found else {"error": "not_found"}, 200 if found else 404)

        if path == "/api/courses":
            return self._json(courses.list_courses())
        if path == "/api/enrollments":
            code = query.get("courseCode", [""])[0]
            return self._json(courses.peek_queue(code))

        if path == "/api/fees":
            sid = query.get("studentId", [""])[0]
            return self._json(fees.list_payments(sid))
        if path.startswith("/api/fees/clearance/"):
            sid = path.split("/")[-1]
            return self._json({"studentId": sid, "cleared": fees.is_cleared(sid)})

        if path == "/api/library":
            q = query.get("q", [""])[0]
            return self._json(library.search(q))

        if path == "/api/analytics/overview":
            return self._json(analytics.overview())
        if path == "/api/analytics/top":
            limit = int(query.get("limit", ["10"])[0])
            return self._json(analytics.top_performers(limit))
        if path == "/api/analytics/graph":
            return self._json(analytics.course_averages())

        # Serve static frontend
        root = Path(__file__).parent.parent / "frontend"
        file_map = {
            "/": "index.html",
            "/students": "students.html",
            "/courses": "courses.html",
            "/fees": "fees.html",
            "/library": "library.html",
            "/analytics": "analytics.html",
        }
        if path in file_map:
            html = (root / file_map[path]).read_text(encoding="utf-8")
            return self._html(html)
        if path.startswith("/css/"):
            css_path = root / path[1:]
            if css_path.exists():
                data = css_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/css")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                return self.wfile.write(data)

        return self._json({"error": "not_found"}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        ctype = self.headers.get("Content-Type", "")
        body = parse_body(length, self.rfile, ctype)

        if path == "/api/students":
            ok, msg = students.add(body.get("id"), body.get("name"), body.get("program"), body.get("year"))
            return self._json({"ok": ok, "message": msg}, 200 if ok else 400)
        if path.startswith("/api/students/remove/"):
            sid = path.split("/")[-1]
            ok = students.remove(sid)
            return self._json({"ok": ok}, 200 if ok else 404)

        if path == "/api/courses":
            ok, msg = courses.create_course(body.get("code"), body.get("title"), int(body.get("capacity", 0)))
            return self._json({"ok": ok, "message": msg}, 200 if ok else 400)
        if path == "/api/enrollments":
            ok, status = courses.enqueue_enrollment(body.get("courseCode"), body.get("studentId"))
            return self._json({"ok": ok, "status": status}, 200 if ok else 400)
        if path == "/api/enrollments/allocate":
            ok, info = courses.allocate_next(body.get("courseCode"))
            return self._json({"ok": ok, "info": info}, 200 if ok else 400)

        if path == "/api/fees/pay":
            ok, rec = fees.record_payment(body.get("studentId"), float(body.get("amount", 0)))
            return self._json({"ok": ok, "record": rec}, 200 if ok else 400)

        if path == "/api/library/borrow":
            ok, msg = library.borrow(body.get("isbn"), body.get("studentId"))
            return self._json({"ok": ok, "message": msg}, 200 if ok else 400)
        if path == "/api/library/return":
            ok, msg = library.return_book(body.get("isbn"), body.get("studentId"))
            return self._json({"ok": ok, "message": msg}, 200 if ok else 400)

        return self._json({"error": "not_found"}, 404)

def run(host="0.0.0.0", port=8000):
    server = HTTPServer((host, port), Handler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run()
