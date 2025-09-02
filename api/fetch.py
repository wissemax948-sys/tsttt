from flask import Flask, request, jsonify, send_file
import requests
import uuid
import os

app = Flask(__name__)

# ⚠️ Clé OSINT privée
API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"
FORCE_DOWNLOAD = False

# Clé API pour ton propre service Flask
MY_API_KEY = "TEST"  # ⚠️ À changer et garder secrète 

@app.route('/fetch', methods=['GET'])
def fetch_data():
    # Vérification de la clé API pour sécuriser l'accès
    client_key = request.headers.get('X-API-KEY')
    if client_key != MY_API_KEY:
        return jsonify({"error": "Unauthorized — invalid API key"}), 401

    storage_id = request.args.get('storageid')
    bucket = request.args.get('bucket')

    if not storage_id or not bucket:
        return jsonify({"error": "Missing required parameters"}), 400

    params = {
        "apikey": API_KEY,
        "storageid": storage_id,
        "bucket": bucket,
        "download": str(FORCE_DOWNLOAD).lower()
    }

    unique_id = uuid.uuid4().hex[:8]
    filename = f"{storage_id[:10]}_{bucket}_{unique_id}.txt"

    try:
        response = requests.get(API_URL, params=params, stream=True, timeout=20)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if 'application/json' in content_type:
            return jsonify({"error": "API returned an error"}), 500
        else:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return send_file(filename, as_attachment=True)

    except requests.exceptions.HTTPError:
        return jsonify({"error": "HTTP Error occurred"}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection Error"}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request Timeout"}), 500
    except requests.exceptions.RequestException:
        return jsonify({"error": "Request Failed"}), 500
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
