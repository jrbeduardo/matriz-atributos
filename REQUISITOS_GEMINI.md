# 📋 Requisitos para Extracción de Atributos con Gemini

## 1. 🔑 Cuenta de Google

### ¿Qué necesitas?

- ✅ **Cuenta de Google** (Gmail)
- ✅ **Acceso a Google AI Studio**
- ✅ **No requiere tarjeta de crédito** (en plan gratuito)

### Crear Cuenta (si no tienes)

1. Ve a: https://accounts.google.com/signup
2. Crea una cuenta Gmail
3. Confirma tu email

---

## 2. 🤖 Google AI Studio y API Key

### Paso 1: Acceder a Google AI Studio

1. **Visita:** https://aistudio.google.com/
2. **Inicia sesión** con tu cuenta de Google
3. **Acepta** los términos de servicio

### Paso 2: Obtener API Key

1. En Google AI Studio, ve a: **"Get API Key"** o directamente:
   - https://aistudio.google.com/app/apikey

2. Haz clic en **"Create API Key"**

3. **Opciones:**
   - **"Create API key in new project"** (Recomendado para empezar)
   - O selecciona un proyecto existente de Google Cloud

4. **Copia tu API Key** - Se ve algo así:
   ```
   AIzaSyABcDeFg1HiJkLmNoPqRsTuVwXyZ1234567
   ```

5. ⚠️ **IMPORTANTE:** Guarda tu API Key en un lugar seguro
   - NO la compartas públicamente
   - NO la subas a GitHub
   - NO la pegues en mensajes públicos

### Paso 3: Verificar que funciona

1. En Google AI Studio, ve a **"Prompt Gallery"**
2. Prueba un prompt de ejemplo
3. Si funciona, tu API está activa ✅

---

## 3. 🎯 Modelos de Gemini Disponibles

### Modelos Gratuitos (Recomendados)

| Modelo | Velocidad | Costo | Límites | Recomendación |
|--------|-----------|-------|---------|---------------|
| **gemini-2.0-flash-exp** | ⚡⚡⚡ Muy rápido | **GRATIS** | 1500 RPM* | ⭐ Mejor para testing |
| **gemini-1.5-flash** | ⚡⚡ Rápido | **GRATIS** | 15 RPM | ✅ Estable y confiable |
| **gemini-1.5-flash-8b** | ⚡⚡⚡ Muy rápido | **GRATIS** | 4000 RPM | ✅ Ideal para volumen |
| **gemini-1.5-pro** | ⚡ Más lento | **GRATIS** | 2 RPM | 🔬 Para casos complejos |

*RPM = Requests Per Minute (Solicitudes por minuto)

### ¿Cuál usar para este proyecto?

Para **20 productos** de Coppel:

**Opción 1: `gemini-2.0-flash-exp`** ⭐ RECOMENDADO
```python
GEMINI_MODEL = 'gemini-2.0-flash-exp'
```
- ✅ Más rápido
- ✅ Límite alto (1500 RPM)
- ✅ Experimental pero muy bueno
- ✅ Procesa 20 productos en ~2 minutos

**Opción 2: `gemini-1.5-flash`** (Más estable)
```python
GEMINI_MODEL = 'gemini-1.5-flash'
```
- ✅ Modelo estable
- ✅ Buena calidad
- ⚠️ Límite menor (15 RPM)
- ✅ Procesa 20 productos en ~5 minutos

**Opción 3: `gemini-1.5-flash-8b`** (Más económico)
```python
GEMINI_MODEL = 'gemini-1.5-flash-8b'
```
- ✅ Muy rápido
- ✅ Límite altísimo (4000 RPM)
- ⚠️ Modelo más simple
- ✅ Ideal para >100 productos

---

## 4. 💰 Límites y Cuotas

### Plan Gratuito (Free Tier)

