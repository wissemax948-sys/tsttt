from flask import Flask, request, Response, jsonify
import requests
import uuid

app = Flask(__name__)

# ⚠️ Clé IntelX privée, ne jamais exposer
API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"
FORCE_DOWNLOAD = False

@app.route('/fetch', methods=['GET'])
def fetch_data():
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

        if 'application/json' in response.headers.get("Content-Type", ""):
            return jsonify({"error": "API returned JSON", "details": response.text}), 500

        # Envoi direct du fichier au client sans sauvegarder sur le serveur
        return Response(
            response.iter_content(chunk_size=8192),
            content_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except requests.exceptions.HTTPError as errh:
        return jsonify({"error": f"HTTP Error {response.status_code}", "details": str(errh)}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection Error — check your internet"}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request Timeout — the server is taking too long to respond"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "General Request Failure", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
