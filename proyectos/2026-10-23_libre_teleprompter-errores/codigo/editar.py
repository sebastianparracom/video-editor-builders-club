# Montaje: cortes del guion de corte, zooms suaves hacia la cara y subtítulos clásicos abajo.
# Uso: .venv/bin/python codigo/editar.py preview|final
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROY = Path(__file__).resolve().parents[1]
ORIGEN = PROY / "crudo/grabacion.mp4"
MODO = sys.argv[1] if len(sys.argv) > 1 else "preview"
W, H = (960, 540) if MODO == "preview" else (1920, 1080)
ESC = W / 1920

# Segmentos (segundos de origen) y zoom inicial → final de cada uno.
# Entre tomas el zoom salta (oculta el corte); dentro de cada toma avanza despacio.
SEGMENTOS = [
    (6.52, 9.70, 1.00, 1.05),
    (14.49, 19.95, 1.16, 1.20),
    (25.45, 32.30, 1.02, 1.10),
    (35.38, 39.85, 1.18, 1.23),
]
CARA_X, CARA_Y = 0.43, 0.40  # centro del zoom (fracción del cuadro), medido en la hoja de contactos
FADE = 0.02

FUENTE = "/System/Library/Fonts/SFNS.ttf" if Path("/System/Library/Fonts/SFNS.ttf").exists() else "/Library/Fonts/Arial Unicode.ttf"
TAM_LETRA = 54
MAX_CARACTERES = 50
MARGEN_INF = 0.08
ENLACES = {"el", "la", "los", "las", "un", "una", "de", "del", "a", "al", "en", "con", "por", "para", "y", "o", "que", "me", "se", "entre", "sin", "sobre"}
MULETILLAS = {"eh", "ah", "mm", "um", "ay", "este"}


def subtitulos():
    """Palabras dentro de los segmentos → tiempos de salida → frases de una línea."""
    datos = json.loads((PROY / "audio/transcripcion.json").read_text())
    palabras, desfase = [], 0.0
    for ini, fin, *_ in SEGMENTOS:
        for p in datos["words"]:
            s, e = p["start"] / 1000, p["end"] / 1000
            if s >= ini and e <= fin + 0.05:
                palabras.append((p["text"], s - ini + desfase, min(e, fin) - ini + desfase))
        desfase += fin - ini

    palabras = [p for p in palabras if p[0].strip(",.;").lower() not in MULETILLAS]

    # Oraciones completas; las largas se parten en la coma más centrada (o en la palabra más centrada).
    oraciones, actual = [], []
    for p in palabras:
        actual.append(p)
        if p[0].endswith((".", "?", "!")):
            oraciones.append(actual)
            actual = []
    if actual:
        oraciones.append(actual)

    def partir(ps):
        texto = " ".join(t for t, *_ in ps)
        if len(texto) <= MAX_CARACTERES:
            return [ps]
        largo = lambda q: len(" ".join(t for t, *_ in q))
        cortes = [k for k in range(1, len(ps)) if ps[k - 1][0].endswith((",", ";"))
                  and largo(ps[:k]) <= MAX_CARACTERES and largo(ps[k:]) <= MAX_CARACTERES] or list(range(1, len(ps)))
        # Nunca dejar un artículo o preposición colgando al final de la línea.
        cortes = [k for k in cortes if ps[k - 1][0].lower() not in ENLACES] or cortes
        k = min(cortes, key=lambda k: abs(largo(ps[:k]) - len(texto) / 2) - (4 if ps[k][0] in ("y", "o", "que") else 0))
        return partir(ps[:k]) + partir(ps[k:])

    frases = []
    for o in oraciones:
        for n, ps in enumerate(partir(o)):
            texto = " ".join(t for t, *_ in ps)
            frases.append([texto[0].upper() + texto[1:] if n == 0 else texto, ps[0][1], ps[-1][2]])
    # Cada frase se mantiene hasta la siguiente si el hueco es corto.
    for a, b in zip(frases, frases[1:]):
        a[2] = b[1] if b[1] - a[2] < 0.7 else a[2] + 0.3
    frases[-1][2] += 0.3
    return frases


def png_subtitulo(texto, ruta):
    fuente = ImageFont.truetype(FUENTE, round(TAM_LETRA * ESC))
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    caja = d.textbbox((0, 0), texto, font=fuente)
    x = (W - (caja[2] - caja[0])) / 2 - caja[0]
    y = H * (1 - MARGEN_INF) - caja[3]
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).text((x, y + 2 * ESC), texto, font=fuente, fill=(0, 0, 0, 200))
    capa = Image.alpha_composite(capa, sombra.filter(ImageFilter.GaussianBlur(4 * ESC)))
    d = ImageDraw.Draw(capa)
    d.text((x, y), texto, font=fuente, fill="white", stroke_width=max(1, round(3 * ESC)), stroke_fill=(0, 0, 0, 230))
    capa.save(ruta)


def main():
    tmp = PROY / "trabajo/subs"
    tmp.mkdir(parents=True, exist_ok=True)
    frases = subtitulos()
    (PROY / "trabajo/subtitulos.json").write_text(json.dumps(frases, ensure_ascii=False, indent=1))

    entradas = ["-i", str(ORIGEN)]
    filtros, etiquetas = [], []
    for i, (ini, fin, z0, z1) in enumerate(SEGMENTOS):
        dur = fin - ini
        p = f"clip(t/{dur:.3f},0,1)"
        z = f"({z0}+({z1 - z0:.3f})*{p}*{p}*(3-2*{p}))"
        filtros.append(
            f"[0:v]trim={ini}:{fin},setpts=PTS-STARTPTS,"
            f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame,"
            f"crop={W}:{H}:x='clip(iw*{CARA_X}-{W / 2},0,iw-{W})':y='clip(ih*{CARA_Y}-{H / 2},0,ih-{H})',setsar=1[v{i}]"
        )
        filtros.append(
            f"[0:a]atrim={ini}:{fin},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d={FADE},afade=t=out:st={dur - FADE:.3f}:d={FADE}[a{i}]"
        )
        etiquetas.append(f"[v{i}][a{i}]")
    filtros.append(f"{''.join(etiquetas)}concat=n={len(SEGMENTOS)}:v=1:a=1[vc][ac]")

    previo = "vc"
    for j, (texto, s, e) in enumerate(frases):
        ruta = tmp / f"sub_{j:02d}.png"
        png_subtitulo(texto, ruta)
        entradas += ["-i", str(ruta)]
        filtros.append(f"[{previo}][{j + 1}:v]overlay=0:0:enable='between(t,{s:.3f},{e:.3f})'[s{j}]")
        previo = f"s{j}"

    if MODO == "preview":
        salida = PROY / "borradores/preview_v1.mp4"
        filtros.append(f"[ac]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        video = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"]
    else:
        salida = PROY / "final/2026-10-23_libre_teleprompter-errores_v1.mp4"
        filtros.append(f"[ac]{sys.argv[2]}[aout]")  # loudnorm de segunda pasada, con valores medidos
        video = ["-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "18"]

    cmd = ["ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", ";".join(filtros),
           "-map", f"[{previo}]", "-map", "[aout]", *video, "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(salida)]
    subprocess.run(cmd, check=True)
    for f in frases:
        print(f"{f[1]:6.2f}-{f[2]:6.2f}  {f[0]}")
    print(salida)


main()
