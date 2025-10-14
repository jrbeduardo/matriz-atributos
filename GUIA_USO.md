# Guía de Uso - Extracción Optimizada de Atributos

## Inicio Rápido

### 1. Instalación de Dependencias

```bash
# Instalar dependencias principales
uv sync

# Instalar dependencias de desarrollo (Jupyter)
uv sync --extra dev
```

### 2. Configuración

#### 2.1 API Key de Gemini

1. Obtén tu API key en: https://aistudio.google.com/app/apikey
2. Copia el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```
3. Edita `.env` y agrega tu API key:
   ```
   GEMINI_API_KEY=tu_api_key_real
   ```

#### 2.2 Estructura de Archivos

```
matriz-atributos/
├── images/                          # Carpeta con tus imágenes
│   ├── producto001.jpg
│   ├── producto002.jpg
│   └── ...
├── productos.csv                    # CSV de entrada
├── prompt_api.txt                   # Tu prompt de extracción
├── extraccion_optimizada.ipynb      # Notebook principal
└── .env                             # Tu API key (NO SUBIR A GIT)
```

### 3. Preparar CSV de Entrada

Tu archivo `productos.csv` debe tener estas columnas mínimas:

- `id`: Identificador único del producto
- `image`: Nombre del archivo de imagen (debe existir en carpeta `images/`)
- Otras columnas opcionales con metadatos del producto

**Ejemplo:**

```csv
id,image,Color,Género,Tipo de producto
PROD001,camisa_azul.jpg,Azul,Unisex,Playera
PROD002,pantalon_gris.jpg,Gris,Niño,Pantalón
```

### 4. Ejecutar la Extracción

#### Opción A: Usar Jupyter Notebook (Recomendado)

```bash
# Iniciar Jupyter
uv run jupyter notebook

# Abrir: extraccion_optimizada.ipynb
# Ejecutar todas las celdas
```

#### Opción B: Desde Terminal

```bash
# Ejecutar el notebook completo
uv run jupyter nbconvert --to notebook --execute extraccion_optimizada.ipynb
```

## Configuración Avanzada

### Personalizar Rutas

Edita la clase `Config` en el notebook:

```python
class Config:
    PROMPT_FILE = Path('mi_prompt_personalizado.txt')
    IMAGE_DIRECTORY = Path('mis_imagenes')
    INPUT_CSV = Path('mi_catalogo.csv')
    OUTPUT_CSV = Path('resultados.csv')

    # Modelo de Gemini
    GEMINI_MODEL = 'gemini-2.0-flash-exp'  # Más rápido
    # O usar: 'gemini-2.5-flash' para mejor calidad

    # Configuración de reintentos
    MAX_RETRIES = 5
    BASE_DELAY = 5
    RATE_LIMIT_DELAY = 1.5  # Segundos entre llamadas
```

### Cambiar Nombres de Columnas

Si tu CSV usa nombres diferentes:

```python
class Config:
    ID_COLUMN = 'sku'              # En lugar de 'id'
    IMAGE_COLUMN = 'foto'          # En lugar de 'image'
    ATTRIBUTES_COLUMN = 'attrs'    # En lugar de 'gemini_attributes'
```

## Características Principales

### 1. Reanudación Automática

El notebook guarda el progreso automáticamente. Si se interrumpe:

- Los productos ya procesados se saltan automáticamente
- Solo procesa productos nuevos o con errores fatales
- Puedes detener y reanudar en cualquier momento

### 2. Manejo Inteligente de Errores

**Tipos de error:**

- `ERROR_IMAGEN`: Imagen no encontrada
- `ERROR_LECTURA`: No se pudo leer la imagen
- `ERROR_API_FATAL`: Error de API después de 5 intentos
- `ERROR_SIN_IMAGEN`: Fila sin nombre de imagen

**Reprocesar errores:**

```python
# En el notebook, ejecutar:
df_result = reprocess_errors(df_result)
```

### 3. Guardado Incremental

Por defecto, guarda después de cada producto procesado. Para cambiar:

```python
# Guardar cada 10 productos
df_result = run_extraction(save_every=10)
```

### 4. Barra de Progreso

Muestra en tiempo real:
- Productos procesados
- Tiempo estimado restante
- Velocidad de procesamiento

### 5. Logging Detallado

Los logs se guardan en:
- **Consola**: Información en tiempo real
- **Archivo**: `extraccion_atributos.log`

Niveles de log:
```
INFO  - Procesamiento normal
WARNING - Advertencias (imagen no encontrada, etc.)
ERROR - Errores recuperables
```

## Análisis de Resultados

### Ver Estadísticas

El notebook incluye una sección de análisis que muestra:

```
📊 ESTADÍSTICAS DE PROCESAMIENTO
====================================
Total de productos: 100
✅ Procesados exitosamente: 92 (92.0%)
❌ Con errores: 5 (5.0%)
⏳ Pendientes: 3 (3.0%)

