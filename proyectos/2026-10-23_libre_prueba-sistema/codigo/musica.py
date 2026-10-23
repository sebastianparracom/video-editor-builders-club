# Genera una pista de música instrumental con ElevenLabs.
# Uso: .venv/bin/python codigo/musica.py <duracion_ms> <archivo_salida.mp3> "<prompt>"
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[3]
load_dotenv(RAIZ / ".env", override=True)

duracion, salida, prompt = int(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
r = requests.post(
    "https://api.elevenlabs.io/v1/music",
    headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
    json={"prompt": prompt, "music_length_ms": duracion, "model_id": "music_v2_5", "force_instrumental": True},
    timeout=300,
)
if r.status_code != 200:
    sys.exit(f"Error {r.status_code}: {r.text[:500]}")
salida.parent.mkdir(parents=True, exist_ok=True)
salida.write_bytes(r.content)
print(f"ok {salida} ({len(r.content)} bytes)")
