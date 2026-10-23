# Transcribe un audio con AssemblyAI y guarda el JSON completo (con tiempos por palabra).
# Uso: .venv/bin/python codigo/transcribir.py <audio> <salida.json> [opciones JSON extra]
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[3]
load_dotenv(RAIZ / ".env", override=True)
BASE = "https://api.assemblyai.com"
CAB = {"authorization": os.environ["ASSEMBLYAI_API_KEY"]}

audio, salida = Path(sys.argv[1]), Path(sys.argv[2])
extra = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}

url = requests.post(f"{BASE}/v2/upload", headers=CAB, data=audio.read_bytes(), timeout=300).json()["upload_url"]
cuerpo = {"audio_url": url, "speech_models": ["universal-3-5-pro"], "language_codes": ["es", "en"], **extra}
r = requests.post(f"{BASE}/v2/transcript", headers=CAB, json=cuerpo, timeout=60)
if r.status_code != 200:
    sys.exit(f"Error {r.status_code}: {r.text[:500]}")
tid = r.json()["id"]

while True:
    t = requests.get(f"{BASE}/v2/transcript/{tid}", headers=CAB, timeout=60).json()
    if t["status"] in ("completed", "error"):
        break
    time.sleep(2)
if t["status"] == "error":
    sys.exit(f"Error de transcripción: {t.get('error')}")

salida.parent.mkdir(parents=True, exist_ok=True)
salida.write_text(json.dumps(t, ensure_ascii=False, indent=1))
print(t["text"])
print(" ".join(f"{w['text']}[{w['start']/1000:.2f}-{w['end']/1000:.2f}]" for w in t["words"]))
