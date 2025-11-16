# backend/analytics.py
class Analytics:
    def __init__(self, data_path=None, students=None, courses=None, fees=None):
        pass

    def overview(self):
        return {"students": 0, "courses": 0, "avgGpa": 0, "passRate": 0}

    def top_performers(self, limit=10):
        return []

    def course_averages(self):
        return {"labels": [], "values": []}
