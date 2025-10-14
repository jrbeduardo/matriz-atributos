# Scraper y Generador de Productos

Este proyecto incluye dos herramientas para crear catálogos de productos:

1. **Scraper de Coppel** - Extrae productos reales del sitio web
2. **Generador de Ejemplos** - Crea productos de ejemplo realistas

## 🚀 Inicio Rápido

### Opción A: Generador de Productos de Ejemplo (Recomendado)

La forma más rápida de empezar es generar productos de ejemplo:

```bash
# Generar catálogo de 30 productos
uv run python generar_productos_ejemplo.py
```

Esto creará:
- ✅ `productos.csv` con 30 productos realistas
- ✅ Archivos placeholder en `images/`
- ✅ Datos basados en estructura real de Coppel

**Resultado:**
```
📦 30 productos generados
📂 images/ con archivos placeholder
📄 productos.csv listo para usar
```

### Opción B: Scraper de Coppel (Avanzado)

Para extraer productos reales de Coppel:

```bash
# Requiere dependencias adicionales
uv sync --extra scraper

# Ejecutar scraper
uv run python scraper_coppel.py
```

**Nota:** El sitio de Coppel tiene protección contra scraping. Se recomienda usar el generador de ejemplos.

## 📊 Estructura del CSV Generado

El archivo `productos.csv` incluye todas las columnas necesarias:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| id | Identificador único | PROD0001 |
| image | Nombre del archivo de imagen | producto_0001.jpg |
| Tipo | Tipo específico (generalmente nan para ropa) | nan |
| Detalles | Características visuales | "cintura elástica" |
| Bolsillos | Número de bolsillos | "2", "Sí", "No" |
| Composición | Material (se completa con Gemini) | nan |
| Número de piezas | Cantidad de piezas | 1, 2, 3 |
| Género | Género del producto | Bebé niño, Unisex |
| Corte | Tipo de corte | Recto, Jogger |
| Características especiales | Atributos especiales | "Suave al tacto" |
| Tipo de cierre | Tipo de cierre | Broche, Elástico |
| Color del armazón | Color del armazón (no aplica ropa) | nan |
| Largo | Largo del producto | "Corto", "25 cm" |
| Color | Color principal | Azul, Rosa, Gris |
| Estilo | Estilo del producto | Casual, Infantil |
| ColorAgrupador | Color con código hex | Azul (#1876D1) |
| Tipo de producto | Categoría principal | Conjunto, Vestido |
| Tipo de cuello | Tipo de cuello | Redondo, Tipo V |
| Material | Material principal | Algodón, Jersey |
| Cintura | Tipo de cintura | Elástica, Ajustable |
| Tipo de manga | Tipo de manga | Corta, Larga |
| Ocasión | Ocasión de uso | Casual, Deporte |
| Tipo de estampado | Tipo de estampado | Liso, Geométrico |

## 🎨 Categorías de Productos

El generador crea productos en 6 categorías:

1. **Conjunto** - Sets de 2-3 piezas
2. **Vestido** - Vestidos para niña/bebé
3. **Pantalón** - Pantalones diversos
4. **Playera** - Camisetas y playeras
5. **Pijama** - Pijamas de 2 piezas
6. **Mameluco** - Mamelucos de bebé

Cada categoría tiene atributos específicos realistas.

## 🔧 Personalización

### Cambiar Número de Productos

Edita `generar_productos_ejemplo.py`:

```python
# En la función main(), cambiar:
num_productos = 50  # En lugar de 30
```

### Agregar Nuevas Categorías

```python
self.categorias['TuCategoria'] = {
    'colores': ['Azul', 'Rosa'],
    'generos': ['Unisex'],
    'tipos_cuello': ['Redondo'],
    'tipos_manga': ['Corta'],
    'tipos_estampado': ['Liso'],
    'piezas': [1],
}
```

### Modificar Atributos

```python
# Agregar más detalles
self.detalles_posibles.append('tu nuevo detalle')

# Agregar más materiales
self.materiales.append('Tu Material')
```

## 📥 Usar Imágenes Reales

### Opción 1: Manual

1. Descarga imágenes de productos de bebé
2. Renombra como: `producto_0001.jpg`, `producto_0002.jpg`, etc.
3. Coloca en la carpeta `images/`

### Opción 2: Desde URLs

Si tienes URLs de imágenes, modifica el generador:

```python
# Agregar método para descargar
def descargar_imagen(self, url, filename):
    import requests
    response = requests.get(url)
    with open(f'images/{filename}', 'wb') as f:
        f.write(response.content)
```

### Opción 3: Scraper Personalizado

Adapta `scraper_coppel.py` para otro sitio sin protección:

```python
# Cambiar URL base
scraper = CoppelScraper(output_dir="images")
df = scraper.scrape_and_save(
    url="https://tu-sitio.com/productos",
    output_csv="productos.csv",
    download_images=True
)
```

## 🧪 Verificar Resultados

```bash
# Ver estadísticas del catálogo
uv run python -c "
import pandas as pd
df = pd.read_csv('productos.csv')
print(f'Total: {len(df)} productos')
print(df['Tipo de producto'].value_counts())
"

# Ver primeros 5 productos
uv run python -c "
import pandas as pd
df = pd.read_csv('productos.csv')
print(df[['id', 'Tipo de producto', 'Color', 'Género']].head())
"
```

## 📋 Siguiente Paso: Extracción de Atributos

Una vez que tengas el CSV con productos:

1. **Opción A - Con imágenes reales:**
   - Reemplaza los placeholders en `images/` con imágenes reales
   - Ejecuta `extraccion_optimizada.ipynb`

2. **Opción B - Sin imágenes (solo metadatos):**
   - Modifica el prompt para trabajar solo con metadatos
   - Ejecuta la extracción

```bash
# Abrir notebook de extracción
uv run jupyter notebook extraccion_optimizada.ipynb
```

## 🛠️ Solución de Problemas

### Error: "No module named 'requests'"

```bash
uv sync
```

### Error: Scraper no funciona

El sitio de Coppel tiene protección. Usa el generador de ejemplos:

```bash
uv run python generar_productos_ejemplo.py
```

### Personalizar Distribución de Productos

```python
# En generar_catalogo(), modificar:
productos_por_categoria = {
    'Conjunto': 10,
    'Vestido': 5,
    'Pantalón': 8,
    # ...
}
```

## 📈 Estadísticas de Ejemplo

Catálogo generado típico (30 productos):

```
Productos por categoría:
- Conjunto: 5
- Vestido: 5
- Pantalón: 5
- Playera: 5
- Pijama: 5
- Mameluco: 5

Productos por género:
- Bebé niño: ~9
- Bebé niña: ~8
- Unisex: ~7
- Bebé: ~3
- Niño: ~2
- Niña: ~1

Distribución realista basada en mercado
```

## 🎯 Casos de Uso

### 1. Testing del Sistema de Extracción
```bash
# Generar muestra pequeña
python generar_productos_ejemplo.py  # Editar num_productos = 5
```

### 2. Catálogo de Producción
```bash
# Generar catálogo completo
python generar_productos_ejemplo.py  # Editar num_productos = 100
```

### 3. Demo/Presentación
```bash
# Generar con categorías específicas
# Editar categorias dict para solo incluir Conjunto y Vestido
```

## 🔗 Integración con Extracción

El CSV generado es 100% compatible con `extraccion_optimizada.ipynb`:

```python
# En el notebook, usar:
config.INPUT_CSV = Path('productos.csv')
config.IMAGE_DIRECTORY = Path('images')

# Ejecutar extracción
df_result = run_extraction()
```

## 💡 Tips

- ✅ Genera primero 5-10 productos para testing
- ✅ Verifica que el CSV se abre correctamente
- ✅ Coloca al menos una imagen real para probar extracción
- ✅ Usa el generador para crear estructura base
- ✅ Completa con datos reales después

## 📚 Recursos

- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Docs](https://requests.readthedocs.io/)
- [Pandas CSV Guide](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
