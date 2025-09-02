import requests
import uuid
import os
from vercel_python_runtime import VercelResponse  # helper Vercel serverless

API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"
MY_API_KEY = "test"
RESULTS_DIR = "/tmp/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def handler(request):
    user_key = request.args.get("user_key")
    storageid = request.args.get("storageid")
    bucket = request.args.get("bucket", "leaks.logs")
    download = request.args.get("download", "false").lower() == "true"

    if user_key != MY_API_KEY:
        return VercelResponse({"error": "Invalid API key"}, status=403)

    params = {
        "apikey": API_KEY,
        "storageid": storageid,
        "bucket": bucket,
        "download": str(download).lower()
    }

    try:
        r = requests.get(API_URL, params=params, stream=True, timeout=20)
        r.raise_for_status()

        unique_id = uuid.uuid4().hex[:8]
        filename = f"{storageid[:10]}_{bucket}_{unique_id}.txt"
        filepath = os.path.join(RESULTS_DIR, filename)

        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        with open(filepath, "rb") as f:
            return VercelResponse(
                f.read(),
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "text/plain"
                }
            )

    except requests.exceptions.RequestException as e:
        return VercelResponse({"error": str(e)}, status=500)