**Límites de Rate (por minuto):**
```
gemini-2.0-flash-exp:  1,500 RPM
gemini-1.5-flash:         15 RPM
gemini-1.5-flash-8b:   4,000 RPM
gemini-1.5-pro:            2 RPM
```

**Límites de Tokens (por día):**
```
Todos los modelos: 1,500 requests/día
Tokens de entrada: ~15,000,000 tokens/día
Tokens de salida: Ilimitado
```

### Para este proyecto (20 productos):

- **Requests necesarios:** 20
- **Tiempo estimado:** 2-5 minutos
- **Costo:** $0.00 (GRATIS)
- **Dentro de límites:** ✅ SÍ

### ¿Qué pasa si excedes límites?

```
Error: 429 - Resource Exhausted
```

**Solución:**
1. Esperar 1 minuto
2. Usar modelo con límite más alto
3. Agregar delays entre requests (ya implementado)

---

## 5. ⚙️ Configuración del Proyecto

### Paso 1: Crear archivo .env

```bash
cd /home/franciscomath/matriz-atributos
cp .env.example .env
```

### Paso 2: Editar .env

Abre el archivo `.env` y agrega tu API key:

```bash
# Editar con nano
nano .env

# O con cualquier editor
code .env
```

Contenido del archivo `.env`:
```env
# Google Gemini API Key
# Obtén tu API key en: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=AIzaSyABcDeFg1HiJkLmNoPqRsTuVwXyZ1234567
```

⚠️ Reemplaza `AIzaSyABcDeFg1HiJkLmNoPqRsTuVwXyZ1234567` con tu API key real

### Paso 3: Verificar que .env NO está en git

```bash
cat .gitignore | grep .env
```

Debe mostrar:
```
.env
```

✅ Si aparece, está protegido
❌ Si no aparece, agrégalo: `echo ".env" >> .gitignore`

---

## 6. 🔐 Permisos y Seguridad

### Permisos de la API Key

Tu API key tiene acceso a:
- ✅ Llamadas a modelos de Gemini
- ✅ Google AI Studio
- ❌ NO tiene acceso a tus archivos de Google Drive
- ❌ NO tiene acceso a tu Gmail
- ❌ NO tiene acceso a otros servicios de Google

### Mejores Prácticas

1. **Nunca compartas tu API key**
   ```bash
   # ❌ MAL
   git add .env

   # ✅ BIEN
   # .env está en .gitignore
   ```

2. **Rota tu API key si se expone**
   - Ve a Google AI Studio
   - Revoca la API key comprometida
   - Crea una nueva

3. **Monitorea el uso**
   - Google AI Studio > Usage
   - Revisa requests diarios
   - Verifica que no haya uso anormal

---

## 7. 🧪 Probar la Configuración

### Opción A: Script de Prueba Rápido

```bash
cd /home/franciscomath/matriz-atributos

uv run python -c "
import os
from dotenv import load_dotenv
from google import genai

# Cargar .env
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print('❌ No se encontró GEMINI_API_KEY en .env')
    exit(1)

print('✅ API Key encontrada')
print(f'   Longitud: {len(api_key)} caracteres')
print(f'   Inicia con: {api_key[:10]}...')

# Probar conexión
try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents='Di solo: funciona'
    )
    print('✅ Conexión exitosa con Gemini')
    print(f'   Respuesta: {response.text}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

**Resultado esperado:**
```
✅ API Key encontrada
   Longitud: 39 caracteres
   Inicia con: AIzaSyABcD...
✅ Conexión exitosa con Gemini
   Respuesta: funciona
