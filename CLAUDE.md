# Asistente de edición de vídeo

Este proyecto es un sistema de trabajo, no una aplicación. Claude ejecuta cada paso directamente (escribe y corre código, llama a las APIs, revisa resultados) siguiendo los documentos de este repositorio. Nunca se construye software que funcione solo.

Idioma de trabajo con el usuario: español.

## Al empezar cada sesión

1. Leer [sistema/preferencias-y-lecciones.md](sistema/preferencias-y-lecciones.md).
2. Si el usuario retoma un proyecto, leer su `proyectos/<id>/proyecto.md` y continuar desde la etapa que indica.
3. Si es un proyecto nuevo, seguir [sistema/protocolo-arranque.md](sistema/protocolo-arranque.md).

## Reglas que no se rompen

1. **Vídeo solo con código propio.** Python + FFmpeg + librerías puntuales (detalle en [sistema/reglas-tecnicas.md](sistema/reglas-tecnicas.md)). Prohibido usar Remotion, Hyperframes, MoviePy o cualquier framework de vídeo.
2. **No usar skills de vídeo instaladas en el entorno**, aunque la petición parezca encajar: `hyperframes`, `hyperframes-*`, `general-video`, `motion-graphics`, `faceless-explainer`, `embedded-captions`, `talking-head-recut`, `music-to-video`, `media-use`, `product-launch-video`, `website-to-video`, `pr-to-video`, `slideshow`, `figma`, `remotion-to-hyperframes`. Tampoco generadores de imagen o vídeo (fal u otros) salvo que el usuario lo pida expresamente.
3. **Servicios fijos.** Transcripción: AssemblyAI. Voz, música, efectos de sonido y aislamiento de voz: ElevenLabs. Las keys están en `.env` ([sistema/apis.md](sistema/apis.md)).
4. **El material original nunca se modifica.** Todo lo que está en `crudo/` es de solo lectura.
5. **Aprobación por etapas.** No se avanza a la siguiente etapa sin el visto bueno explícito del usuario.
6. **Preguntar en vez de asumir.** Si una instrucción del proyecto falta, se pregunta. El tipo de subtítulos se pregunta siempre.
7. **Aprender de cada corrección.** Cuando el usuario corrige algo, se guarda automáticamente: en la ficha de la marca si es de una marca, o en `sistema/preferencias-y-lecciones.md` si es general.

## Tipos de proyecto

- **Tipo 1, generado:** vídeo de motion graphics creado desde cero (tipografía, formas, gráficos, datos, logos). Flujo en [sistema/flujo-tipo1-generado.md](sistema/flujo-tipo1-generado.md).
- **Tipo 2, edición:** el usuario entrega material crudo para editar. Flujo en [sistema/flujo-tipo2-edicion.md](sistema/flujo-tipo2-edicion.md).

## Mapa del repositorio

| Carpeta | Para qué |
|---|---|
| `sistema/` | Cómo se trabaja: protocolo, flujos, reglas técnicas, APIs, lecciones |
| `marcas/` | Una carpeta por marca. `_plantilla/` es el molde. Todo es opcional |
| `recetas/` | Recetas globales reutilizables. Las de una sola marca viven en `marcas/<marca>/recetas/` |
| `catalogos/` | Menús visuales de estilos (subtítulos, títulos, transiciones) para elegir rápido |
| `herramientas/` | Fragmentos de código ya probados en proyectos reales, para reutilizar |
| `proyectos/` | Un proyecto por carpeta: `AAAA-MM-DD_<marca o libre>_<nombre>`. `_plantilla/` es el molde |

## Entregas y revisiones

- Cada borrador se deja en `proyectos/<id>/borradores/` **y** se envía al usuario en la conversación (SendUserFile).
- Etapas de corte (tipo 2): resumen rápido para aprobar en un vistazo. Etapas visuales y de diseño: revisión detallada.
- Uso de créditos de APIs: libre dentro de cada etapa aprobada.
