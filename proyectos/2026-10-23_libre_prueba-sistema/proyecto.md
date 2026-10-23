# Proyecto: prueba del sistema

- **ID:** 2026-10-23_libre_prueba-sistema
- **Tipo:** 1 (generado)
- **Marca:** libre
- **Receta:** ninguna
- **Estado:** en curso

## Brief

- **Objetivo y público:** prueba de punta a punta del sistema; mostrar al máximo la capacidad de motion graphics hecha con código. Tema: "edito vídeos con IA sin tocar un editor".
- **Plataforma y formato:** 9:16 vertical (reels)
- **Duración objetivo:** 10 s
- **Idioma(s):** español con términos en inglés (prueba de mezcla de idiomas)
- **Subtítulos:** tipo b, bloques de 2-4 palabras grandes y centrados que entran con rebote
- **Exportación:** estándar (1080×1920, H.264, 30 fps, -14 LUFS)
- **Otras instrucciones:**
  - Estilo visual 1, oscuro tech: fondo casi negro, acento eléctrico, Neue Montreal y SF Mono, movimientos precisos.
  - Efectos **muy agresivos**: mostrar el máximo de capacidad en motion graphics.
  - Guion escrito por Claude. Voz: clon "Sebastian PArra" (`7bmVaeToqOpy05SKlvVj`), propuesta por defecto sin objeción.
  - Música instrumental electrónica moderna; efectos de sonido acordes con el estilo agresivo.

## Etapas

| Etapa | Estado | Aprobado el | Notas |
|---|---|---|---|
| 1. Guion | aprobado | 2026-10-23 | `guion/guion_v1.md` |
| 2. Voz | aprobado | 2026-10-23 | `audio/voz/voz_v4.mp3` (11,8 s). Tiempos por palabra en `audio/voz/transcripcion.json` |
| 3. Storyboard | en revisión | | `guion/storyboard_v1.md`, `borradores/storyboard_v1.png`, vistas previas con música A y B |
| 4. Render | pendiente | | |
| 5. Cierre | pendiente | | |

## Generaciones de API

| Fecha | Servicio | Modelo / voz | Prompt o texto | Archivo |
|---|---|---|---|---|
| 2026-10-23 | ElevenLabs TTS | eleven_v4 / Sebastian PArra | guion v1 completo | `audio/voz/voz_v4.mp3` (11,8 s) |
| 2026-10-23 | ElevenLabs TTS | eleven_multilingual_v2 / Sebastian PArra | guion v1 completo | `audio/voz/voz_multilingual_v2.mp3` (12,9 s) |
| 2026-10-23 | ElevenLabs TTS | eleven_v4, speed 1.12 | guion v1 completo | descartada: duró igual (11,9 s) |
| 2026-10-23 | AssemblyAI | universal-3-5-pro | transcripción de las tomas | falló: 401 "API key is disabled" (se usaba la key vieja del shell) |
| 2026-10-23 | AssemblyAI | universal-3-5-pro, language_codes es+en | voz_v4.mp3 | `audio/voz/transcripcion.json`: texto exacto |
| 2026-10-23 | ElevenLabs Music | music_v2_5, 12,5 s, instrumental | "Dark aggressive cyberpunk electronic, 128 BPM, punchy distorted kick…" | `audio/musica/musica_A.mp3` |
| 2026-10-23 | ElevenLabs Music | music_v2_5, 12,5 s, instrumental | "Hard-hitting dark trap and electronic hybrid, 140 BPM, deep 808…" | `audio/musica/musica_B.mp3` |

## Decisiones y cambios

- 2026-10-23: brief confirmado. El usuario redujo la duración de 15 s a 10 s y pidió efectos agresivos.
- 2026-10-23: los bloques de subtítulos son la tipografía principal; no hay texto en pantalla aparte, para no duplicar.
- 2026-10-23: voz v4 aprobada; el usuario acepta extender la duración a unos 12 s (voz de 11,8 s).
