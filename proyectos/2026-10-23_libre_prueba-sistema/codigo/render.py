# Render del vídeo de prueba: motion graphics 100 % con código (Pillow + numpy + FFmpeg).
# Uso:
#   .venv/bin/python codigo/render.py frames <t1,t2,...> <carpeta>   → PNG de fotogramas clave
#   .venv/bin/python codigo/render.py video <salida.mp4> [ancho]     → vídeo sin audio (ancho 540 = vista previa)
import json
import math
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROY = Path(__file__).resolve().parents[1]
W, H, FPS, DUR = 1080, 1920, 30, 12.0
CX, CY = W // 2, H // 2
BG = (10, 10, 11)
FG = (245, 245, 240)
LIMA = (198, 255, 0)
F_BOLD = str(Path.home() / "Library/Fonts/NeueMontreal-Bold.otf")
F_MONO = "/Library/Fonts/SF-Mono-Medium.otf"
F_BLACK = "/Library/Fonts/SF-Pro-Display-Black.otf"

PAL = json.loads((PROY / "audio/voz/transcripcion.json").read_text())["words"]
T = [(w["start"] / 1000, w["end"] / 1000) for w in PAL]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_back(x, s=2.4):
    x = clamp(x) - 1
    return 1 + (s + 1) * x**3 + s * x**2


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


# ---------------------------------------------------------------- bloques de subtítulo (estilo b)
# (primera palabra, última palabra, líneas [[(texto, acento)]], tamaño máximo)
BLOQUES = [
    (0, 1, [[("ESTE", 0), ("VIDEO", 0)]], 210),
    (2, 4, [[("NO", 0), ("PASÓ", 0), ("POR", 0)]], 210),
    (5, 6, [[("NINGÚN", 1)], [("EDITOR", 1)]], 250),
    (7, 8, [[("CERO", 1)], [("PREMIERE", 0)]], 230),
    (9, 11, [[("CERO", 1)], [("AFTER", 0)], [("EFFECTS", 0)]], 230),
    (12, 13, [[("SOLO", 0)], [("CÓDIGO", 1)]], 230),
    (14, 14, [[("IA", 1)]], 520),
    (15, 17, [[("Y", 0), ("UN", 0)], [("WORKFLOW", 1)]], 230),
    (18, 19, [[("BIEN", 0)], [("DISEÑADO", 0)]], 220),
    (20, 21, [[("MOTION", 1)], [("GRAPHICS", 1)]], 230),
    (22, 25, [[("ESCRITOS", 0)], [("LÍNEA POR", 1)], [("LÍNEA", 1)]], 200),
]
INICIO = [T[b[0]][0] - 0.05 for b in BLOQUES]
FIN = INICIO[1:] + [DUR]
TACHADO = {3: (T[8][0] + 0.02, T[8][1] + 0.04), 4: (T[10][0], T[11][1] + 0.02)}  # bloque: (tachar, romper)
ULTIMO = len(BLOQUES) - 1
SUBRAYADO = [(1, T[23][0]), (2, T[25][0])]  # (línea, momento) del último bloque


@lru_cache(None)
def img_bloque(k, tachar=False):
    _, _, lineas, tope = BLOQUES[k]
    size = tope
    while True:
        f = ImageFont.truetype(F_BOLD, size)
        anchos = [f.getlength(" ".join(t for t, _ in l)) for l in lineas]
        if max(anchos) <= 900 or size < 60:
            break
        size -= 6
    hb = f.getbbox("H", anchor="ls")
    alto = int(size * 0.97)
    pad = 60
    w, h = int(max(anchos)) + 2 * pad, alto * len(lineas) + 2 * pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cajas = []
    for j, l in enumerate(lineas):
        x = (w - anchos[j]) / 2
        base = pad + j * alto + alto * 0.82
        cajas.append((x, base + (hb[1] + hb[3]) / 2, x + anchos[j], base))
        for txt, ac in l:
            d.text((x, base), txt, font=f, fill=(*(LIMA if ac else FG), 255), anchor="ls")
            x += f.getlength(txt + " ")
    if tachar:
        x0, ym, x1, _ = cajas[-1]
        g = size * 0.11
        d.rectangle((x0 - 25, ym - g / 2, x1 + 25, ym + g / 2), fill=(*LIMA, 255))
    return im, cajas, size


