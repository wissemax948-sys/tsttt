from flask import Flask, request, Response, jsonify
import requests
import os

app = Flask(__name__)

# ⚠️ Clé IntelX privée (ne jamais exposer côté client)
API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"
FORCE_DOWNLOAD = False

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API IntelX Flask opérationnelle. Utilisez /fetch"}), 200

@app.route('/fetch', methods=['GET'])
def fetch_data():
    # Récupération des paramètres depuis la requête
    storage_id = request.args.get('storageid')
    bucket = request.args.get('bucket')

    if not storage_id or not bucket:
        return jsonify({"error": "Missing required parameters"}), 400

    params = {
        "apikey": API_KEY,  # ⚠️ reste côté serveur
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
            # IntelX renvoie une erreur JSON
            return jsonify({
                "error": "IntelX API returned an error",
                "response": response.json()
            }), 500

        # Renvoi direct du flux au client
        return Response(
            response.iter_content(chunk_size=8192),
            content_type='application/octet-stream'
        )

    except requests.exceptions.HTTPError as errh:
        return jsonify({
            "error": "HTTP Error occurred",
            "status_code": errh.response.status_code,
            "response_text": errh.response.text
        }), 500
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection Error — vérifie internet ou API IntelX"}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request Timeout — serveur IntelX trop long"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Request Failed", "details": str(e)}), 500


if __name__ == '__main__':
    # Serveur WSGI robuste pour production avec Waitress
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    serve(app, host="0.0.0.0", port=port)
