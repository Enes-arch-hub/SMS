# backend/students.py
class StudentRegistry:
    def __init__(self, data_path=None):
        self.students = {}

    def add(self, sid, name, program, year):
        self.students[sid] = {"id": sid, "name": name, "program": program, "year": year}
        return True, "added"

    def get(self, sid):
        return self.students.get(sid)

    def search(self, q):
        return [s for s in self.students.values() if q.lower() in s["name"].lower() or q.lower() in s["id"].lower()]

    def remove(self, sid):
        return self.students.pop(sid, None) is not None
