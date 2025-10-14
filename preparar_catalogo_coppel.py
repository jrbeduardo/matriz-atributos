"""
Prepara el catálogo de Coppel para extracción de atributos
Descarga imágenes y formatea el CSV
"""

import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import time


def descargar_imagen(url: str, filename: str, output_dir: Path) -> str:
    """Descarga una imagen desde URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Determinar extensión
        content_type = response.headers.get('content-type', '')
        ext = 'jpg'
        if 'png' in content_type:
            ext = 'png'
        elif 'webp' in content_type:
            ext = 'webp'

        # Guardar imagen
        image_filename = f"{filename}.{ext}"
        image_path = output_dir / image_filename

        with open(image_path, 'wb') as f:
            f.write(response.content)

        return image_filename

    except Exception as e:
        print(f"  ❌ Error descargando {filename}: {e}")
        return ''


def preparar_catalogo(
    input_csv: str = "productos_coppel_playwright.csv",
    output_csv: str = "productos.csv",
    download_images: bool = True
):
    """Prepara el catálogo para extracción de atributos"""

    print("=" * 60)
    print("📋 PREPARANDO CATÁLOGO DE COPPEL")
    print("=" * 60)

    # Leer CSV extraído
    print(f"\n📖 Leyendo: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"✅ {len(df)} productos cargados")

    # Crear directorio de imágenes
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    # Descargar imágenes
    if download_images:
        print(f"\n📥 Descargando imágenes a {images_dir}/...")

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Descargando"):
            if pd.notna(row.get('image')) and row['image']:
                # Generar nombre de archivo
                product_id = str(row.get('id', f'PROD{idx+1:04d}'))
                safe_id = product_id.replace('/', '_').replace(' ', '_')

                # Descargar imagen
                image_filename = descargar_imagen(row['image'], safe_id, images_dir)

                if image_filename:
                    df.at[idx, 'image_file'] = image_filename
                else:
                    df.at[idx, 'image_file'] = ''

                # Rate limiting
                time.sleep(0.3)
            else:
                df.at[idx, 'image_file'] = ''

        print(f"✅ Imágenes descargadas")

    # Crear columnas adicionales para extracción de atributos
    print("\n🔧 Agregando columnas para extracción...")

    # Renombrar columnas
    df_final = df.rename(columns={
        'name': 'nombre',
        'description': 'descripcion',
        'price': 'precio',
        'brand': 'marca',
        'category': 'categoria',
        'image_file': 'image'
    })

    # Agregar columnas de atributos (vacías, se llenarán con Gemini)
    columnas_atributos = [
        'Tipo', 'Detalles', 'Bolsillos', 'Composición', 'Número de piezas',
        'Género', 'Corte', 'Características especiales', 'Tipo de cierre',
        'Color del armazón', 'Largo', 'Color', 'Estilo', 'ColorAgrupador',
        'Tipo de producto', 'Tipo de cuello', 'Material', 'Cintura',
        'Tipo de manga', 'Ocasión', 'Tipo de estampado'
    ]

    for col in columnas_atributos:
        if col not in df_final.columns:
            df_final[col] = 'nan'

    # Inferir algunos atributos del nombre
    print("🤖 Infiriendo atributos básicos del nombre...")

    for idx, row in df_final.iterrows():
        nombre = str(row.get('nombre', '')).lower()

        # Género
        if 'niña' in nombre or 'girl' in nombre:
            df_final.at[idx, 'Género'] = 'Bebé niña'
        elif 'niño' in nombre or 'boy' in nombre:
            df_final.at[idx, 'Género'] = 'Bebé niño'
        elif 'bebé' in nombre or 'baby' in nombre:
            df_final.at[idx, 'Género'] = 'Bebé'
        else:
            df_final.at[idx, 'Género'] = 'Unisex'

        # Tipo de producto
        if 'conjunto' in nombre or 'set' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Conjunto'
            # Número de piezas
            if '3 piezas' in nombre:
                df_final.at[idx, 'Número de piezas'] = 3
            elif '2 piezas' in nombre:
                df_final.at[idx, 'Número de piezas'] = 2
        elif 'mameluco' in nombre or 'bodysuit' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Mameluco'
            df_final.at[idx, 'Número de piezas'] = 1
        elif 'jumper' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Jumper'
            df_final.at[idx, 'Número de piezas'] = 1
        elif 'vestido' in nombre or 'dress' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Vestido'
            df_final.at[idx, 'Número de piezas'] = 1
        elif 'pantalón' in nombre or 'pants' in nombre or 'leggings' in nombre or 'mallas' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Pantalón'
            df_final.at[idx, 'Número de piezas'] = 1
        elif 'playera' in nombre or 'shirt' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Playera'
            df_final.at[idx, 'Número de piezas'] = 1
        elif 'sudadera' in nombre or 'hoodie' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Sudadera'
            df_final.at[idx, 'Número de piezas'] = 1
        elif 'babero' in nombre or 'bib' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Babero'
            df_final.at[idx, 'Número de piezas'] = 1
        elif 'zapato' in nombre or 'shoe' in nombre:
            df_final.at[idx, 'Tipo de producto'] = 'Zapatos'
            df_final.at[idx, 'Número de piezas'] = 1

        # Color
        colores = {
            'rosa': 'Rosa',
            'pink': 'Rosa',
            'azul': 'Azul',
            'blue': 'Azul',
            'negro': 'Negro',
            'black': 'Negro',
            'blanco': 'Blanco',
            'white': 'Blanco',
            'gris': 'Gris',
            'gray': 'Gris',
            'beige': 'Beige',
            'verde': 'Verde',
            'green': 'Verde',
        }

        for color_key, color_value in colores.items():
            if color_key in nombre:
                df_final.at[idx, 'Color'] = color_value
                break

        # Marca
        marcas = ['nike', 'adidas', 'baby colors', 'baby room', 'baby pop']
        for marca in marcas:
            if marca in nombre:
                df_final.at[idx, 'marca'] = marca.title()
                break

    # Seleccionar columnas finales
    columnas_finales = [
        'id', 'image', 'nombre', 'descripcion', 'precio', 'marca', 'categoria',
        'Tipo', 'Detalles', 'Bolsillos', 'Composición', 'Número de piezas',
        'Género', 'Corte', 'Características especiales', 'Tipo de cierre',
        'Color del armazón', 'Largo', 'Color', 'Estilo', 'ColorAgrupador',
        'Tipo de producto', 'Tipo de cuello', 'Material', 'Cintura',
        'Tipo de manga', 'Ocasión', 'Tipo de estampado'
    ]

    df_output = df_final[[col for col in columnas_finales if col in df_final.columns]]

    # Guardar CSV final
    df_output.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n✅ Catálogo guardado en: {output_csv}")

    # Estadísticas
    print("\n📊 ESTADÍSTICAS:")
    print(f"Total de productos: {len(df_output)}")

    if download_images:
        con_imagen = len(df_output[df_output['image'].notna() & (df_output['image'] != '')])
        print(f"Con imágenes descargadas: {con_imagen}")

    print(f"\nPor tipo de producto:")
    tipo_counts = df_output['Tipo de producto'].value_counts()
    for tipo, count in tipo_counts.items():
        if tipo != 'nan':
            print(f"  {tipo}: {count}")

    print(f"\nPor género:")
    genero_counts = df_output['Género'].value_counts()
    for genero, count in genero_counts.items():
        if genero != 'nan':
            print(f"  {genero}: {count}")

    print("\n" + "=" * 60)
    print("MUESTRA DEL CATÁLOGO:")
    print("=" * 60)
    print(df_output[['id', 'nombre', 'Tipo de producto', 'Género', 'Color']].head(10).to_string(index=False))

    print("\n💡 PRÓXIMO PASO:")
    print("Ejecuta el notebook de extracción de atributos:")
    print("  uv run jupyter notebook extraccion_optimizada.ipynb")

    return df_output


if __name__ == "__main__":
    df = preparar_catalogo(
        input_csv="productos_coppel_playwright.csv",
        output_csv="productos.csv",
        download_images=True
    )
