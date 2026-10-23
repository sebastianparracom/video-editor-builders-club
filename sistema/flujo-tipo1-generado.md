# Flujo tipo 1: vídeo generado (motion graphics)

Cada etapa termina con una entrega al usuario y su aprobación. Se registra en `proyecto.md` qué se aprobó y cuándo.

## Etapa 1: guion

- Si el usuario da el guion: se pasa a formato de escenas sin cambiar el texto y se señalan dudas (frases largas para pantalla, pronunciaciones raras, mezcla de idiomas).
- Si lo escribo yo: se usa el tono de la marca (si hay) y el objetivo del brief.
- Formato del borrador, una tabla por escena:

| # | Voz en off | Texto en pantalla | Visual | Duración aprox. |
|---|---|---|---|---|

- Se guarda en `guion/guion_vN.md`.
- **Entrega:** borrador del guion. → aprobación.

## Etapa 2: voz

- Voz de la marca si existe. Si no, se proponen 2 o 3 voces de ElevenLabs con una muestra corta de la primera frase.
- Se genera la voz completa por escenas (un archivo por escena facilita retocar solo una) en `audio/voz/`.
- Mezcla de idiomas: revisar pronunciación de los términos en el otro idioma; si falla, ajustar ortografía fonética o separar el fragmento.
- **Entrega:** audio de la voz. → aprobación.
- Después de aprobar: transcribir la voz con AssemblyAI para obtener tiempos por palabra. Se guarda en `audio/voz/transcripcion.json`. Las animaciones se sincronizan con estos tiempos.

## Etapa 3: storyboard

- Se escribe el código de render del vídeo en `codigo/` y con él se generan fotogramas clave: al menos uno por escena, en la resolución final.
- Se preguntan los subtítulos (tipo y estilo) si no se decidieron.
- Música: se generan 1 o 2 opciones con ElevenLabs con la duración del vídeo. Efectos de sonido: lista de dónde irían.
- **Entrega (revisión detallada):** fotogramas clave, opciones de música y la lista de efectos. → aprobación.

## Etapa 4: render

- Render completo con el mismo código del storyboard.
- Mezcla de audio: voz por encima, música atenuada bajo la voz, efectos; normalizar a -14 LUFS.
- Verificaciones de [reglas-tecnicas.md](reglas-tecnicas.md#verificación-antes-de-entregar).
- **Entrega:** `final/<id>_vN.mp4`. Si hay ajustes, se corrige y se entrega una versión nueva.

## Etapa 5: cierre

Ver [reglas-tecnicas.md](reglas-tecnicas.md#cierre-de-proyecto). Ofrecer convertirlo en receta si el usuario quiere repetirlo.
