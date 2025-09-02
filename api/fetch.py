from flask import Flask, request, send_file
import requests
import uuid
import os

app = Flask(__name__)
RESULTS_DIR = "/tmp/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"
MY_API_KEY = "test"

@app.route("/api/fetch")
def fetch():
    user_key = request.args.get("user_key")
    storageid = request.args.get("storageid")
    bucket = request.args.get("bucket", "leaks.logs")
    download = request.args.get("download", "false").lower() == "true"

    if user_key != MY_API_KEY:
        return {"error": "Invalid API key"}, 403

    params = {
        "apikey": API_KEY,
        "storageid": storageid,
        "bucket": bucket,
        "download": str(download).lower()
    }

    try:
        r = requests.get(API_URL, params=params, stream=True, timeout=20)
        r.raise_for_status()

        filename = f"{storageid[:10]}_{bucket}_{uuid.uuid4().hex[:8]}.txt"
        filepath = os.path.join(RESULTS_DIR, filename)
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return send_file(filepath, mimetype="text/plain", as_attachment=True, download_name=filename)

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500
