from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse, Response
import requests
import uuid
import os

app = FastAPI()

# 🔑 Clés directement dans le code
API_URL = "https://osintsolutions.org/api/intelx_advanced"
API_KEY = "TZ1JuGJ-kwQ-CwZ7Y7v1k-CwZ7Y7v1k-CVf6mWJ6UJ"  # clé IntelX
MY_API_KEY = "test"  # clé utilisateur interne

# 📂 Dossier pour résultats temporaires
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "API IntelX Proxy - utilisez /fetch avec user_key et storageid"}

@app.get("/fetch")
def fetch_data(
    user_key: str = Query(..., description="Votre clé API interne"),
    storageid: str = Query(..., description="ID IntelX à récupérer"),
    bucket: str = Query("leaks.logs", description="Nom du bucket"),
    download: bool = Query(False, description="Télécharger en fichier ou renvoyer le contenu")
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
        r = requests.get(API_URL, params=params, stream=True, timeout=30)
        r.raise_for_status()

        if download:
            # Générer un nom unique pour le fichier
            unique_id = uuid.uuid4().hex[:8]
            filename = f"{storageid[:10]}_{bucket}_{unique_id}.txt"
            filepath = os.path.join(RESULTS_DIR, filename)

            # Écriture du contenu IntelX dans le fichier
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Retourner le fichier
            return FileResponse(
                filepath,
                media_type="text/plain",
                filename=filename
            )
        else:
            # Retour direct du contenu sans fichier
            return Response(r.content, media_type="text/plain")

    except requests.exceptions.RequestException as e:
        # Retourner erreur en texte
        error_msg = f"Erreur IntelX : {str(e)}"
        if e.response is not None:
            try:
                error_msg += f"\n{e.response.text}"
            except:
                pass
        return Response(error_msg, media_type="text/plain")
