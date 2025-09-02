from flask import Flask, request, Response, jsonify
import cloudscraper

app = Flask(__name__)

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

    try:
        scraper = cloudscraper.create_scraper()  # 🌐 gère Cloudflare
        response = scraper.get(API_URL, params=params, stream=True, timeout=20)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if 'application/json' in content_type:
            return jsonify({"error": "IntelX API returned an error"}), 500

        return Response(response.iter_content(chunk_size=8192),
                        content_type='application/octet-stream')

    except Exception as e:
        return jsonify({"error": "Request Failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
