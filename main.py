from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import yt_dlp
from typing import Optional
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video URL Resolver API",
    description="API para resolver URLs directas de videos de YouTube, Facebook, Instagram, TikTok",
    version="1.0.0"
)

# Configuración de CORS - Permite todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos
class VideoRequest(BaseModel):
    url: str

class VideoData(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    stream_url: str

class VideoResponse(BaseModel):
    status: str
    data: Optional[VideoData] = None
    message: Optional[str] = None

# Configuración de yt-dlp
def get_ydl_opts():
    return {
        'format': 'best',  # Mejor calidad disponible
        'quiet': True,  # No muestra logs excesivos
        'simulate': True,  # CRÍTICO: No descarga el video
        'force_url': True,  # Fuerza obtener URL directa
        'noplaylist': True,  # Solo el video individual
        'no_warnings': True,  # Suprime warnings
        'extract_flat': False,  # Extrae información completa
        'socket_timeout': 10,  # Timeout de 10 segundos
    }

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Video URL Resolver API",
        "version": "1.0.0",
        "endpoints": {
            "resolve": "POST /resolve - Resuelve URLs de video",
            "health": "GET /health - Estado de salud del servicio"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo"""
    return {"status": "healthy", "service": "video-resolver"}

@app.post("/resolve", response_model=VideoResponse)
async def resolve_video_url(request: VideoRequest):
    """
    Resuelve la URL directa de un video sin descargarlo.
    
    Soporta: YouTube, Facebook, Instagram, TikTok y muchos otros sitios.
    
    Args:
        request: Objeto con la URL del video
        
    Returns:
        VideoResponse con los metadatos y URL directa
    """
    try:
        logger.info(f"Procesando URL: {request.url}")
        
        ydl_opts = get_ydl_opts()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrae información sin descargar
            info = ydl.extract_info(request.url, download=False)
            
            # Obtiene la URL directa del video
            stream_url = None
            if 'url' in info:
                stream_url = info['url']
            elif 'formats' in info and len(info['formats']) > 0:
                # Busca el mejor formato con URL
                for fmt in reversed(info['formats']):
                    if fmt.get('url'):
                        stream_url = fmt['url']
                        break
            
            if not stream_url:
                raise HTTPException(
                    status_code=400,
                    detail="No se pudo obtener la URL directa del video"
                )
            
            # Construye la respuesta
            video_data = VideoData(
                title=info.get('title', 'Sin título'),
                thumbnail=info.get('thumbnail'),
                duration=info.get('duration'),
                stream_url=stream_url
            )
            
            logger.info(f"URL resuelta exitosamente: {info.get('title')}")
            
            return VideoResponse(
                status="success",
                data=video_data
            )
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Error de yt-dlp: {str(e)}")
        return VideoResponse(
            status="error",
            message=f"No se pudo procesar la URL: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return VideoResponse(
            status="error",
            message=f"Error interno del servidor: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
