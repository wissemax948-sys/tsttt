from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
import requests
import uuid
import os

app = FastAPI()

# 🔑 Clés privées
API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"  # clé OSINT cachée

# 🚪 Clé API utilisateur
MY_API_KEY = "test"

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
    # Vérification de la clé utilisateur
    if user_key != MY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    params = {
        "apikey": API_KEY,
        "storageid": storageid,
        "bucket": bucket,
        "download": str(download).lower()
    }

    try:
        r = requests.get(API_URL, params=params, stream=True, timeout=20)
        r.raise_for_status()

        # Générer un nom unique pour le fichier
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{storageid[:10]}_{bucket}_{unique_id}.txt"
        filepath = os.path.join(RESULTS_DIR, filename)

        # Sauvegarder tout le contenu dans un fichier, même si c’est JSON
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
        # Si une erreur réseau se produit, écrire le message dans un fichier
        error_filename = f"error_{uuid.uuid4().hex[:8]}.txt"
        error_filepath = os.path.join(RESULTS_DIR, error_filename)
        with open(error_filepath, "w") as f:
            f.write(str(e))
        return FileResponse(
            error_filepath,
            media_type="text/plain",
            filename=error_filename
        )
