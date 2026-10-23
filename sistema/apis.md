# APIs: AssemblyAI y ElevenLabs

Las keys se leen de `.env` (`ASSEMBLYAI_API_KEY`, `ELEVENLABS_API_KEY`). Nunca se imprimen ni se escriben en otros archivos.

**Siempre `load_dotenv(..., override=True)`.** El `~/.zshrc` del usuario exporta una `ASSEMBLYAI_API_KEY` antigua y deshabilitada. Sin `override`, Python usa esa y no la de `.env` (causó un 401 "API key is disabled" el 2026-10-23). En bash: `set -a && . ./.env && set +a`.

Uso de créditos: libre dentro de cada etapa aprobada. Cada generación se registra en `proyecto.md` (modelo, voz, prompt, duración) para poder repetirla.

Los detalles marcados con **⚠ verificar** se comprobaron en la documentación (octubre de 2026) pero aún no en una llamada real. Al confirmarlos en el primer proyecto, quitar la marca.

## AssemblyAI (transcripción)

Base: `https://api.assemblyai.com` · Cabecera: `authorization: <key>`

Para comprobar que la key funciona, subir un archivo pequeño a `/v2/upload`. `GET /v2/transcript` puede responder 200 con una key deshabilitada (pasó el 2026-10-23).

1. **Subir archivo local:** `POST /v2/upload` con los bytes del archivo en el cuerpo → devuelve `upload_url`. Subir audio extraído (WAV o M4A), no el vídeo completo.
2. **Crear transcripción:** `POST /v2/transcript` con JSON:
   ```json
   {
     "audio_url": "<upload_url>",
     "speech_models": ["universal-3-5-pro"],
     "language_codes": ["es", "en"],
     "speaker_labels": true
   }
   ```
   - Un solo idioma conocido: `"language_code": "es"`.
   - Mezcla español-inglés: `"language_codes": ["es", "en"]` o `"language_detection": true`. `language_codes` es incompatible con `language_code` y `language_detection`. Verificado el 2026-10-23 con `language_codes: ["es","en"]`: transcribió sin errores "Premiere", "After Effects", "workflow" y "motion graphics" dentro de frases en español. Escribe "video" sin tilde.
   - `speaker_labels`: solo si hay varias personas.
   - `prompt`: descripción breve del audio en frases completas. `keyterms_prompt`: lista de nombres propios y términos técnicos. En Universal-3.5 Pro no se pueden usar los dos en la misma petición.
3. **Consultar:** `GET /v2/transcript/{id}` hasta que `status` sea `completed` o `error`.
4. **Resultado:** `words` trae cada palabra con `start` y `end` en milisegundos, `confidence` y `speaker`. Guardar el JSON completo en el proyecto.

**Muletillas ("eh", "este", "um"):** por defecto se eliminan del texto. Para la edición tipo 2 hacen falta. Opciones: parámetro `disfluencies: true` o pedirlo en el `prompt`. **⚠ verificar** cuál funciona con `universal-3-5-pro` en español.

## ElevenLabs

Base: `https://api.elevenlabs.io` · Cabecera: `xi-api-key: <key>`

### Voz (texto a voz)
- `POST /v1/text-to-speech/{voice_id}` con `{"text": "...", "model_id": "..."}`. Parámetro de consulta `output_format` (por defecto `mp3_44100_128`).
- Listar voces: `GET /v2/voices`.
- Modelos:
  - `eleven_v4`: máxima calidad y expresividad, 90+ idiomas, mantiene la voz al cambiar de idioma. **Opción por defecto.**
  - `eleven_multilingual_v2`: el más estable en textos largos, también mantiene la voz entre idiomas.
  - `eleven_v3`: expresivo y dramático, 70+ idiomas.
  - `eleven_flash_v2_5`: rápido y barato, para pruebas.
- `voice_settings.speed` (0,7 a 1,2) apenas cambió la duración con `eleven_v4` y un clon profesional (1,12 → misma duración). Para ajustar la duración, recortar el texto o las pausas.
- Referencia de ritmo (clon "Sebastian PArra", `eleven_v4`): unas 25 palabras ≈ 11,8 s. Calcular unas 2,1 palabras por segundo al escribir guiones con duración fija.

### Música
- `POST /v1/music` con `{"prompt": "...", "music_length_ms": 30000, "model_id": "music_v2_5", "force_instrumental": true}`.
- Duración: 3.000 a 600.000 ms. `force_instrumental: true` cuando va bajo voz en off.

### Efectos de sonido
- `POST /v1/sound-generation` con `{"text": "...", "duration_seconds": 1.5, "prompt_influence": 0.5}`.
- `duration_seconds`: 0,5 a 30 (si se omite, lo decide el modelo). `prompt_influence`: 0 a 1 (más alto = más fiel al texto). `loop: true` para sonidos en bucle.
- Modelos: `eleven_text_to_sound_v2` (por defecto) o `eleven_text_to_sound_v3`.

### Aislador de voz
- `POST /v1/audio-isolation`, `multipart/form-data` con el campo `audio`. Devuelve el audio con la voz aislada.
- Para audio sucio (eco, calle, ventilador). Para ruido leve bastan los filtros de FFmpeg.
- **⚠ verificar** los límites de duración y tamaño del archivo.
