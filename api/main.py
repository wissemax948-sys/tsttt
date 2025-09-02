from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

# ⚠️ Clé IntelX privée
API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"
FORCE_DOWNLOAD = False

@app.route('/fetch', methods=['GET'])
def fetch_data():
    # Récupération des paramètres depuis la requête
    storage_id = request.args.get('storageid')
    bucket = request.args.get('bucket')

    if not storage_id or not bucket:
        return jsonify({"error": "Missing required parameters"}), 400

    params = {
        "apikey": API_KEY,  # ⚠️ reste côté serveur, jamais exposé
        "storageid": storage_id,
        "bucket": bucket,
        "download": str(FORCE_DOWNLOAD).lower()
    }

    try:
        # Appel à IntelX
        response = requests.get(API_URL, params=params, stream=True, timeout=20)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")

        if 'application/json' in content_type:
            # Erreur renvoyée par IntelX
            return jsonify({"error": "IntelX API returned an error"}), 500

        # Renvoi direct du flux au client
        return Response(
            response.iter_content(chunk_size=8192),
            content_type='application/octet-stream'
        )

    except requests.exceptions.HTTPError:
        return jsonify({"error": "HTTP Error occurred"}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection Error"}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request Timeout"}), 500
    except requests.exceptions.RequestException:
        return jsonify({"error": "Request Failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
