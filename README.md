# Matriz de Atributos

## Descripción

Proyecto de extracción automática de atributos de productos a partir de imágenes de categorías de ropa y muebles utilizando IA generativa (Google Gemini).

## Características

- **Extracción automática de atributos**: Analiza imágenes de productos y extrae características relevantes como color, material, estilo, etc.
- **Almacenamiento flexible**: Soporte para CSV local y Google Sheets
- **Procesamiento por lotes**: Maneja múltiples imágenes de forma secuencial con reintentos automáticos
- **Resistente a errores**: Sistema de reintentos con backoff exponencial para llamadas a la API
- **Reanudación automática**: Detecta productos ya procesados y continúa desde donde se quedó
- **Generador de productos**: Crea catálogos de ejemplo realistas para testing
- **Scraper incluido**: Extrae productos de sitios web (con limitaciones)

## Categor�as Soportadas

- Ropa (beb�s, adultos, etc.)
- Muebles
- Accesorios

## Archivos del Proyecto

### Extracción de Atributos
- **extraccion_optimizada.ipynb**: Notebook optimizado con extracción a CSV (RECOMENDADO)
- **extraccion-atributos.ipynb**: Notebook original con Google Sheets
- **prompt_api.txt**: Prompt actual optimizado para extracción
- **prompt_api anterior.txt**: Versión anterior del prompt (referencia)

### Generación de Datos
- **generar_productos_ejemplo.py**: Genera catálogos de productos realistas
- **scraper_coppel.py**: Scraper para sitios web (experimental)
- **productos.csv**: CSV de productos generado

### Documentación
- **GUIA_USO.md**: Guía completa de uso del sistema
- **README_SCRAPER.md**: Documentación del scraper y generador
- **pyproject.toml**: Configuración del proyecto y dependencias

## Requisitos

- Python >= 3.9
- API Key de Google Gemini
- Imágenes de productos en formato JPG/PNG

## Inicio Rápido

### 1. Instalación

```bash
# Instalar dependencias básicas
uv sync

# Instalar con Jupyter para notebooks
uv sync --extra dev
```

### 2. Configuración

```bash
# Copiar y configurar .env
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY
```

### 3. Generar Catálogo de Ejemplo

```bash
# Generar 30 productos de ejemplo
uv run python generar_productos_ejemplo.py
```

### 4. Ejecutar Extracción

```bash
# Abrir notebook optimizado
uv run jupyter notebook extraccion_optimizada.ipynb
```

## Dependencias Principales

- **google-generativeai**: API de Gemini
- **pandas**: Procesamiento de datos
- **tqdm**: Barras de progreso
- **requests**: Scraping web
- **beautifulsoup4**: Parsing HTML

## Flujos de Trabajo

### Flujo Recomendado (CSV Local)

1. Genera productos de ejemplo o usa tu propio CSV
2. Coloca imágenes en carpeta `images/`
3. Configura tu API key de Gemini
4. Ejecuta `extraccion_optimizada.ipynb`
5. Obtén `productos_con_atributos.csv`

### Flujo Original (Google Sheets)

1. Configura credenciales OAuth de Google
2. Prepara Google Sheet con productos
3. Ejecuta `extraccion-atributos.ipynb`
4. Los resultados se guardan en Sheets

## Documentación Detallada

- **[GUIA_USO.md](GUIA_USO.md)**: Guía completa del sistema de extracción
- **[README_SCRAPER.md](README_SCRAPER.md)**: Guía del generador y scraper
- **Análisis de prompts**: Ver sección de comparación en este README

## Características Avanzadas

### Generador de Productos

Crea catálogos realistas con:
- 6 categorías de productos (Conjunto, Vestido, Pantalón, etc.)
- Atributos realistas basados en Coppel
- Distribución balanceada de géneros, colores, etc.

### Scraper Web

Extrae productos de sitios web:
- Manejo de JSON-LD y Next.js
- Descarga automática de imágenes
- Fallback a HTML parsing

### Sistema de Extracción

- Reintentos automáticos con backoff exponencial
- Guardado incremental
- Análisis de resultados incluido
- Logging detallado
