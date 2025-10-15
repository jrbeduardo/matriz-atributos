"""
Scraper de Coppel con Playwright
Versión mejorada que ejecuta JavaScript
"""

import time
import json
import re
from pathlib import Path
from typing import List, Dict
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from urllib.parse import urlparse



class CoppelScraperPlaywright:
    """Scraper de Coppel usando Playwright para manejar JavaScript"""
 
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.output_dir = Path("images")
        self.output_dir.mkdir(exist_ok=True)

    def extraer_path_imagen_coppel(self, url: str) -> str:
        try:
            patron = r'([a-z]+)/(\d+-\d+)'
            match = re.search(patron, url)
            if match:
                return f"{match.group(1)}-{match.group(2)}"
            return ""        
        except Exception as e:
            print(f"Error procesando URL {url}: {e}")
            return None
 
    def scrape_products(self, url: str, max_products: int = 20) -> List[Dict]:
        """
        Scrape productos de Coppel usando Playwright

        Args:
            url: URL de la categoría
            max_products: Número máximo de productos a extraer

        """
        products = []

        print(f"🌐 Iniciando navegador...")

        with sync_playwright() as p:
            # Lanzar navegador
            browser = p.chromium.launch(headless=self.headless)

            # Crear contexto con user agent realista
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='es-MX'
            )

            page = context.new_page()

            try:
                print(f"🔍 Navegando a: {url}")

                # Ir a la página
                page.goto(url, wait_until='networkidle', timeout=60000)

                print(" Esperando que carguen los productos...")
                time.sleep(5)  # Esperar carga de JavaScript

                # Intentar extraer datos del script __NEXT_DATA__
                next_data = page.evaluate('''() => {
                    const script = document.getElementById('__NEXT_DATA__');
                    if (script) {
                        return JSON.parse(script.textContent);
                    }
                    return null;
                }''')

                if next_data:
                    print(" Datos Next.js encontrados")
                    products = self.parse_nextjs_data(next_data)

                # Si no hay datos Next.js, intentar scraping HTML
                if not products:
                    print(" Intentando scraping HTML...")
                    products = self.scrape_html_products(page)

                # Limitar productos
                if max_products:
                    products = products[:max_products]

                print(f" Encontrados {len(products)} productos")

            except PlaywrightTimeout:
                print(" Timeout: La página tardó demasiado en cargar")
            except Exception as e:
                print(f" Error durante scraping: {e}")
            finally:
                browser.close()

        return products

    def parse_nextjs_data(self, data: dict) -> List[Dict]:
        """Extrae productos de __NEXT_DATA__"""
        products = []

        try:
            # Navegar estructura de Next.js (varía por sitio)
            page_props = data.get('props', {}).get('pageProps', {})

            # Intentar diferentes ubicaciones
            product_lists = [
                page_props.get('products', []),
                page_props.get('initialProducts', []),
                page_props.get('productList', []),
                page_props.get('items', []),
            ]

            for product_list in product_lists:
                if product_list and isinstance(product_list, list):
                    for item in product_list:
                        product = self.parse_product(item)
                        if product:
                            products.append(product)
                    break

        except Exception as e:
            print(f"Error parsing Next.js data: {e}")

        return products

    def scrape_html_products(self, page) -> List[Dict]:
        """Fallback: scraping HTML de productos"""
        products = []

        try:
            # Esperar a que aparezcan productos
            page.wait_for_selector('[data-testid*="product"], .product-card, .product-item',
                                   timeout=10000)

            # Evaluar JavaScript para extraer productos
            products_data = page.evaluate('''() => {
                const products = [];
                const productCards = document.querySelectorAll(
                    '[data-testid*="product"], .product-card, .product-item'
                );

                productCards.forEach(card => {
                    const nameElem = card.querySelector('h2, h3, .product-name, [class*="name"]');
                    const imgElem = card.querySelector('img');
                    const priceElem = card.querySelector('[data-testid*="product_mosaico_price"]');

                    if (nameElem || imgElem) {
                        products.push({
                            name: nameElem ? nameElem.textContent.trim() : '',
                            image: imgElem ? (imgElem.src || imgElem.dataset.src) : '',
                            price: priceElem ? priceElem.textContent.trim() : '',
                            id: card.dataset.id || card.dataset.productId || ''
                        });
                    }
                });

                return products;
            }''')

            for item in products_data:
                if item.get('name') or item.get('image'):
                    products.append({
                        'id': item.get('id', ''),
                        'name': item.get('name', ''),
                        'image': item.get('image', ''),
                        'price': item.get('price', ''),
                        'description': '',
                        'brand': '',
                        'category': 'Bebé'
                    })

        except PlaywrightTimeout:
            print(" No se encontraron productos en el HTML")
        except Exception as e:
            print(f"Error en scraping HTML: {e}")

        return products

    def parse_product(self, item: dict) -> Dict:
        """Parsea un producto individual"""
        # Extraer imagen
        image = item.get('image', item.get('imageUrl', item.get('thumbnail', '')))
        if isinstance(image, list) and len(image) > 0:
            image = image[0]

        return {
            'id': str(item.get('id', item.get('sku', item.get('productId', '')))),
            'name': item.get('name', item.get('title', item.get('productName', ''))),
            'description': item.get('description', item.get('desc', '')),
            'image': image,
            'price': str(item.get('price', item.get('salePrice', ''))),
            'brand': item.get('brand', item.get('brandName', '')),
            'category': item.get('category', item.get('categoryName', 'Bebé')),
        }

    def download_image(self, page, url: str, filename: str) -> str:
        """Descarga imagen usando Playwright"""
        if not url:
            return ''

        try:
            # Navegar a la imagen
            response = page.request.get(url)
            
            if response.ok:
                ext = 'jpg'
                content_type = response.headers.get('content-type', '')
                if 'png' in content_type:
                    ext = 'png'
                elif 'webp' in content_type:
                    ext = 'webp'

                image_filename = f"{filename}.{ext}"
                image_path = self.output_dir / image_filename
                
                with open(image_path, 'wb') as f:
                    f.write(response.body())

                return image_filename
        except Exception as e:
            print(f"Error descargando imagen: {e}")

        return ''

    def scrape_and_save(
        self,
        url: str,
        output_csv: str = "productos_coppel.csv",
        download_images: bool = False,
        max_products: int = 20
    ) -> pd.DataFrame:
        """Scrape y guarda productos en CSV"""

        print("=" * 60)
        print(" SCRAPER DE COPPEL CON PLAYWRIGHT")
        print("=" * 60)

        # Scrape productos
        products = self.scrape_products(url, max_products)

        if not products:
            print("\n No se pudieron extraer productos")
            print(" Usa el generador de ejemplos: generar_productos_ejemplo.py")
            return pd.DataFrame()

        print(f"\n Productos extraídos: {len(products)}")

        # Descargar imágenes si se solicita
        if download_images and products:
            print("\n Descargando imágenes...")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                for i, product in enumerate(products):
                    if product.get('image'):
                        name_image = self.extraer_path_imagen_coppel(product['image'])
                        image_file = self.download_image(page, product['image'], name_image)
                        product['image_file'] = image_file
                        time.sleep(0.5)
                    else:
                        product['image_file'] = ''

                browser.close()

        # Crear DataFrame
        df = pd.DataFrame(products)

        # Renombrar columnas
        if 'image_file' in df.columns:
            df = df.rename(columns={'image_file': 'image'})

        # Guardar CSV
        df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"\n Productos guardados en: {output_csv}")

        return df


def main():
    """Función principal"""

    print("  NOTA: Este scraper requiere Playwright instalado")
    print("  Ejecuta: uv run playwright install chromium\n")

    url = "https://www.coppel.com/sd/RB2315EPMTPEBEBALOOKS"

    scraper = CoppelScraperPlaywright(headless=True)

    try:
        df = scraper.scrape_and_save(
            url=url,
            output_csv="productos_coppel.csv",
            download_images=True,  # Cambiar a True para descargar imágenes
            max_products=60
        )

        if not df.empty:
            print("\n" + "=" * 60)
            print("PRIMEROS PRODUCTOS:")
            print("=" * 60)
            print(df[['id', 'name', 'price']].head())

    except Exception as e: 
        print(f"\n Error: {e}")
        print("\n ALTERNATIVA: Usa el generador de ejemplos")
        print("   uv run python generar_productos_ejemplo.py")

if __name__ == "__main__":
    main()
