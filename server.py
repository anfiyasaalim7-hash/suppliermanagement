import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from datetime import datetime

DATA_DIR = "data"

FILES = {
    "vendors": "vendors.json",
    "invoices": "invoices.json",
    "payments": "payments.json",
    "purchases": "purchases.json"
}


# ---------------- STORAGE ---------------- #

def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    for file in FILES.values():
        path = os.path.join(DATA_DIR, file)
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump([], f)


def load(name):
    with open(os.path.join(DATA_DIR, FILES[name]), "r") as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(DATA_DIR, FILES[name]), "w") as f:
        json.dump(data, f, indent=4)


def new_id(data):
    return max([d["id"] for d in data], default=0) + 1


# ---------------- SCORE CALCULATION ---------------- #

def calculate_score(vendor_id):
    invoices = load("invoices")
    payments = load("payments")

    total = 0
    paid = 0

    for inv in invoices:
        if inv["vendor_id"] == vendor_id:
            total += 1
            for pay in payments:
                if pay["invoice_id"] == inv["id"]:
                    paid += 1

    return round((paid / total) * 100, 2) if total > 0 else 0


# ---------------- HTTP SERVER ---------------- #

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/vendors":
            self.send_json(load("vendors"))

        elif self.path == "/invoices":
            self.send_json(load("invoices"))

        else:
            self.send_json({"message": "Backend Running"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        data = parse_qs(body)

        # CREATE VENDOR
        if self.path == "/vendor/create":
            vendors = load("vendors")

            vendor = {
                "id": new_id(vendors),
                "supplier_id": data.get("supplier_id", ["SUP001"])[0],
                "shop_name": data["shop_name"][0],
                "owner": data["owner"][0],
                "contact": data["contact"][0],
                "score": 0
            }

            vendors.append(vendor)
            save("vendors", vendors)

            self.send_json(vendor)

        # CREATE INVOICE
        elif self.path == "/invoice/create":
            invoices = load("invoices")

            invoice = {
                "id": new_id(invoices),
                "vendor_id": int(data["vendor_id"][0]),
                "amount": float(data["amount"][0]),
                "status": "PENDING",
                "date": str(datetime.now())
            }

            invoices.append(invoice)
            save("invoices", invoices)

            self.send_json(invoice)

        # PAY INVOICE
        elif self.path == "/payment/pay":
            invoice_id = int(data["invoice_id"][0])
            invoices = load("invoices")
            payments = load("payments")
            vendors = load("vendors")

            for inv in invoices:
                if inv["id"] == invoice_id:
                    inv["status"] = "PAID"

                    payment = {
                        "id": new_id(payments),
                        "invoice_id": invoice_id,
                        "paid_on": str(datetime.now())
                    }

                    payments.append(payment)

                    # update score
                    for v in vendors:
                        if v["id"] == inv["vendor_id"]:
                            v["score"] = calculate_score(v["id"])

                    save("invoices", invoices)
                    save("payments", payments)
                    save("vendors", vendors)

                    self.send_json({"message": "Payment Successful"})
                    return

            self.send_json({"error": "Invoice not found"})


# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":
    init_storage()
    server = HTTPServer(("localhost", 8000), Handler)
    print("Server running at http://localhost:8000")
    server.serve_forever()