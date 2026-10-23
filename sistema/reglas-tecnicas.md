# Reglas técnicas

## Qué es "código puro"

**Permitido**
- FFmpeg / ffprobe (instalados por Homebrew).
- Python 3 con librerías puntuales: `Pillow` o `pycairo` (dibujar texto y gráficos), `numpy` (procesamiento), `opencv-python` y `mediapipe` (detección de caras), `requests` (APIs), `python-dotenv` (leer `.env`).
- Las librerías de Python se instalan en un entorno virtual en la raíz: `.venv/`. Se crea la primera vez que hace falta.

**Prohibido**
- Frameworks de vídeo: Remotion, Hyperframes, MoviePy, Manim, motion canvas o similares.
- Skills de vídeo del entorno (lista en `CLAUDE.md`).
- Construir aplicaciones, servidores, interfaces o automatizaciones que funcionen solas.

## Estándar de exportación (se confirma en cada proyecto)

| Parámetro | Valor |
|---|---|
| Códec de vídeo | H.264 (libx264), perfil high, `yuv420p`, `-movflags +faststart` |
| Calidad | CRF 18, preset slow |
| Fotogramas | 30 fps (o los del material original en tipo 2, si se pide) |
| Audio | AAC, 48 kHz, 192 kbps, estéreo |
| Volumen | -14 LUFS integrado, pico real máximo -1 dBTP |

Resoluciones a 1080p según formato: 9:16 → 1080×1920, 16:9 → 1920×1080, 1:1 → 1080×1080, 4:5 → 1080×1350.

## Material y archivos

- `crudo/` es de solo lectura. Nunca se sobrescribe ni se recodifica en el sitio.
- Material mayor de 1080p o con códec pesado: trabajar con proxies, renderizar el final desde el original.
- Tipografías: solo archivos de fuente presentes en `marcas/<marca>/fuentes/` o instalados en el sistema. Si falta una fuente, se pide; no se sustituye en silencio.
- Versiones: `guion_v1.md`, `guion_v2.md`… y `<id>_v1.mp4`, `<id>_v2.mp4`… Los archivos ligeros conservan todas las versiones; de los renders pesados se conserva solo la última.

## Verificación antes de entregar

1. `ffprobe` del archivo final: resolución, fps, códec, duración y pistas correctas.
2. Volumen medido con `loudnorm` (modo análisis) dentro de ±1 LU del objetivo.
3. Revisar fotogramas extraídos en puntos clave: principio, cada cambio de escena, final. Comprobar textos cortados, márgenes seguros y legibilidad.
4. Subtítulos: comparar varios puntos contra la transcripción para confirmar la sincronía.
5. Sin cortes de audio bruscos ni clics en los empalmes (fundidos cortos de 10-30 ms).

## Cierre de proyecto

1. Borrar intermedios pesados: `trabajo/` completo (proxies, WAV de trabajo, renders de prueba) y los vídeos de `borradores/`.
2. Conservar: `crudo/`, `final/`, `guion/`, `codigo/`, `audio/` y `proyecto.md`.
3. Marcar el proyecto como cerrado en `proyecto.md`.
4. Guardar las lecciones aprendidas que no se hayan guardado ya.
5. Si el código o el método sirve para otros proyectos: ofrecer convertirlo en receta y promover a `herramientas/` el código reutilizable.
