# backend/courses.py
class CourseScheduler:
    def __init__(self, data_path=None):
        self.courses = {}

    def list_courses(self):
        return []

    def create_course(self, code, title, capacity):
        return True, "created"

    def enqueue_enrollment(self, course_code, student_id):
        return True, "queued"

    def allocate_next(self, course_code):
        return True, {"course": course_code, "studentId": "dummy"}
