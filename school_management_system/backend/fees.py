# backend/fees.py
class FeeTracker:
    def __init__(self, data_path=None):
        self.fees = []

    def record_payment(self, student_id, amount):
        return True, {"txnId": "TXN1", "studentId": student_id, "amount": amount}

    def list_payments(self, student_id=""):
        return self.fees

    def is_cleared(self, student_id):
        return False
