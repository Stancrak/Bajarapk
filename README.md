# Video URL Resolver API

API FastAPI para resolver URLs directas de videos de YouTube, Facebook, Instagram, TikTok y otros sitios sin descargar contenido al servidor.

## 🚀 Características

- **Sin descarga en servidor**: Usa `yt-dlp` en modo simulación
- **Múltiples plataformas**: YouTube, Facebook, Instagram, TikTok, etc.
- **CORS habilitado**: Listo para apps móviles
- **Despliegue en Render**: Configuración incluida para Free Tier

## 📋 Requisitos

- Python 3.11+
- Cuenta en Render.com
- Cuenta en GitHub

## 🔧 Instalación Local

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
python main.py
```

El servidor estará disponible en: `http://localhost:8000`

## 📡 Endpoints

### `GET /`

Información general de la API

### `GET /health`

Health check del servicio

### `POST /resolve`

Resuelve la URL directa de un video

**Request:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response (Success):**

```json
{
  "status": "success",
  "data": {
    "title": "Título del video",
    "thumbnail": "https://...",
    "duration": 213,
    "stream_url": "https://direct-url-to-video..."
  }
}
```

**Response (Error):**

```json
{
  "status": "error",
  "message": "Descripción del error"
}
```

## 🌐 Desplegar en Render

### Paso 1: Crear repositorio en GitHub

1. Ve a [GitHub](https://github.com) e inicia sesión
2. Click en el botón `+` arriba a la derecha → `New repository`
3. Nombre del repositorio: `video-url-resolver` (o el que prefieras)
4. Marca como **Público** (requerido para Render Free Tier)
5. Click en `Create repository`

### Paso 2: Subir código al repositorio

Abre tu terminal en la carpeta del proyecto y ejecuta:

```bash
# Inicializar git
git init

# Agregar todos los archivos
git add .

# Crear primer commit
git commit -m "Initial commit: FastAPI video URL resolver"

# Conectar con tu repositorio remoto (reemplaza con tu URL)
git remote add origin https://github.com/TU_USUARIO/video-url-resolver.git

# Subir el código
git branch -M main
git push -u origin main
```

### Paso 3: Conectar con Render

1. Ve a [Render.com](https://render.com) y crea una cuenta (puedes usar GitHub)
2. En el Dashboard, click en `New +` → `Blueprint`
3. Conecta tu repositorio de GitHub
4. Render detectará automáticamente el `render.yaml`
5. Click en `Apply` para crear el servicio
6. Espera a que el despliegue termine (5-10 minutos)

### Paso 4: Obtener tu URL de producción

Una vez desplegado, Render te dará una URL como:

```
https://video-url-resolver-xxxx.onrender.com
```

## 🧪 Probar la API

Puedes probar la API con curl:

```bash
curl -X POST "https://tu-app.onrender.com/resolve" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

O desde tu app móvil:

```javascript
fetch("https://tu-app.onrender.com/resolve", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  }),
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## ⚠️ Importante

- **Free Tier de Render**: El servicio se "duerme" después de 15 minutos de inactividad. La primera petición después de dormir puede tardar 30-60 segundos.
- **URLs temporales**: Las URLs directas (`stream_url`) pueden expirar después de unas horas. Tu app móvil debe usarlas inmediatamente.
- **Rate limiting**: yt-dlp puede tener límites según la plataforma. Considera implementar caché si tienes mucho tráfico.

## 📝 Licencia

MIT