```

### Opción B: Notebook de Prueba

```bash
uv run jupyter notebook extraccion_optimizada.ipynb
```

Ejecuta solo las primeras 3 celdas:
1. ✅ Instalación de dependencias
2. ✅ Configuración y carga de .env
3. ✅ Inicialización del cliente Gemini

---

## 8. 📊 Configuración Recomendada para los 20 Productos

### En el notebook: `extraccion_optimizada.ipynb`

```python
class Config:
    # Rutas
    PROMPT_FILE = Path('prompt_api.txt')
    IMAGE_DIRECTORY = Path('images')
    INPUT_CSV = Path('productos.csv')
    OUTPUT_CSV = Path('productos_con_atributos.csv')

    # API Configuration ⭐ IMPORTANTE
    GEMINI_MODEL = 'gemini-2.0-flash-exp'  # Modelo recomendado
    MAX_RETRIES = 5                         # Reintentos por error
    BASE_DELAY = 5                          # Segundos base
    RATE_LIMIT_DELAY = 1.5                  # Segundos entre requests

    # Columnas CSV
    ID_COLUMN = 'id'
    IMAGE_COLUMN = 'image'
    ATTRIBUTES_COLUMN = 'gemini_attributes'
```

### Tiempo Estimado

Para **20 productos** con `gemini-2.0-flash-exp`:

```
⏱️ Tiempo total estimado: 2-3 minutos

Cálculo:
- 20 productos
- 1.5s delay entre requests
- ~3-5s por procesamiento
- = ~90-150 segundos total
```

---

## 9. ❓ Preguntas Frecuentes

### ¿Necesito tarjeta de crédito?

**NO.** El plan gratuito no requiere tarjeta de crédito.

### ¿Cuánto cuesta?

**$0.00** para este volumen. El plan gratuito es suficiente.

### ¿Expira la API key?

No, a menos que la revoques manualmente.

### ¿Puedo usar múltiples API keys?

Sí, pero no es necesario para 20 productos.

### ¿Qué pasa si me quedo sin cuota?

Espera 24 horas o usa otro modelo con límite más alto.

### ¿Puedo procesar más de 20 productos?

Sí, con el plan gratuito puedes procesar:
- **gemini-2.0-flash-exp**: ~1,500 productos/día
- **gemini-1.5-flash**: ~15 productos/minuto
- **gemini-1.5-flash-8b**: ~4,000 productos/día

---

## 10. ✅ Checklist Final

Antes de ejecutar la extracción, verifica:

- [ ] Cuenta de Google creada
- [ ] Google AI Studio accesible
- [ ] API Key generada
- [ ] Archivo `.env` creado
- [ ] API Key en `.env`
- [ ] `.env` en `.gitignore`
- [ ] Dependencias instaladas (`uv sync --extra dev`)
- [ ] 20 productos en `productos.csv`
- [ ] 20 imágenes en `images/`
- [ ] Conexión probada con script de prueba

---

## 11. 🚀 ¿Listo para Comenzar?

Si completaste todos los pasos:

```bash
# 1. Verifica tu configuración
cat .env | grep GEMINI_API_KEY

# 2. Abre el notebook
uv run jupyter notebook extraccion_optimizada.ipynb

# 3. Ejecuta todas las celdas
# (Ctrl+Shift+Enter en cada celda)

# 4. Espera 2-3 minutos
# 5. ¡Obtén productos_con_atributos.csv!
```

---

## 📞 Soporte

**Si encuentras errores:**

1. **Error 401 - Unauthorized**
   - ❌ API Key incorrecta
   - ✅ Verifica tu API Key en .env

2. **Error 429 - Too Many Requests**
   - ❌ Excediste el límite de rate
   - ✅ Espera 1 minuto o usa otro modelo

3. **Error 404 - Model not found**
   - ❌ Modelo no disponible
   - ✅ Usa 'gemini-1.5-flash' en su lugar

4. **Error al cargar .env**
   - ❌ Archivo .env no existe o está mal
   - ✅ Verifica que .env esté en el directorio raíz

---

## 🎯 Resumen Rápido

```bash
# 1. Obtén API Key
https://aistudio.google.com/app/apikey

# 2. Configura .env
echo "GEMINI_API_KEY=tu_api_key_aqui" > .env

# 3. Ejecuta
uv run jupyter notebook extraccion_optimizada.ipynb
```

**¡Eso es todo!** 🚀
