from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
import requests
import uuid
import os

app = FastAPI()

# 🔑 Clés privées (ne jamais exposer publiquement)
API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"  # clé OSINT cachée

# 🚪 Clé API de ton proxy (fournie aux utilisateurs)
MY_API_KEY = "Q9wYH0N0rLh8eKJ4tWZ7d3Xgq2Oa5pRf8Ty1VuLm9SjCxBkDnMhEzGiKoPtUrXy"

# 📂 Dossier où stocker les résultats
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.get("/fetch")
def fetch_data(
    user_key: str = Query(...), 
    storageid: str = Query(...), 
    bucket: str = Query("leaks.logs"), 
    download: bool = Query(False)
):
    # Vérifier la clé utilisateur
    if user_key != MY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    params = {
        "apikey": API_KEY,   # clé OSINT cachée
        "storageid": storageid,
        "bucket": bucket,
        "download": str(download).lower()
    }

    try:
        r = requests.get(API_URL, params=params, stream=True, timeout=20)
        r.raise_for_status()

        # Si c’est une erreur (JSON), on renvoie directement
        if "application/json" in r.headers.get("Content-Type", ""):
            return r.json()

        # Générer un nom unique de fichier
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{storageid[:10]}_{bucket}_{unique_id}.txt"
        filepath = os.path.join(RESULTS_DIR, filename)

        # Écrire le contenu dans un fichier
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Retourner le fichier en téléchargement
        return FileResponse(
            filepath,
            media_type="text/plain",
            filename=filename
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
