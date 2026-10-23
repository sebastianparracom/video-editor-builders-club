# Protocolo de arranque de proyecto

Se sigue siempre que el usuario pide un vídeo nuevo. El objetivo es no olvidar nada y no asumir nada.

## 1. Leer lo que ya se sabe

- `sistema/preferencias-y-lecciones.md`
- Si hay marca: `marcas/<marca>/marca.md` y sus recetas.
- Si el usuario menciona una receta ("como el de la semana pasada", "el formato de tips"): leer esa receta.

## 2. Preguntar lo que falte

Solo se pregunta lo que la petición, la marca o la receta no respondan ya. Las preguntas se agrupan en un solo mensaje, con opciones concretas cuando sea posible.

**Siempre**
- [ ] Tipo de proyecto: 1 (generado) o 2 (edición)
- [ ] Marca o libre
- [ ] Objetivo y público del vídeo (para qué sirve, quién lo ve)
- [ ] Plataforma(s) y formato: 9:16, 16:9, 1:1, 4:5. ¿Varios formatos del mismo vídeo?
- [ ] Duración objetivo
- [ ] Idioma(s): español, inglés o mezcla. Si es español, qué variante
- [ ] Subtítulos: si lleva y de qué tipo (mostrar `catalogos/subtitulos/` si tiene entradas)
- [ ] Calidad de exportación: confirmar el estándar (1080p, H.264, 30 fps, -14 LUFS) o cambiarlo

**Tipo 1 (generado)**
- [ ] ¿El guion lo da el usuario o lo escribo yo? Si lo escribo: tema, mensajes clave, llamada a la acción
- [ ] Voz en off: ¿lleva? ¿qué voz? (de la marca, o propongo opciones)
- [ ] Música: ¿lleva? ¿qué estilo o energía?
- [ ] Efectos de sonido: ¿sí o no?
- [ ] Estilo visual si es libre: referencias, paleta, tipografía, ritmo
- [ ] Vídeos de referencia, si los hay

**Tipo 2 (edición)**
- [ ] Qué hay en `crudo/` y qué es cada archivo (si no es evidente)
- [ ] Qué ediciones se necesitan: cortes de silencios y muletillas, mejor toma, clips de un vídeo largo, reencuadre, limpieza de audio, color, gráficos, b-roll, música, efectos
- [ ] Qué no se puede cortar (frases clave, momentos obligatorios)
- [ ] Si son clips de un vídeo largo: cuántos, de qué duración y con qué criterio

## 3. Crear el proyecto

1. Copiar `proyectos/_plantilla/` a `proyectos/AAAA-MM-DD_<marca o libre>_<nombre-corto>/` (minúsculas, guiones, sin tildes).
2. Rellenar `proyecto.md` con el brief y las respuestas.
3. Tipo 2: pedir al usuario que deje el material en `crudo/` (o moverlo allí si lo dio en otra ruta y él lo aprueba).
4. Arrancar la etapa 1 del flujo correspondiente.
