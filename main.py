from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
from typing import Optional
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video URL Resolver API",
    description="API para resolver URLs directas de videos de YouTube, Facebook, Instagram, TikTok",
    version="2.0.0"
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
    title: Optional[str] = "Sin título"
    thumbnail: Optional[str] = None
    duration: Optional[float] = None  # Acepta decimales para Instagram
    stream_url: str

class VideoResponse(BaseModel):
    status: str
    data: Optional[VideoData] = None
    message: Optional[str] = None

# Configuración de yt-dlp optimizada para evasión de bloqueos
def get_ydl_opts():
    return {
        'format': 'best',  # Intenta obtener la mejor calidad
        'quiet': True,
        'no_warnings': True,
        'simulate': True,  # No descargar al disco del servidor
        'force_url': True,  # Solo queremos la URL
        'noplaylist': True,
        'socket_timeout': 30,  # Timeout aumentado para TikTok
        'retries': 3,  # Reintentar 3 veces si falla
        'age_limit': None,
        'geo_bypass': True,
        # Evasión de Bloqueos:
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android_creator', 'android', 'ios'],
                'player_skip': ['webpage', 'configs', 'js'],
                'skip': ['hls', 'dash', 'translated_subs'],
            },
            'instagram': {
                'skip_hls': True,
            },
            'tiktok': {
                'api_hostname': 'api22-normal-c-useast2a.tiktokv.com',
                'app_version': '34.1.2',
                'manifest_app_version': '2023401020',
            },
            'twitter': {
                'api': 'syndication',
            },
            'reddit': {
                'skip_hls': True,
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': '*/*',
        }
    }

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Video URL Resolver API",
        "version": "2.0.0",
        "status": "online",
        "endpoints": {
            "resolve": "POST /resolve - Resuelve URLs de video",
            "health": "GET /health - Estado de salud del servicio"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo"""
    return {"status": "healthy", "service": "video-resolver", "version": "2.0.0"}

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
            
            if not info:
                raise HTTPException(
                    status_code=400,
                    detail="No se pudo extraer información del video"
                )
            
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
            
            # Construye la respuesta con manejo seguro de campos opcionales
            video_data = VideoData(
                title=info.get('title', 'Sin título'),
                thumbnail=info.get('thumbnail'),
                duration=float(info['duration']) if info.get('duration') is not None else None,
                stream_url=stream_url
            )
            
            logger.info(f"URL resuelta exitosamente: {video_data.title}")
            
            return VideoResponse(
                status="success",
                data=video_data
            )
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        logger.error(f"Error de yt-dlp: {error_msg}")
        return VideoResponse(
            status="error",
            message=f"No se pudo procesar la URL: {error_msg}"
        )
    except HTTPException as e:
        # Re-lanzar excepciones HTTP de FastAPI
        raise e
    except Exception as e:
        # Captura cualquier otro error inesperado
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return VideoResponse(
            status="error",
            message=f"Error interno del servidor: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