🔍 TIPOS DE ERRORES:
  ERROR_IMAGEN: 3
  ERROR_API_FATAL: 2
```

### Exportar Resultados Limpios

Automáticamente exporta `productos_limpios.csv` sin errores:

```python
# Solo productos con atributos exitosos
df_clean = df_result[~df_result['gemini_attributes'].str.startswith('ERROR')]
```

### Verificar Imágenes Faltantes

```python
# Encuentra qué imágenes no existen
missing_images = check_missing_images(df_result, config.IMAGE_DIRECTORY)
print(missing_images)
```

## Mejores Prácticas

### 1. Organización de Imágenes

```bash
# Renombrar imágenes con nombres consistentes
images/
├── PROD001.jpg
├── PROD002.jpg
└── PROD003.jpg
```

### 2. Validar CSV Antes de Procesar

```python
# En el notebook, verificar estructura
df = pd.read_csv('productos.csv')
print(df.columns)
print(df.head())
```

### 3. Probar con Muestra Pequeña

```python
# Procesar solo primeros 5 productos para probar
df_test = df.head(5)
df_test.to_csv('productos_test.csv', index=False)

# Luego ejecutar con productos_test.csv
```

### 4. Optimizar Costo de API

```python
# Usar modelo más rápido y económico
GEMINI_MODEL = 'gemini-2.0-flash-exp'

# Aumentar delay para evitar rate limits
RATE_LIMIT_DELAY = 2.0
```

### 5. Backup Regular

```bash
# Hacer backup del CSV de salida
cp productos_con_atributos.csv productos_backup_$(date +%Y%m%d).csv
```

## Solución de Problemas

### Error: "GEMINI_API_KEY not found"

```bash
# Verificar que .env existe
cat .env

# Si no existe, crearlo
cp .env.example .env
# Editar y agregar tu API key
```

### Error: "File not found: productos.csv"

```bash
# Crear CSV de ejemplo o copiar el tuyo
cp productos_ejemplo.csv productos.csv
```

### Error: Rate Limit Exceeded

```python
# Aumentar el delay entre llamadas
config.RATE_LIMIT_DELAY = 3.0  # 3 segundos
```

### Imágenes no se Encuentran

```python
# Verificar ruta completa
from pathlib import Path
image_path = Path('images/producto001.jpg')
print(f"Existe: {image_path.exists()}")
print(f"Ruta absoluta: {image_path.absolute()}")
```

## Comparación con Versión Original

| Característica | Original | Optimizada |
|----------------|----------|------------|
| Almacenamiento | Google Sheets | CSV local |
| Dependencias | gspread + OAuth | Solo pandas |
| Reanudación | ✅ | ✅ Mejorada |
| Progreso visual | ❌ | ✅ tqdm |
| Logging | Print básico | ✅ logging |
| Guardado | Por celda | ✅ Configurable |
| Estructura | Monolítico | ✅ Modular |
| Análisis | ❌ | ✅ Incluido |

## Próximos Pasos

1. **Procesamiento Paralelo**: Procesar múltiples imágenes simultáneamente
2. **Validación de Atributos**: Verificar que los atributos cumplan el formato
3. **Dashboard Web**: Interfaz gráfica para monitorear progreso
4. **Integración con Bases de Datos**: Guardar directo en PostgreSQL/MongoDB

## Soporte

Para reportar problemas o sugerencias:
- Revisa el archivo `extraccion_atributos.log`
- Verifica la documentación de Gemini: https://ai.google.dev/docs
- Consulta ejemplos en el notebook
