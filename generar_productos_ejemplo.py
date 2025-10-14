"""
Generador de productos de ejemplo realistas
Basado en la estructura de productos de bebé de Coppel
"""

import pandas as pd
import random
from pathlib import Path


class GeneradorProductosEjemplo:
    """Genera productos de ejemplo realistas para testing"""

    def __init__(self):
        self.categorias = {
            'Conjunto': {
                'colores': ['Gris', 'Azul', 'Rosa', 'Blanco', 'Multicolor'],
                'generos': ['Unisex', 'Bebé niño', 'Bebé niña'],
                'tipos_cuello': ['Redondo', 'Tipo V', 'Polo'],
                'tipos_manga': ['Corta', 'Larga', 'Sin manga'],
                'tipos_estampado': ['Geométrico', 'Liso', 'Rayas', 'Puntos', 'Floral'],
                'piezas': [2, 3],
            },
            'Vestido': {
                'colores': ['Rosa', 'Rosa fucsia', 'Blanco', 'Multicolor', 'Azul'],
                'generos': ['Bebé niña', 'Niña'],
                'tipos_cuello': ['Redondo', 'Cuadrado', 'Tipo V'],
                'tipos_manga': ['Sin manga', 'Corta', 'Larga'],
                'tipos_estampado': ['Floral', 'Liso', 'Puntos', 'Estampado'],
                'piezas': [1],
            },
            'Pantalón': {
                'colores': ['Azul', 'Negro', 'Gris', 'Café', 'Verde'],
                'generos': ['Bebé niño', 'Niño', 'Unisex'],
                'cortes': ['Recto', 'Jogger', 'Cargo', 'Skinny'],
                'tipos_estampado': ['Liso', 'Rayas'],
                'piezas': [1],
            },
            'Playera': {
                'colores': ['Blanco', 'Azul', 'Rosa', 'Gris', 'Multicolor'],
                'generos': ['Unisex', 'Bebé niño', 'Bebé niña'],
                'tipos_cuello': ['Redondo', 'Polo', 'Tipo V'],
                'tipos_manga': ['Corta', 'Larga'],
                'tipos_estampado': ['Estampado', 'Liso', 'Rayas', 'Geométrico'],
                'piezas': [1],
            },
            'Pijama': {
                'colores': ['Azul', 'Rosa', 'Gris', 'Multicolor'],
                'generos': ['Unisex', 'Bebé niño', 'Bebé niña'],
                'tipos_cuello': ['Redondo'],
                'tipos_manga': ['Larga', 'Corta'],
                'tipos_estampado': ['Estampado', 'Puntos', 'Rayas'],
                'piezas': [2],
            },
            'Mameluco': {
                'colores': ['Blanco', 'Rosa', 'Azul', 'Gris', 'Multicolor'],
                'generos': ['Bebé', 'Bebé niño', 'Bebé niña'],
                'tipos_cuello': ['Redondo'],
                'tipos_manga': ['Corta', 'Larga', 'Sin manga'],
                'tipos_estampado': ['Liso', 'Estampado', 'Puntos'],
                'piezas': [1],
            },
        }

        self.colores_agrupados = {
            'Azul': 'Azul (#1876D1)',
            'Blanco': 'Blanco (#FEFEFE)',
            'Rosa': 'Rosa (#F36EA8)',
            'Rosa fucsia': 'Rosa (#F36EA8)',
            'Gris': 'Gris (#C2C4C6)',
            'Negro': 'Negro (#000)',
            'Multicolor': 'Multicolor (Multicolor)',
            'Café': 'Café (#915808)',
            'Verde': 'Verde (#72BA11)',
        }

        self.detalles_posibles = [
            'cintura elástica',
            'con botones al frente',
            'con cierre',
            'cuello ribeteado',
            'bolsillos laterales',
            'estampado de dinosaurios',
            'aplicación de flores',
            'manga ranglan',
            'pretina ajustable',
            'con capucha',
            'broches en entrepierna',
            'costuras reforzadas',
        ]

        self.materiales = [
            'Algodón',
            'Poliéster',
            'Algodón y poliéster',
            'Jersey',
            'Mezcla de algodón',
        ]

        self.ocasiones = ['Casual', 'Uso diario', 'Deporte']

        self.caracteristicas = [
            'Suave al tacto',
            'Fácil de lavar',
            'Transpirable',
            'Resistente',
            'Cómodo',
            'Libre de sustancias nocivas',
        ]

    def generar_producto(self, idx: int, tipo_producto: str = None) -> dict:
        """Genera un producto de ejemplo"""

        # Seleccionar tipo de producto
        if tipo_producto is None:
            tipo_producto = random.choice(list(self.categorias.keys()))

        config = self.categorias[tipo_producto]

        # Generar atributos
        color = random.choice(config['colores'])
        genero = random.choice(config['generos'])
        numero_piezas = random.choice(config['piezas'])
        tipo_estampado = random.choice(config['tipos_estampado'])

        producto = {
            'id': f'PROD{idx:04d}',
            'image': f'producto_{idx:04d}.jpg',
            'Tipo': 'nan',  # Generalmente no aplica para ropa
            'Detalles': random.choice(self.detalles_posibles),
            'Bolsillos': random.choice(['No', 'Sí', 'nan', '2', '4']),
            'Composición': 'nan',  # Se completa con Gemini
            'Número de piezas': numero_piezas,
            'Género': genero,
            'Corte': config.get('cortes', ['nan'])[0] if 'cortes' in config else 'nan',
            'Características especiales': random.choice(self.caracteristicas),
            'Tipo de cierre': random.choice(['nan', 'Broche', 'Elástico', 'Presión']),
            'Color del armazón': 'nan',  # No aplica para ropa
            'Largo': random.choice(['nan', 'Corto', '20 cm', '25 cm']),
            'Color': color,
            'Estilo': random.choice(['Casual', 'Infantil', 'Moderno', 'Confort']),
            'ColorAgrupador': self.colores_agrupados.get(color, 'nan'),
            'Tipo de producto': tipo_producto,
            'Tipo de cuello': config.get('tipos_cuello', ['nan'])[0] if 'tipos_cuello' in config else 'nan',
            'Material': random.choice(self.materiales),
            'Cintura': random.choice(['Elástica', 'Ajustable', 'Sencilla', 'nan']),
            'Tipo de manga': config.get('tipos_manga', ['nan'])[0] if 'tipos_manga' in config else 'nan',
            'Ocasión': random.choice(self.ocasiones),
            'Tipo de estampado': tipo_estampado,
        }

        return producto

    def generar_catalogo(self, num_productos: int = 30) -> pd.DataFrame:
        """Genera un catálogo completo de productos"""

        productos = []

        # Distribuir productos entre categorías
        categorias = list(self.categorias.keys())
        productos_por_categoria = num_productos // len(categorias)

        idx = 1
        for categoria in categorias:
            for _ in range(productos_por_categoria):
                producto = self.generar_producto(idx, categoria)
                productos.append(producto)
                idx += 1

        # Productos restantes aleatorios
        while idx <= num_productos:
            producto = self.generar_producto(idx)
            productos.append(producto)
            idx += 1

        df = pd.DataFrame(productos)
        return df

    def crear_imagenes_placeholder(self, df: pd.DataFrame, output_dir: str = "images"):
        """Crea archivos placeholder para las imágenes"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Crear archivos vacíos como placeholder
        for image_name in df['image']:
            image_path = output_path / image_name
            if not image_path.exists():
                # Crear archivo vacío
                image_path.touch()

        print(f"✅ Creados {len(df)} archivos placeholder en {output_dir}/")


def main():
    """Función principal"""
    print("=" * 60)
    print("🏭 GENERADOR DE PRODUCTOS DE EJEMPLO")
    print("=" * 60)

    generador = GeneradorProductosEjemplo()

    # Generar catálogo
    num_productos = 30
    print(f"\n📦 Generando {num_productos} productos de ejemplo...")
    df = generador.generar_catalogo(num_productos)

    # Guardar CSV
    output_csv = "productos.csv"
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"✅ Catálogo guardado en: {output_csv}")

    # Crear placeholders de imágenes
    print(f"\n🖼️  Creando archivos placeholder para imágenes...")
    generador.crear_imagenes_placeholder(df)

    # Mostrar estadísticas
    print("\n📊 ESTADÍSTICAS DEL CATÁLOGO:")
    print(f"Total de productos: {len(df)}")
    print("\nProductos por categoría:")
    print(df['Tipo de producto'].value_counts().to_string())

    print("\nProductos por género:")
    print(df['Género'].value_counts().to_string())

    print("\nProductos por color:")
    print(df['Color'].value_counts().to_string())

    # Mostrar muestra
    print("\n" + "=" * 60)
    print("MUESTRA DE PRODUCTOS:")
    print("=" * 60)
    print(df[['id', 'image', 'Tipo de producto', 'Color', 'Género', 'Número de piezas']].head(10).to_string())

    print("\n💡 SIGUIENTE PASO:")
    print("1. Reemplaza los archivos placeholder en images/ con imágenes reales")
    print("2. O usa el scraper para descargar imágenes reales")
    print("3. Ejecuta el notebook de extracción de atributos")


if __name__ == "__main__":
    main()
