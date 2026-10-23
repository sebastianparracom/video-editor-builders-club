# Proyecto: Teleprompter con errores

- **ID:** 2026-10-23_libre_teleprompter-errores
- **Tipo:** 2 (edición)
- **Marca:** libre
- **Receta:** —
- **Estado:** en curso

## Brief

- **Objetivo y público:** pendiente
- **Plataforma y formato:** 16:9, 1920×1080
- **Duración objetivo:** la que salga tras quitar errores
- **Idioma(s):** español
- **Subtítulos:** frases clásicas abajo, una línea, blanco con borde y sombra (SF Pro del sistema), texto tal como se dice
- **Exportación:** estándar (1080p, H.264, 30 fps, -14 LUFS); antes, preview en baja resolución
- **Otras instrucciones:** corregir los errores de lectura según el guion; añadir subtítulos; solo zooms naturales para dinamismo, nada más.

## Etapas

| Etapa | Estado | Aprobado el | Notas |
|---|---|---|---|
| 0. Ingesta | hecha | | transcripción con `disfluencies` + prompt: muletillas incluidas |
| 1. Guion de corte | aprobado | 2026-10-23 | guion/corte_v1.md |
| 2+3. Preview baja resolución (corte + zooms + subtítulos) | en revisión | | borradores/preview_v1.mp4, codigo/editar.py |
| 4. Render final | pendiente | | |
| 5. Cierre | pendiente | | |

## Material (tipo 2)

| Archivo | Resolución | fps | Duración | Códec | Notas |
|---|---|---|---|---|---|
| crudo/grabacion.mp4 | 1920×1080 | 30 | 41,0 s | H.264 / AAC 48 kHz estéreo | Copia de Grabaciones OBS/2026-10-23 15-25-51.mp4. Plano medio fijo, mirada a cámara |

## Generaciones de API

| Fecha | Servicio | Modelo / voz | Prompt o texto | Archivo |
|---|---|---|---|---|
| 2026-10-23 | AssemblyAI | universal-3-5-pro, disfluencies:true + prompt de literalidad | — | audio/transcripcion.json |

## Decisiones y cambios

- 2026-10-23: guion original recibido (guion/guion_original.md). El corte v1 lo cubre entero; única diferencia: en la grabación falta la "y" de "natural y sentirme".
- 2026-10-23: el usuario eligió subtítulos clásicos abajo, 16:9 y exportación estándar, y pidió un preview en baja resolución antes del render final. Corte, zooms y subtítulos se revisan juntos en un único preview (960×540).
