"""
Scraper Avanzado de Coppel con Playwright
Incluye múltiples estrategias anti-detección
"""

import time
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class CoppelScraperAvanzado:
    """Scraper avanzado con técnicas anti-detección"""

    def __init__(self, headless: bool = False, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo  # Milisegundos de retraso entre acciones
        self.output_dir = Path("images")
        self.output_dir.mkdir(exist_ok=True)

    def scrape_products(self, url: str, max_products: int = 20, timeout: int = 30) -> List[Dict]:
        """
        Scrape productos con estrategias anti-detección avanzadas
        """
        products = []

        print(f" Iniciando navegador (headless={self.headless})...")

        with sync_playwright() as p:
            # Lanzar navegador con configuración realista
            browser = p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            )

            # Crear contexto con configuración anti-detección
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='es-MX',
                timezone_id='America/Mexico_City',
                permissions=['geolocation'],
                geolocation={'latitude': 19.4326, 'longitude': -99.1332},  # Ciudad de México
                color_scheme='light',
                extra_http_headers={
                    'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )

            page = context.new_page()

            # Inyectar scripts anti-detección
            page.add_init_script("""
                // Eliminar señales de webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Mockear plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // Mockear idiomas
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['es-MX', 'es', 'en']
                });

                // Chrome runtime
                window.chrome = {
                    runtime: {}
                };

                // Permisos
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            """)

            try:
                print(f" Navegando a: {url}")
                print(f"  Timeout configurado: {timeout}s")

                # Intentar cargar la página
                response = page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)

                if not response:
                    print(" No se recibió respuesta del servidor")
                    return products

                print(f" Respuesta del servidor: {response.status}")

                # Esperar un momento para que cargue JavaScript
                print(" Esperando carga de JavaScript...")
                page.wait_for_timeout(5000)

                # Tomar screenshot para debug
                screenshot_path = Path("debug_screenshot.png")
                page.screenshot(path=str(screenshot_path))
                print(f"📸 Screenshot guardado en: {screenshot_path}")

                # Obtener el HTML para análisis
                html_content = page.content()
                print(f" HTML recibido: {len(html_content)} caracteres")

                # Intentar múltiples métodos de extracción
                print("\n Intentando extraer productos...")

                # Método 1: __NEXT_DATA__
                print("  Método 1: Buscando __NEXT_DATA__...")
                next_data = page.evaluate('''() => {
                    const script = document.getElementById('__NEXT_DATA__');
                    if (script) {
                        try {
                            return JSON.parse(script.textContent);
                        } catch (e) {
                            return null;
                        }
                    }
                    return null;
                }''')

                if next_data:
                    print("  Datos Next.js encontrados!")
                    products = self.parse_nextjs_data(next_data)
                    if products:
                        print(f"   Extraídos {len(products)} productos de Next.js")

                # Método 2: Scripts JSON-LD
                if not products:
                    print("  Método 2: Buscando scripts JSON-LD...")
                    json_ld_scripts = page.evaluate('''() => {
                        const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
                        return scripts.map(s => {
                            try {
                                return JSON.parse(s.textContent);
                            } catch (e) {
                                return null;
                            }
                        }).filter(d => d !== null);
                    }''')

                    if json_ld_scripts:
                        print(f"  Encontrados {len(json_ld_scripts)} scripts JSON-LD")
                        for data in json_ld_scripts:
                            if isinstance(data, dict) and data.get('@type') == 'Product':
                                products.append(self.parse_product_schema(data))

                # Método 3: Selectores CSS comunes
                if not products:
                    print("  Método 3: Buscando con selectores CSS...")
                    products = self.scrape_html_products(page)

                # Método 4: Buscar en window object
                if not products:
                    print("  Método 4: Buscando en window object...")
                    window_data = page.evaluate('''() => {
                        // Buscar variables globales con productos
                        const keys = Object.keys(window);
                        const productKeys = keys.filter(k =>
                            k.toLowerCase().includes('product') ||
                            k.toLowerCase().includes('item') ||
                            k.toLowerCase().includes('catalog')
                        );

                        const data = {};
                        productKeys.forEach(k => {
                            try {
                                data[k] = window[k];
                            } catch (e) {}
                        });

                        return data;
                    }''')

                    if window_data:
                        print(f"    Variables encontradas: {list(window_data.keys())}")

                # Método 5: Network requests
                if not products:
                    print("  Método 5: Intentando capturar requests de API...")
                    print("  Reintentar con monitoreo de red activo")

                # Limitar productos
                if products and max_products:
                    products = products[:max_products]

                if products:
                    print(f"\n Total extraído: {len(products)} productos")
                else:
                    print("\n No se pudieron extraer productos")
                    print("\n DIAGNÓSTICO:")
                    print(f"  - URL cargada: {page.url}")
                    print(f"  - Título: {page.title()}")
                    print(f"  - Estado: {response.status}")

                    # Guardar HTML para análisis
                    html_file = Path("debug_page.html")
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"  - HTML guardado en: {html_file}")

            except PlaywrightTimeout:
                print(f"\n TIMEOUT: La página tardó más de {timeout}s")
                print(" Posibles causas:")
                print("  - Bloqueo por WAF/Cloudflare")
                print("  - Requiere interacción humana (CAPTCHA)")
                print("  - Geolocalización requerida")
                print("  - Cookies/sesión previa necesaria")
            except Exception as e:
                print(f"\n Error durante scraping: {e}")
            finally:
                print("\n Cerrando navegador...")
                browser.close()

        return products

    def parse_nextjs_data(self, data: dict) -> List[Dict]:
        """Extrae productos de __NEXT_DATA__"""
        products = []

        try:
            # Navegar estructura de Next.js
            page_props = data.get('props', {}).get('pageProps', {})

            # Intentar diferentes ubicaciones posibles
            possible_locations = [
                page_props.get('products'),
                page_props.get('initialProducts'),
                page_props.get('productList'),
                page_props.get('items'),
                page_props.get('data', {}).get('products'),
                page_props.get('initialData', {}).get('products'),
            ]

            for product_list in possible_locations:
                if product_list and isinstance(product_list, list):
                    print(f"     Lista de productos encontrada: {len(product_list)} items")
                    for item in product_list:
                        product = self.parse_product_dict(item)
                        if product and product.get('name'):
                            products.append(product)
                    if products:
                        break

        except Exception as e:
            print(f"     Error parsing Next.js data: {e}")

        return products

    def parse_product_schema(self, data: Dict) -> Dict:
        """Parsea un producto desde schema.org JSON-LD"""
        image = data.get('image', '')
        if isinstance(image, list):
            image = image[0] if len(image) > 0 else ''

        offers = data.get('offers', {})
        price = ''
        if isinstance(offers, dict):
            price = str(offers.get('price', offers.get('lowPrice', '')))
        elif isinstance(offers, list) and offers:
            price = str(offers[0].get('price', ''))

        return {
            'id': data.get('sku', data.get('productID', data.get('identifier', ''))),
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'image': image,
            'price': price,
            'brand': data.get('brand', {}).get('name', '') if isinstance(data.get('brand'), dict) else str(data.get('brand', '')),
            'category': data.get('category', 'Bebé'),
        }

    def scrape_html_products(self, page) -> List[Dict]:
        """Extrae productos del HTML"""
        products = []

        try:
            # Selectores comunes para productos
            selectors = [
                '[data-testid*="product"]',
                '[data-testid*="item"]',
                '.product-card',
                '.product-item',
                '[class*="ProductCard"]',
                '[class*="product-card"]',
                'article[class*="product"]',
                'div[class*="ProductItem"]',
            ]

            for selector in selectors:
                count = page.locator(selector).count()
                if count > 0:
                    print(f"    ✅ Selector '{selector}': {count} elementos")

                    products_data = page.evaluate(f'''() => {{
                        const products = [];
                        const cards = document.querySelectorAll('{selector}');

                        cards.forEach((card, index) => {{
                            const nameSelectors = [
                                'h2', 'h3', 'h4',
                                '[class*="name"]',
                                '[class*="title"]',
                                '[data-testid*="name"]'
                            ];

                            const imgSelectors = ['img'];
                            const priceSelectors = [
                                '[class*="price"]',
                                '[data-testid*="price"]'
                            ];

                            let name = '';
                            for (const sel of nameSelectors) {{
                                const elem = card.querySelector(sel);
                                if (elem && elem.textContent.trim()) {{
                                    name = elem.textContent.trim();
                                    break;
                                }}
                            }}

                            let image = '';
                            const imgElem = card.querySelector('img');
                            if (imgElem) {{
                                image = imgElem.src || imgElem.dataset.src || imgElem.dataset.lazySrc || '';
                            }}

                            let price = '';
                            for (const sel of priceSelectors) {{
                                const elem = card.querySelector(sel);
                                if (elem && elem.textContent.trim()) {{
                                    price = elem.textContent.trim();
                                    break;
                                }}
                            }}

                            if (name || image) {{
                                products.push({{
                                    id: card.dataset.id || card.dataset.productId || `PROD${{index + 1}}`,
                                    name: name,
                                    image: image,
                                    price: price,
                                    description: '',
                                    brand: '',
                                    category: 'Bebé'
                                }});
                            }}
                        }});

                        return products;
                    }}''')

                    if products_data:
                        products.extend(products_data)
                        break

        except Exception as e:
            print(f"     Error en scraping HTML: {e}")

        return products

    def parse_product_dict(self, item: dict) -> Dict:
        """Parsea un producto individual"""
        # Extraer imagen
        image = item.get('image', item.get('imageUrl', item.get('thumbnail', item.get('img', ''))))
        if isinstance(image, list) and len(image) > 0:
            image = image[0]
        if isinstance(image, dict):
            image = image.get('url', image.get('src', ''))

        # Extraer precio
        price = item.get('price', item.get('salePrice', item.get('currentPrice', '')))
        if isinstance(price, dict):
            price = price.get('value', price.get('amount', ''))

        return {
            'id': str(item.get('id', item.get('sku', item.get('productId', item.get('code', ''))))),
            'name': item.get('name', item.get('title', item.get('productName', ''))),
            'description': item.get('description', item.get('desc', item.get('shortDescription', ''))),
            'image': str(image),
            'price': str(price),
            'brand': item.get('brand', item.get('brandName', item.get('manufacturer', ''))),
            'category': item.get('category', item.get('categoryName', 'Bebé')),
        }

    def scrape_and_save(
        self,
        url: str,
        output_csv: str = "productos_coppel.csv",
        max_products: int = 20,
        timeout: int = 30
    ) -> pd.DataFrame:
        """Scrape y guarda productos en CSV"""

        print("=" * 60)
        print(" SCRAPER AVANZADO DE COPPEL CON PLAYWRIGHT")
        print("=" * 60)

        # Scrape productos
        products = self.scrape_products(url, max_products, timeout)

        if not products:
            print("\n" + "=" * 60)
            print(" NO SE PUDIERON EXTRAER PRODUCTOS")
            print("=" * 60)
            print("\n RECOMENDACIONES:")
            print("1. Verificar debug_screenshot.png para ver qué cargó")
            print("2. Verificar debug_page.html para analizar estructura")
            print("3. Intentar con headless=False para ver el navegador")
            print("4. Usar el generador de ejemplos:")
            print("   uv run python generar_productos_ejemplo.py")
            return pd.DataFrame()

        print(f"\n Productos extraídos: {len(products)}")

        # Crear DataFrame
        df = pd.DataFrame(products)

        # Guardar CSV
        df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"\n Productos guardados en: {output_csv}")

        return df


def main():
    """Función principal"""

    url = "https://www.coppel.com/sd/RB2315EPMTPEBEBALOOKS"

    # Crear scraper (headless=False para ver el navegador)
    scraper = CoppelScraperAvanzado(
        headless=True,  # Cambiar a False para ver qué pasa
        slow_mo=100     # Delay entre acciones
    )

    try:
        df = scraper.scrape_and_save(
            url=url,
            output_csv="productos_coppel_playwright.csv",
            max_products=20,
            timeout=60  # Timeout más largo
        )

        if not df.empty:
            print("\n" + "=" * 60)
            print("PRODUCTOS EXTRAÍDOS:")
            print("=" * 60)
            print(df[['id', 'name', 'price']].head(10))
            print(f"\nTotal: {len(df)} productos")

    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