def pegar(canvas, im, cx, cy, escala=1.0, angulo=0.0, opacidad=1.0):
    if escala <= 0.01 or opacidad <= 0.01:
        return
    if abs(escala - 1) > 0.002:
        im = im.resize((max(1, int(im.width * escala)), max(1, int(im.height * escala))), Image.Resampling.BILINEAR)
    if abs(angulo) > 0.05:
        im = im.rotate(angulo, resample=Image.Resampling.BILINEAR, expand=True)
    if opacidad < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * opacidad))
        im = im.copy()
        im.putalpha(a)
    canvas.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


# ---------------------------------------------------------------- fragmentos al romper el texto tachado
def preparar_fragmentos(k, rng):
    im, _, _ = img_bloque(k, True)
    cols, filas = 10, 6
    tw, th = im.width / cols, im.height / filas
    frags = []
    for c in range(cols):
        for f in range(filas):
            caja = (int(c * tw), int(f * th), int((c + 1) * tw), int((f + 1) * th))
            pieza = im.crop(caja)
            if pieza.getchannel("A").getbbox() is None:
                continue
            ox = caja[0] + tw / 2 - im.width / 2
            oy = caja[1] + th / 2 - im.height / 2
            ang = math.atan2(oy, ox) + rng.uniform(-0.6, 0.6)
            vel = rng.uniform(900, 2600)
            frags.append((pieza, ox, oy, math.cos(ang) * vel, math.sin(ang) * vel - 300, rng.uniform(-900, 900)))
    return frags


RNG = np.random.default_rng(7)
FRAGMENTOS = {k: preparar_fragmentos(k, RNG) for k in TACHADO}

