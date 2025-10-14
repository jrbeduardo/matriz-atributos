"""
Scraper de productos de Coppel
Extrae información de productos de bebé de Coppel.com
"""

import os
import time
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm


class CoppelScraper:
    """Scraper para productos de Coppel"""

    def __init__(self, output_dir: str = "images"):
        self.base_url = "https://www.coppel.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def extract_product_data_from_script(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrae datos de productos desde scripts JSON-LD o Next.js data"""
        products = []

        # Buscar scripts con datos JSON
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    products.append(self.parse_product_schema(data))
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            products.append(self.parse_product_schema(item))
            except:
                continue

        # Buscar Next.js __NEXT_DATA__
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        if next_data_script:
            try:
                next_data = json.loads(next_data_script.string)
                # Navegar por la estructura de Next.js
                page_props = next_data.get('props', {}).get('pageProps', {})

                # Diferentes estructuras posibles
                if 'products' in page_props:
                    for product in page_props['products']:
                        products.append(self.parse_nextjs_product(product))
                elif 'initialProducts' in page_props:
                    for product in page_props['initialProducts']:
                        products.append(self.parse_nextjs_product(product))
                elif 'productList' in page_props:
                    for product in page_props['productList']:
                        products.append(self.parse_nextjs_product(product))
            except Exception as e:
                print(f"Error parsing Next.js data: {e}")

        return products

    def parse_product_schema(self, data: Dict) -> Dict:
        """Parsea un producto desde schema.org JSON-LD"""
        return {
            'id': data.get('sku', data.get('productID', '')),
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'image': data.get('image', ''),
            'price': self.extract_price(data.get('offers', {})),
            'brand': data.get('brand', {}).get('name', ''),
            'category': data.get('category', ''),
        }

    def parse_nextjs_product(self, product: Dict) -> Dict:
        """Parsea un producto desde datos de Next.js"""
        # Adaptable a diferentes estructuras
        image = product.get('image', product.get('imageUrl', product.get('thumbnail', '')))
        if isinstance(image, list) and len(image) > 0:
            image = image[0]

        return {
            'id': product.get('id', product.get('sku', product.get('productId', ''))),
            'name': product.get('name', product.get('title', product.get('productName', ''))),
            'description': product.get('description', product.get('desc', '')),
            'image': image,
            'price': product.get('price', product.get('salePrice', '')),
            'brand': product.get('brand', product.get('brandName', '')),
            'category': product.get('category', product.get('categoryName', '')),
        }

    def extract_price(self, offers: Dict) -> str:
        """Extrae precio de la estructura de ofertas"""
        if isinstance(offers, dict):
            return str(offers.get('price', offers.get('lowPrice', '')))
        elif isinstance(offers, list) and len(offers) > 0:
            return str(offers[0].get('price', ''))
        return ''

    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape una página de Coppel"""
        print(f"\n🔍 Scrapeando: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Intentar extraer desde scripts JSON
            products = self.extract_product_data_from_script(soup)

            if products:
                print(f"✅ Encontrados {len(products)} productos desde JSON")
                return products

            # Si no hay datos JSON, intentar scraping HTML tradicional
            print("⚠️ No se encontraron datos JSON, intentando HTML parsing...")
            products = self.scrape_html_fallback(soup)

            return products

        except requests.RequestException as e:
            print(f"❌ Error al hacer request: {e}")
            return []

    def scrape_html_fallback(self, soup: BeautifulSoup) -> List[Dict]:
        """Fallback: scraping HTML cuando no hay JSON disponible"""
        products = []

        # Buscar contenedores de productos (selectores comunes)
        product_selectors = [
            {'class': re.compile(r'product.*card', re.I)},
            {'class': re.compile(r'item.*product', re.I)},
            {'data-testid': re.compile(r'product', re.I)},
        ]

        product_elements = []
        for selector in product_selectors:
            elements = soup.find_all(['div', 'article', 'li'], selector)
            if elements:
                product_elements = elements
                print(f"Encontrados {len(elements)} elementos con selector {selector}")
                break

        for elem in product_elements:
            try:
                # Intentar extraer información básica
                product = {
                    'id': self.extract_id(elem),
                    'name': self.extract_name(elem),
                    'description': self.extract_description(elem),
                    'image': self.extract_image(elem),
                    'price': self.extract_price_html(elem),
                    'brand': '',
                    'category': 'Bebé',
                }

                if product['name'] or product['image']:
                    products.append(product)
            except:
                continue

        return products

    def extract_id(self, elem) -> str:
        """Extrae ID del producto"""
        # Buscar en atributos data-*
        for attr in ['data-id', 'data-product-id', 'data-sku', 'id']:
            if elem.get(attr):
                return str(elem[attr])
        return ''

    def extract_name(self, elem) -> str:
        """Extrae nombre del producto"""
        # Buscar en diferentes tags
        name_elem = (
            elem.find(['h2', 'h3', 'h4'], class_=re.compile(r'name|title|product', re.I)) or
            elem.find('a', class_=re.compile(r'name|title', re.I)) or
            elem.find(['span', 'p'], class_=re.compile(r'name|title', re.I))
        )
        return name_elem.get_text(strip=True) if name_elem else ''

    def extract_description(self, elem) -> str:
        """Extrae descripción del producto"""
        desc_elem = elem.find(['p', 'span', 'div'], class_=re.compile(r'description|desc', re.I))
        return desc_elem.get_text(strip=True) if desc_elem else ''

    def extract_image(self, elem) -> str:
        """Extrae URL de imagen"""
        img = elem.find('img')
        if img:
            # Probar diferentes atributos
            for attr in ['src', 'data-src', 'data-lazy-src', 'srcset']:
                url = img.get(attr)
                if url:
                    # Si es srcset, tomar la primera URL
                    if attr == 'srcset':
                        url = url.split(',')[0].split(' ')[0]
                    return urljoin(self.base_url, url)
        return ''

    def extract_price_html(self, elem) -> str:
        """Extrae precio del HTML"""
        price_elem = elem.find(['span', 'div', 'p'], class_=re.compile(r'price', re.I))
        if price_elem:
            text = price_elem.get_text(strip=True)
            # Extraer solo números
            match = re.search(r'\d+(?:,\d+)?(?:\.\d+)?', text.replace(',', ''))
            return match.group(0) if match else text
        return ''

    def download_image(self, url: str, filename: str) -> Optional[str]:
        """Descarga una imagen y retorna el nombre del archivo"""
        if not url:
            return None

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Determinar extensión
            content_type = response.headers.get('content-type', '')
            ext = 'jpg'
            if 'png' in content_type:
                ext = 'png'
            elif 'webp' in content_type:
                ext = 'webp'

            image_filename = f"{filename}.{ext}"
            image_path = self.output_dir / image_filename

            with open(image_path, 'wb') as f:
                f.write(response.content)

            return image_filename

        except Exception as e:
            print(f"Error descargando imagen {url}: {e}")
            return None

    def scrape_and_save(
        self,
        url: str,
        output_csv: str = "productos.csv",
        download_images: bool = True,
        max_products: int = None
    ) -> pd.DataFrame:
        """
        Scrape productos y guarda en CSV

        Args:
            url: URL de la página de Coppel
            output_csv: Nombre del archivo CSV de salida
            download_images: Si descargar las imágenes
            max_products: Número máximo de productos (None = todos)
        """
        print("=" * 60)
        print("🛒 SCRAPER DE PRODUCTOS COPPEL")
        print("=" * 60)

        # Scrape productos
        products = self.scrape_page(url)

        if not products:
            print("❌ No se encontraron productos")
            return pd.DataFrame()

        # Limitar productos si es necesario
        if max_products:
            products = products[:max_products]

        print(f"\n📦 Total de productos encontrados: {len(products)}")

        # Descargar imágenes
        if download_images:
            print("\n📥 Descargando imágenes...")
            for i, product in enumerate(tqdm(products, desc="Descargando")):
                if product.get('image'):
                    # Generar nombre de archivo único
                    product_id = product.get('id', f'PROD{i+1:03d}')
                    filename = f"{product_id}"

                    image_filename = self.download_image(product['image'], filename)
                    if image_filename:
                        product['image_file'] = image_filename
                    else:
                        product['image_file'] = ''

                    # Rate limiting
                    time.sleep(0.5)
                else:
                    product['image_file'] = ''

        # Crear DataFrame
        df = pd.DataFrame(products)

        # Renombrar columnas para consistencia
        column_mapping = {
            'id': 'id',
            'name': 'nombre',
            'image_file': 'image',
            'description': 'descripcion',
            'price': 'precio',
            'brand': 'marca',
            'category': 'categoria',
        }

        df = df.rename(columns=column_mapping)

        # Seleccionar columnas relevantes
        columns_order = ['id', 'image', 'nombre', 'descripcion', 'precio', 'marca', 'categoria']
        df = df[[col for col in columns_order if col in df.columns]]

        # Guardar CSV
        df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"\n✅ Productos guardados en: {output_csv}")
        print(f"✅ Imágenes guardadas en: {self.output_dir}/")

        # Mostrar resumen
        print("\n📊 RESUMEN:")
        print(f"Total de productos: {len(df)}")
        print(f"Con imágenes: {len(df[df['image'] != ''])}")
        print(f"Con descripción: {len(df[df['descripcion'] != ''])}")

        return df


def main():
    """Función principal"""
    # URL de la categoría de bebés en Coppel
    url = "https://www.coppel.com/sd/RB2315EPMTPEBEBALOOKS"

    # Crear scraper
    scraper = CoppelScraper(output_dir="images")

    # Scrape y guardar
    df = scraper.scrape_and_save(
        url=url,
        output_csv="productos_coppel.csv",
        download_images=True,
        max_products=20  # Limitar a 20 productos para prueba
    )

    # Mostrar primeros resultados
    if not df.empty:
        print("\n" + "=" * 60)
        print("PRIMEROS PRODUCTOS:")
        print("=" * 60)
        print(df.head().to_string())


if __name__ == "__main__":
    main()
