from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
import requests
import uuid
import os

app = FastAPI()

API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CVf6mWJ6UJ"  # clé IntelX
MY_API_KEY = "test"
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

    unique_id = uuid.uuid4().hex[:8]
    filename = f"{storageid[:10]}_{bucket}_{unique_id}.txt"
    filepath = os.path.join(RESULTS_DIR, filename)

    try:
        r = requests.get(API_URL, params=params, stream=True, timeout=20)
        r.raise_for_status()

        # Écriture du contenu IntelX dans le fichier
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    except requests.exceptions.RequestException as e:
        # Même en cas d'erreur (403, 404...), écrire l'erreur dans le fichier
        with open(filepath, "w") as f:
            f.write(f"Erreur IntelX : {str(e)}\n")
            if e.response is not None:
                try:
                    f.write(e.response.text)
                except:
                    pass

    # Retourner le fichier en téléchargement
    return FileResponse(
        filepath,
        media_type="text/plain",
        filename=filename
    )
