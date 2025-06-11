# ASR Service PoC

**Objetivo:**  
- Frontend en Next.js para subir y reproducir audio y mostrar la transcripción.  
- Backend en Django + DRF que llame al modelo `mdmev/whisper-small-hi`.  
- Ambos servicios en Docker y desplegados en Cloud Run.

**Estructura inicial**  
- /frontend    → Next.js  
- /backend     → Django + DRF