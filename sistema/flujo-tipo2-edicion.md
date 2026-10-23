# Flujo tipo 2: edición de material crudo

Límite que hay que tener presente: no veo el vídeo en tiempo real. Trabajo con la transcripción, el análisis de audio y fotogramas extraídos. Las decisiones basadas en el habla son precisas; las puramente visuales (expresión, desenfoques breves) son aproximadas y se le señalan al usuario.

## Etapa 0: ingesta (sin aprobación)

1. Inventario de `crudo/` con `ffprobe`: resolución, fps, duración, códec, pistas de audio. Se anota en `proyecto.md`.
2. Copias ligeras (proxies) en `trabajo/proxies/` si el material es mayor de 1080p o usa un códec pesado (ProRes, HEVC 10 bits). El render final usa siempre los originales.
3. Extraer el audio a WAV en `trabajo/` y transcribirlo con AssemblyAI (identificación de hablantes si hay varias personas; ver [apis.md](apis.md)).
4. Hoja de contactos: una cuadrícula de fotogramas por archivo para entender el material de un vistazo.

## Etapa 1: guion de corte (resumen rápido)

- Lista de segmentos que se quedan, en orden, con tiempos de origen y texto.
- Una línea con lo eliminado (silencios, muletillas, repeticiones, tomas descartadas) y la duración resultante.
- Si hay varias tomas o clips candidatos: la elección y el porqué en una línea cada uno.
- **Entrega:** el resumen. → aprobación.

## Etapa 2: corte en bruto (resumen rápido)

- Montaje solo con cortes, sin adornos, en baja resolución, en `borradores/`.
- **Entrega:** el vídeo y un resumen de 2 o 3 líneas. → aprobación.

## Etapa 3: capas (revisión detallada)

Todo lo que va encima del corte: reencuadre, subtítulos, títulos, gráficos, b-roll, zooms, color, música y efectos. Se pregunta el tipo de subtítulos si no está decidido.

- **Entrega:** fotogramas de muestra de cada elemento nuevo, más un fragmento de vídeo representativo. → aprobación.

## Etapa 4: render final

- Render desde los originales a la calidad acordada.
- Verificaciones de [reglas-tecnicas.md](reglas-tecnicas.md#verificación-antes-de-entregar).
- **Entrega:** `final/<id>_vN.mp4`.

## Etapa 5: cierre

Ver [reglas-tecnicas.md](reglas-tecnicas.md#cierre-de-proyecto).

## Cómo se hace cada tipo de edición

| Edición | Método |
|---|---|
| Silencios | Huecos entre palabras de la transcripción, confirmados con `silencedetect` de FFmpeg. Dejar un pequeño margen para no cortar respiraciones de forma brusca |
| Muletillas y repeticiones | Desde la transcripción con muletillas incluidas (ver apis.md). Revisar a mano las dudosas |
| Mejor toma | Comparar tomas por texto (completitud, fluidez) y por fotogramas. Presentar la elección con su motivo |
| Clips de un vídeo largo | Proponer candidatos con tiempos, gancho inicial y motivo; el usuario elige |
| Varias cámaras | Sincronizar por correlación de audio; elegir el plano según quién habla |
| Reencuadre a vertical | Detección de cara con OpenCV/MediaPipe, trayectoria suavizada, recorte con FFmpeg |
| Limpieza de audio | Ruido leve: filtros de FFmpeg (`afftdn`, `highpass`). Audio sucio: Voice Isolator de ElevenLabs |
| Volumen | `loudnorm` de FFmpeg en dos pasadas a -14 LUFS |
| Color | Filtros `eq`, `colorbalance` o LUT con `lut3d`; igualar cámaras distintas |
| Gráficos, títulos, subtítulos | Generados con Python (Pillow/Cairo) como imágenes o secuencias con transparencia y superpuestos con FFmpeg |
| Música y efectos | ElevenLabs; música atenuada bajo la voz (`sidechaincompress` o automatización de volumen) |

Los cortes se hacen siempre recodificando, nunca con copia de flujo, para que sean exactos al fotograma.
