# Genera la voz en off con ElevenLabs.
# Uso: .venv/bin/python codigo/voz.py <modelo> <archivo_salida.mp3> [velocidad]
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[3]
load_dotenv(RAIZ / ".env", override=True)

VOZ = "7bmVaeToqOpy05SKlvVj"  # clon "Sebastian PArra"
TEXTO = (
    "Este vídeo no pasó por ningún editor. "
    "Cero Premiere. Cero After Effects. "
    "Solo código, IA y un workflow bien diseñado. "
    "Motion graphics, escritos línea por línea."
)

modelo, salida = sys.argv[1], Path(sys.argv[2])
velocidad = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0  # 0.7 a 1.2
r = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOZ}",
    params={"output_format": "mp3_44100_128"},
    headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
    json={"text": TEXTO, "model_id": modelo, "voice_settings": {"speed": velocidad}},
    timeout=120,
)
if r.status_code != 200:
    sys.exit(f"Error {r.status_code}: {r.text[:500]}")
salida.parent.mkdir(parents=True, exist_ok=True)
salida.write_bytes(r.content)
print(f"ok {salida} ({len(r.content)} bytes)")
