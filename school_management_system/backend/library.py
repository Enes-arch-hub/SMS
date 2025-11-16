# backend/library.py
class LibrarySystem:
    def __init__(self, data_path=None):
        self.books = {}

    def search(self, q=""):
        return []

    def borrow(self, isbn, student_id):
        return True, "borrowed"

    def return_book(self, isbn, student_id):
        return True, "returned"