# ---------------------------------------------------------------- fondos precalculados
def rejilla(color, paso=54):
    im = Image.new("RGBA", (W, H + paso), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(0, H + paso, paso):
        for x in range(paso // 2, W, paso):
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=color)
    return im


REJILLA = rejilla((38, 38, 42, 255))
REJILLA_LIMA = rejilla((*LIMA, 255))


@lru_cache(None)
def cero_gigante(color):
    f = ImageFont.truetype(F_BLACK, 1500)
    im = Image.new("RGBA", (1300, 1700), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((650, 850), "0", font=f, anchor="mm", fill=(0, 0, 0, 0), stroke_width=7, stroke_fill=color)
    return im


SOMBRA = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(SOMBRA).ellipse((CX - 520, CY - 420, CX + 520, CY + 420), fill=(6, 6, 7, 215))
SOMBRA = SOMBRA.filter(ImageFilter.GaussianBlur(120))

CODIGO = [l.rstrip() for l in Path(__file__).read_text().splitlines() if l.strip()][:150]
F_COD = ImageFont.truetype(F_MONO, 25)
F_NODO = ImageFont.truetype(F_MONO, 26)

NODOS = [("VOZ", 230, 470, 6.00), ("TRANSCRIPCIÓN", 820, 380, 6.30), ("IA", 170, 1430, T[14][0]),
         ("CÓDIGO", 900, 1330, 6.95), ("FFMPEG", 300, 1690, 7.40), ("RENDER", 800, 1720, 7.85)]
ARISTAS = [(0, 1), (1, 3), (2, 3), (0, 2), (3, 4), (4, 5)]

# ---------------------------------------------------------------- partículas de la explosión final
T_EXPLOSION = T[20][0]
T_ARMADO = INICIO[ULTIMO]
N_PART = 1600
ANG = RNG.uniform(0, 2 * math.pi, N_PART)
VEL = 300 + 3200 * RNG.random(N_PART) ** 2.2
V0 = np.stack([np.cos(ANG) * VEL, np.sin(ANG) * VEL], 1)
P0 = RNG.normal(0, 25, (N_PART, 2)) + [CX, CY]
ES_LIMA = RNG.random(N_PART) < 0.7
K_ARRASTRE = 2.2


def destinos():
    im, _, _ = img_bloque(ULTIMO)
    ys, xs = np.nonzero(np.array(im.getchannel("A")) > 128)
    idx = RNG.choice(len(xs), N_PART, replace=len(xs) < N_PART)
    return np.stack([xs[idx] - im.width / 2 + CX, ys[idx] - im.height / 2 + CY], 1)


DESTINOS = destinos()


def particulas(t):
    dt = t - T_EXPLOSION
    caida = (1 - math.exp(-K_ARRASTRE * dt)) / K_ARRASTRE
    pos = P0 + V0 * caida
    vel = V0 * math.exp(-K_ARRASTRE * dt)
    if t >= T_ARMADO:
        e = ease_in_out((t - T_ARMADO) / 0.42)
        pos_armado = P0 + V0 * (1 - math.exp(-K_ARRASTRE * (T_ARMADO - T_EXPLOSION))) / K_ARRASTRE
        pos = pos_armado * (1 - e) + DESTINOS * e
        vel = vel * 0
    return pos, vel


# ---------------------------------------------------------------- golpes: sacudida, zoom, aberración, glitch, destellos
GOLPES = [(i, 0.35) for i in INICIO]
GOLPES += [(T[6][0], 1.0), (INICIO[3], 0.6), (INICIO[5], 0.5), (T[14][0], 0.85), (T[17][0], 0.5),
           (T_EXPLOSION, 1.1), (T_ARMADO + 0.42, 0.5), (T[25][1] - 0.04, 1.2)]
GOLPES += [(r, 0.8) for _, r in TACHADO.values()]
DESTELLOS = [(0.0, 0.9, 0.09), (INICIO[3], 0.45, 0.05), (INICIO[5], 0.35, 0.05), (T_EXPLOSION, 0.7, 0.08),
             (T[25][1] - 0.04, 0.7, 0.10)]


def envolvente(t, eventos, tau=0.12):
    return sum(s * math.exp(-(t - t0) / tau) for t0, s in eventos if t >= t0)


def destello(t):
    return clamp(sum(s * math.exp(-(t - t0) / tau) for t0, s, tau in DESTELLOS if t >= t0))


def camara(t):
    e = envolvente(t, GOLPES)
    z = 1 + 0.07 * e
    if 5.3 <= t < T_EXPLOSION:
        z *= 1 + 0.07 * (t - 5.3) / (T_EXPLOSION - 5.3)
    sx = 38 * e * (math.sin(t * 53.1) + 0.6 * math.sin(t * 91.7 + 1.3))
    sy = 38 * e * (math.sin(t * 47.3 + 2.1) + 0.6 * math.sin(t * 83.9))
    th = math.radians(1.6 * e * math.sin(t * 37.0))
    return z, sx, sy, th


def aplicar_camara(im, t):
    z, sx, sy, th = camara(t)
    if abs(z - 1) < 1e-3 and abs(sx) < 0.3 and abs(sy) < 0.3 and abs(th) < 1e-4:
        return im
    c, s = math.cos(th), math.sin(th)
    a, b, d, e = c / z, s / z, -s / z, c / z
    cx, cy = CX + sx, CY + sy
    datos = (a, b, CX - a * cx - b * cy, d, e, CY - d * cx - e * cy)
    return im.transform((W, H), Image.Transform.AFFINE, datos, resample=Image.Resampling.BILINEAR, fillcolor=BG)


# ---------------------------------------------------------------- capas por escena
def capa_rejilla(cv, t):
    off = int((t * 90) % 54)
    cv.paste(REJILLA, (0, off - 54), REJILLA)
    e = envolvente(t, GOLPES)
    if e > 0.08:
        g = REJILLA_LIMA.copy()
        g.putalpha(REJILLA_LIMA.getchannel("A").point(lambda v: int(v * clamp(e * 0.55))))
        cv.paste(g, (0, off - 54), g)


def capa_lineas_velocidad(cv, t):
    t0 = T[6][0]
    if not (t0 <= t < t0 + 0.6):
        return
    d = ImageDraw.Draw(cv)
    r = np.random.default_rng(3)
    for i in range(90):
        ang = r.uniform(0, 2 * math.pi)
        v = r.uniform(2500, 6000)
        r0 = 260 + (t - t0) * v
        largo = r.uniform(150, 500)
        a = clamp(1 - (t - t0) / 0.6)
        col = LIMA if i % 3 else FG
        col = tuple(int(BG[j] + (col[j] - BG[j]) * a) for j in range(3))
        d.line((CX + math.cos(ang) * r0, CY + math.sin(ang) * r0,
                CX + math.cos(ang) * (r0 + largo), CY + math.sin(ang) * (r0 + largo)), fill=col, width=int(r.uniform(2, 7)))


def capa_cero(cv, t):
    t0 = INICIO[3]
    golpe = any(0 <= t - T[i][0] < 0.18 for i in (7, 9))
    im = cero_gigante(LIMA + (255,) if golpe else (52, 52, 58, 255))
    pegar(cv, im, CX, CY, 1 + 0.06 * (t - t0), -8 * (t - t0), clamp((t - t0) / 0.1))


def capa_codigo(t, colapso):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    escritos = (t - 5.3) * 1600
    filas, total = [], 0
    for l in CODIGO:
        if total + len(l) <= escritos:
            filas.append(l)
            total += len(l)
        else:
            filas.append(l[: int(max(0, escritos - total))])
            break
    filas = filas[-52:]
    y = 110
    for i, l in enumerate(filas):
        clave = l.lstrip().startswith(("def ", "class ", "import ", "from ", "for ", "return"))
        d.text((48, y), l, font=F_COD, fill=(130, 165, 15, 255) if clave else (88, 88, 96, 255))
        if i == len(filas) - 1 and int(t * 6) % 2 == 0:
            x = 48 + F_COD.getlength(l)
            d.rectangle((x + 3, y + 2, x + 17, y + 30), fill=(*LIMA, 255))
        y += 33
    for nombre, nx, ny, ta in NODOS:
        if t < ta:
            continue
        nx, ny = nx + (CX - nx) * colapso, ny + (CY - ny) * colapso
        p = clamp((t - ta) / 0.35)
        rr = 15 * ease_out_back(min(1, (t - ta) / 0.2))
        if p < 1:
            ra = 15 + 70 * ease_out(p)
            col = tuple(int(c * (1 - p)) for c in LIMA)
            d.ellipse((nx - ra, ny - ra, nx + ra, ny + ra), outline=(*col, 255), width=4)
        d.ellipse((nx - rr, ny - rr, nx + rr, ny + rr), fill=(*LIMA, 255))
        d.text((nx, ny + 34), nombre, font=F_NODO, anchor="mt", fill=(200, 200, 205, 255))
    for i, (a, b) in enumerate(ARISTAS):
        ta = max(NODOS[a][3], NODOS[b][3]) + 0.05
        if t < ta:
            continue
        ax, ay = NODOS[a][1:3]
        bx, by = NODOS[b][1:3]
        ax, ay = ax + (CX - ax) * colapso, ay + (CY - ay) * colapso
        bx, by = bx + (CX - bx) * colapso, by + (CY - by) * colapso
        p = ease_out((t - ta) / 0.3)
        ex, ey = ax + (bx - ax) * p, ay + (by - ay) * p
        d.line((ax, ay, ex, ey), fill=(150, 190, 0, 255), width=3)
        if p >= 1:
            q = (t * 1.6 + i * 0.37) % 1
            px, py = ax + (bx - ax) * q, ay + (by - ay) * q
            d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(255, 255, 255, 255))
    if colapso > 0:
        capa = capa.resize((W, H)).transform(
            (W, H), Image.Transform.AFFINE,
            (1 / (1 - 0.92 * colapso), 0, CX - CX / (1 - 0.92 * colapso), 0, 1 / (1 - 0.92 * colapso), CY - CY / (1 - 0.92 * colapso)),
            resample=Image.Resampling.BILINEAR)
    a = clamp((t - 5.3) / 0.2) * (1 - colapso)
    if a < 0.999:
        capa.putalpha(capa.getchannel("A").point(lambda v: int(v * a)))
    return capa


def capa_particulas(cv, t):
    dt = t - T_EXPLOSION
    if dt < 0 or t > T_ARMADO + 0.62:
        return
    d = ImageDraw.Draw(cv)
    if dt < 0.4:
        ra = dt * 3200
        anchura = max(1, int(14 * (1 - dt / 0.4)))
        d.ellipse((CX - ra, CY - ra, CX + ra, CY + ra), outline=LIMA, width=anchura)
    pos, vel = particulas(t)
    desvanecer = 1 - clamp((t - T_ARMADO - 0.42) / 0.2)
    for i in range(0, N_PART, 1):
        x, y = pos[i]
        col = LIMA if ES_LIMA[i] else FG
        if desvanecer < 1:
            col = tuple(int(BG[j] + (col[j] - BG[j]) * desvanecer) for j in range(3))
        vx, vy = vel[i] * 0.03
        if abs(vx) + abs(vy) > 2:
            d.line((x, y, x - vx, y - vy), fill=col, width=3)
        else:
            d.rectangle((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=col)


def capa_texto(cv, t):
    for k in range(len(BLOQUES)):
        ini, fin = INICIO[k], FIN[k]
        romper = TACHADO.get(k, (None, None))[1]
        if romper is not None and romper <= t < romper + 0.55:
            for pieza, ox, oy, vx, vy, w in FRAGMENTOS[k]:
                dt = t - romper
                pegar(cv, pieza, CX + ox + vx * dt, CY + oy + vy * dt + 900 * dt * dt, 1 + dt * 0.6, w * dt,
                      clamp(1 - dt / 0.55))
        if not (ini <= t < fin) or (romper is not None and t >= romper):
            continue
        tachar = k in TACHADO and t >= TACHADO[k][0]
        im, cajas, size = img_bloque(k, tachar)
        if tachar and t < TACHADO[k][0] + 0.12:
            # el tachado crece: se dibuja parcial sobre la versión limpia
            im = img_bloque(k)[0].copy()
            x0, ym, x1, _ = cajas[-1]
            g = size * 0.11
            p = ease_out((t - TACHADO[k][0]) / 0.12)
            ImageDraw.Draw(im).rectangle((x0 - 25, ym - g / 2, x0 - 25 + (x1 - x0 + 50) * p, ym + g / 2), fill=(*LIMA, 255))
        if k == ULTIMO:
            op = clamp((t - (T_ARMADO + 0.32)) / 0.12)
            im = im.copy()
            d = ImageDraw.Draw(im)
            for linea, tl in SUBRAYADO:
                if t >= tl:
                    x0, _, x1, base = cajas[linea]
                    p = ease_out((t - tl) / 0.15)
                    d.rectangle((x0, base + 9, x0 + (x1 - x0) * p, base + 17), fill=(*LIMA, 255))
            pegar(cv, im, CX, CY, 1 + 0.03 * (t - ini), 0, op)
            continue
        u = (t - ini) / 0.2
        escala = 2.5 + (1 - 2.5) * ease_out_back(u) + 0.035 * (t - ini)
        angulo = -7 * (1 - ease_out(u))
        pegar(cv, im, CX, CY, escala, angulo, clamp((t - ini) / 0.05))


def muestra(t):
    cv = Image.new("RGBA", (W, H), (*BG, 255))
    if t < 5.3:
        capa_rejilla(cv, t)
    if INICIO[3] <= t < 5.3:
        capa_cero(cv, t)
    capa_lineas_velocidad(cv, t)
    if 5.3 <= t < T_EXPLOSION:
        colapso = ease_in_out((t - (T_EXPLOSION - 0.26)) / 0.26)
        capa = capa_codigo(t, colapso)
        cv.paste(capa, (0, 0), capa)
    if t >= 5.3:
        cv.paste(SOMBRA, (0, 0), SOMBRA)
    capa_particulas(cv, t)
    capa_texto(cv, t)
    return aplicar_camara(cv.convert("RGB"), t)


# ---------------------------------------------------------------- posproceso
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VINETA = (1 - 0.55 * np.clip(((xx - CX) / (W * 0.75)) ** 2 + ((yy - CY) / (H * 0.62)) ** 2, 0, 1))[..., None]
GRANO = [np.random.default_rng(i).normal(0, 7, (H, W, 1)).astype(np.float32) for i in range(6)]
del yy, xx


def movimiento_rapido(t):
    if envolvente(t, GOLPES) > 0.15 or T_EXPLOSION <= t < T_ARMADO + 0.5:
        return True
    if any(0 <= t - i < 0.22 for i in INICIO):
        return True
    return any(r <= t < r + 0.55 for _, r in TACHADO.values())


def fotograma(n):
    t = n / FPS
    m = 5 if movimiento_rapido(t) else 1
    acum = np.zeros((H, W, 3), np.float32)
    for k in range(m):
        tk = t + ((k + 0.5) / m - 0.5) / FPS * 0.85 if m > 1 else t
        acum += np.asarray(muestra(max(0, tk)), np.float32)
    f = acum / m
    e = envolvente(t, GOLPES)
    # brillo (bloom)
    peq = Image.fromarray(np.clip(f - 150, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.Resampling.BILINEAR)
    peq = peq.filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.Resampling.BILINEAR)
    f += np.asarray(peq, np.float32) * (0.9 + 1.6 * clamp(e))
    # aberración cromática
    ca = int(4 + 22 * clamp(e))
    f[..., 0] = np.roll(f[..., 0], ca, 1)
    f[..., 2] = np.roll(f[..., 2], -ca, 1)
    # glitch por franjas
    g = e - 0.45
    if g > 0:
        r = np.random.default_rng(n)
        for _ in range(int(6 + 14 * g)):
            y0 = int(r.integers(0, H - 20))
            alto = int(r.integers(8, 90))
            f[y0:y0 + alto] = np.roll(f[y0:y0 + alto], int(r.normal(0, 140 * g)), 1)
            if r.random() < 0.35:
                f[y0:y0 + alto, :, 1] = np.roll(f[y0:y0 + alto, :, 1], int(r.normal(0, 60)), 1)
    # destello
    fl = destello(t)
    if fl > 0:
        f = f * (1 - fl) + np.array([255, 255, 245], np.float32) * fl
    f = f * VINETA + GRANO[n % 6]
    # corte final a negro
    f *= 1 - clamp((t - (DUR - 0.2)) / 0.17)
    return np.clip(f, 0, 255).astype(np.uint8)


def main():
    modo = sys.argv[1]
    if modo == "frames":
        tiempos = [float(x) for x in sys.argv[2].split(",")]
        out = Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        with Pool() as pool:
            imgs = pool.map(fotograma, [round(t * FPS) for t in tiempos])
        for t, im in zip(tiempos, imgs):
            Image.fromarray(im).save(out / f"f_{t:05.2f}.png")
        print("ok", len(imgs), "fotogramas")
        return
    salida = Path(sys.argv[2])
    ancho = int(sys.argv[3]) if len(sys.argv) > 3 else W
    escala = f"scale={ancho}:-2:flags=lanczos," if ancho != W else ""
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-vf", f"{escala}format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "18", str(salida)],
        stdin=subprocess.PIPE)
    total = round(DUR * FPS)
    with Pool() as pool:
        for i, im in enumerate(pool.imap(fotograma, range(total), chunksize=2)):
            ff.stdin.write(im.tobytes())
            if i % 60 == 0:
                print(f"{i}/{total}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("ok", salida)


if __name__ == "__main__":
    main()
