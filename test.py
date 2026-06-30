import requests

requests.post(
    "http://localhost:8000/api/admin/update-expiry",
    json={
        "password": "sudev@2026",
        "expiry_date": "2027-01-01"
    }
)
print("done")
