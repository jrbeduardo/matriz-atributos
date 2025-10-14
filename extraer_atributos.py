"""
Script para extraer atributos de productos usando Gemini
Versión corregida que funciona con google.generativeai
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

import pandas as pd
import google.generativeai as genai
from tqdm import tqdm
from dotenv import load_dotenv


# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraccion_atributos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """Configuración centralizada del proyecto"""

    # Rutas
    PROMPT_FILE = Path('prompt_api.txt')
    IMAGE_DIRECTORY = Path('images')
    INPUT_CSV = Path('productos.csv')
    OUTPUT_CSV = Path('productos_con_atributos.csv')

    # API Configuration
    GEMINI_MODEL = 'gemini-2.0-flash-exp'
    MAX_RETRIES = 5
    BASE_DELAY = 5
    RATE_LIMIT_DELAY = 1.5

    # Columnas CSV
    ID_COLUMN = 'id'
    IMAGE_COLUMN = 'image'
    ATTRIBUTES_COLUMN = 'gemini_attributes'


def load_prompt(file_path: Path) -> str:
    """Carga el texto del prompt desde un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
        logger.info(f"Prompt cargado desde {file_path} ({len(prompt)} caracteres)")
        return prompt
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            prompt = f.read().strip()
        logger.warning(f"Prompt cargado con encoding latin-1")
        return prompt
    except Exception as e:
        logger.error(f"Error al cargar prompt: {e}")
        raise


def process_image_with_gemini(
    image_path: Path,
    prompt_text: str,
    model_name: str = Config.GEMINI_MODEL,
    max_retries: int = Config.MAX_RETRIES,
    base_delay: int = Config.BASE_DELAY
) -> str:
    """
    Procesa una imagen con Gemini API.
    """
    if not image_path.exists():
        return f"ERROR_IMAGEN: Archivo no encontrado en {image_path}"

    # Leer imagen
    try:
        from PIL import Image
        image = Image.open(image_path)
    except Exception as e:
        return f"ERROR_LECTURA: {str(e)}"

    # Reintentos con backoff exponencial
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt_text, image])
            return response.text.strip().replace('\n', ' ')

        except Exception as e:
            error_message = str(e)
            logger.warning(f"Intento {attempt + 1}/{max_retries} falló: {error_message}")

            if attempt < max_retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                logger.info(f"Esperando {sleep_time}s antes de reintentar...")
                time.sleep(sleep_time)
            else:
                return f"ERROR_API_FATAL: {error_message}"

    return "ERROR_INESPERADO: Bucle de reintento fallido"


def run_extraction(
    config: Config,
    input_csv: Path,
    output_csv: Path,
    prompt_file: Path,
    image_dir: Path
):
    """Ejecuta el proceso de extracción de atributos."""

    print("=" * 60)
    print("🚀 EXTRACCIÓN DE ATRIBUTOS CON GEMINI")
    print("=" * 60)

    # Cargar prompt
    prompt = load_prompt(prompt_file)

    # Cargar CSV
    if not input_csv.exists():
        print(f"❌ Error: No se encontró {input_csv}")
        return None

    df = pd.read_csv(input_csv)
    print(f"\n✅ CSV cargado: {len(df)} productos")

    # Asegurar columna de atributos
    if config.ATTRIBUTES_COLUMN not in df.columns:
        df[config.ATTRIBUTES_COLUMN] = ''

    # Contar pendientes
    rows_to_process = df[config.ATTRIBUTES_COLUMN].str.len() == 0
    total_to_process = rows_to_process.sum()

    print(f"📊 A procesar: {total_to_process}")
    print(f"✅ Ya procesados: {len(df) - total_to_process}")

    if total_to_process == 0:
        print("\n✨ ¡Todos los productos ya están procesados!")
        return df

    print(f"\n⏱️  Tiempo estimado: {total_to_process * 3 // 60} minutos")
    print(f"💰 Costo: $0.00 (gratis)")
    print("\n" + "=" * 60)

    # Procesar productos
    processed_count = 0

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Procesando"):
        # Saltar si ya está procesado
        if df.at[idx, config.ATTRIBUTES_COLUMN]:
            continue

        product_id = row.get(config.ID_COLUMN, idx)
        image_filename = row.get(config.IMAGE_COLUMN, '')

        if not image_filename:
            df.at[idx, config.ATTRIBUTES_COLUMN] = "ERROR_SIN_IMAGEN"
            continue

        image_path = image_dir / image_filename

        # Procesar con Gemini
        attributes = process_image_with_gemini(image_path, prompt)

        # Guardar resultado
        df.at[idx, config.ATTRIBUTES_COLUMN] = attributes

        # Log
        if attributes.startswith("ERROR"):
            print(f"\n❌ {product_id}: {attributes[:80]}")
        else:
            print(f"\n✅ {product_id}: {attributes[:80]}...")

        processed_count += 1

        # Guardar checkpoint cada producto
        df.to_csv(output_csv, index=False, encoding='utf-8')

        # Rate limiting
        time.sleep(config.RATE_LIMIT_DELAY)

    # Estadísticas finales
    print("\n" + "=" * 60)
    print("✨ PROCESO COMPLETADO")
    print("=" * 60)

    successful = len(df[~df[config.ATTRIBUTES_COLUMN].str.startswith('ERROR', na=False)])
    errors = len(df[df[config.ATTRIBUTES_COLUMN].str.startswith('ERROR', na=False)])

    print(f"\n📊 RESULTADOS:")
    print(f"✅ Exitosos: {successful}")
    print(f"❌ Errores: {errors}")
    print(f"📁 Guardado en: {output_csv}")

    return df


def main():
    """Función principal"""

    # Cargar configuración
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("❌ Error: No se encontró GEMINI_API_KEY en .env")
        print("\n💡 Pasos:")
        print("1. Crea archivo .env")
        print("2. Agrega: GEMINI_API_KEY=tu_api_key")
        return

    # Configurar Gemini
    genai.configure(api_key=api_key)
    print("✅ API Key configurada")

    # Crear config
    config = Config()

    # Verificar archivos
    print("\n🔍 Verificando archivos...")

    files_ok = True
    if not config.PROMPT_FILE.exists():
        print(f"❌ No encontrado: {config.PROMPT_FILE}")
        files_ok = False
    else:
        print(f"✅ Prompt: {config.PROMPT_FILE}")

    if not config.INPUT_CSV.exists():
        print(f"❌ No encontrado: {config.INPUT_CSV}")
        files_ok = False
    else:
        print(f"✅ CSV: {config.INPUT_CSV}")

    if not config.IMAGE_DIRECTORY.exists():
        print(f"❌ No encontrado: {config.IMAGE_DIRECTORY}")
        files_ok = False
    else:
        num_images = len(list(config.IMAGE_DIRECTORY.glob('*.jpg')))
        print(f"✅ Imágenes: {config.IMAGE_DIRECTORY} ({num_images} archivos)")

    if not files_ok:
        print("\n❌ Faltan archivos necesarios")
        return

    # Ejecutar extracción
    df = run_extraction(
        config=config,
        input_csv=config.INPUT_CSV,
        output_csv=config.OUTPUT_CSV,
        prompt_file=config.PROMPT_FILE,
        image_dir=config.IMAGE_DIRECTORY
    )

    if df is not None:
        print("\n📄 Primeros 5 resultados:")
        print(df[['id', 'image', 'gemini_attributes']].head().to_string())

        print(f"\n💾 Resultados guardados en: {config.OUTPUT_CSV}")
        print("\n🎉 ¡Listo! Revisa el archivo CSV para ver todos los atributos")


if __name__ == "__main__":
    main()
