#!/usr/bin/env python3
"""
Script interactivo para configurar Gemini API
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def print_header(text):
    """Imprime un header bonito"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(number, text):
    """Imprime un paso numerado"""
    print(f"\n{'─' * 60}")
    print(f"📍 PASO {number}: {text}")
    print('─' * 60)


def check_env_file():
    """Verifica si existe .env"""
    env_path = Path('.env')
    env_example = Path('.env.example')

    print_step(1, "Verificando archivo .env")

    if env_path.exists():
        print("✅ Archivo .env encontrado")
        return True
    else:
        print("⚠️  Archivo .env NO encontrado")

        if env_example.exists():
            print("\n💡 Se encontró .env.example")
            response = input("¿Quieres crear .env desde .env.example? (s/n): ")

            if response.lower() in ['s', 'si', 'y', 'yes']:
                env_example.rename(env_path)
                print("✅ Archivo .env creado")
                return True
        else:
            print("\n💡 Creando .env desde cero...")
            with open(env_path, 'w') as f:
                f.write("# Google Gemini API Key\n")
                f.write("# Obtén tu API key en: https://aistudio.google.com/app/apikey\n")
                f.write("GEMINI_API_KEY=\n")
            print("✅ Archivo .env creado")
            return True

    return False


def get_api_key():
    """Obtiene o solicita la API key"""
    print_step(2, "Configurando API Key de Gemini")

    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if api_key and len(api_key) > 10:
        print(f"✅ API Key encontrada en .env")
        print(f"   Longitud: {len(api_key)} caracteres")
        print(f"   Inicia con: {api_key[:15]}...")

        response = input("\n¿Quieres usar esta API key? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            return api_key

    print("\n🔑 Necesitas obtener una API Key de Google Gemini")
    print("\n📋 Instrucciones:")
    print("1. Abre tu navegador")
    print("2. Ve a: https://aistudio.google.com/app/apikey")
    print("3. Inicia sesión con tu cuenta de Google")
    print("4. Haz clic en 'Create API Key'")
    print("5. Selecciona 'Create API key in new project'")
    print("6. Copia la API key generada")

    print("\n" + "─" * 60)
    input("Presiona ENTER cuando hayas copiado tu API key...")

    api_key = input("\nPega tu API Key aquí: ").strip()

    if len(api_key) < 20:
        print("\n❌ La API key parece muy corta")
        print("   Una API key típica tiene ~39 caracteres")
        sys.exit(1)

    # Guardar en .env
    env_content = []
    env_path = Path('.env')

    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.readlines()

    # Actualizar o agregar GEMINI_API_KEY
    key_found = False
    for i, line in enumerate(env_content):
        if line.startswith('GEMINI_API_KEY'):
            env_content[i] = f"GEMINI_API_KEY={api_key}\n"
            key_found = True
            break

    if not key_found:
        env_content.append(f"\nGEMINI_API_KEY={api_key}\n")

    with open(env_path, 'w') as f:
        f.writelines(env_content)

    print("\n✅ API Key guardada en .env")
    return api_key


def test_connection(api_key):
    """Prueba la conexión con Gemini"""
    print_step(3, "Probando conexión con Gemini")

    try:
        from google import genai

        print("⏳ Conectando con Gemini...")
        client = genai.Client(api_key=api_key)

        print("⏳ Enviando mensaje de prueba...")
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents='Responde solo con: OK'
        )

        print("\n✅ ¡CONEXIÓN EXITOSA!")
        print(f"   Respuesta de Gemini: {response.text}")
        return True

    except ImportError:
        print("\n❌ Módulo 'google-generativeai' no instalado")
        print("   Ejecuta: uv sync")
        return False

    except Exception as e:
        error_str = str(e)

        if '401' in error_str or 'API_KEY_INVALID' in error_str:
            print("\n❌ API Key inválida")
            print("   Verifica que copiaste la API key correctamente")
        elif '429' in error_str:
            print("\n⚠️  Rate limit excedido")
            print("   Espera 1 minuto e intenta de nuevo")
        else:
            print(f"\n❌ Error: {e}")

        return False


def check_files():
    """Verifica que existan los archivos necesarios"""
    print_step(4, "Verificando archivos del proyecto")

    files_to_check = {
        'productos.csv': '📄 CSV de productos',
        'images/': '📂 Directorio de imágenes',
        'prompt_api.txt': '📝 Archivo de prompt',
        'extraccion_optimizada.ipynb': '📓 Notebook de extracción'
    }

    all_ok = True

    for file, description in files_to_check.items():
        path = Path(file)
        if path.exists():
            if path.is_dir():
                num_files = len(list(path.glob('*.jpg'))) + len(list(path.glob('*.png')))
                print(f"✅ {description} ({num_files} imágenes)")
            else:
                print(f"✅ {description}")
        else:
            print(f"❌ {description} - NO ENCONTRADO")
            all_ok = False

    return all_ok


def show_next_steps():
    """Muestra los próximos pasos"""
    print_step(5, "¡Configuración Completa!")

    print("""
✅ Todo está listo para extraer atributos

🚀 PRÓXIMOS PASOS:

1️⃣  Abrir el notebook de extracción:
   uv run jupyter notebook extraccion_optimizada.ipynb

2️⃣  Ejecutar todas las celdas (Shift+Enter)

3️⃣  Esperar ~2-3 minutos mientras procesa

4️⃣  Obtener productos_con_atributos.csv con todos los atributos

📊 CONFIGURACIÓN ACTUAL:

• Modelo: gemini-2.0-flash-exp
• Productos: 20 productos de Coppel
• Imágenes: Reales descargadas
• Tiempo estimado: 2-3 minutos
• Costo: $0.00 (GRATIS)

📚 DOCUMENTACIÓN:

• REQUISITOS_GEMINI.md - Guía completa
• GUIA_USO.md - Cómo usar el sistema
• EXITO_SCRAPING.md - Cómo se obtuvieron los productos

💡 TIPS:

• Si hay errores, revisa el log: extraccion_atributos.log
• Los productos ya procesados se saltan automáticamente
• Puedes detener y reanudar en cualquier momento

¡ÉXITO! 🎉
    """)


def main():
    """Función principal"""
    print_header("🔧 CONFIGURADOR DE GEMINI API")

    print("""
Este script te ayudará a configurar todo lo necesario para
extraer atributos de los 20 productos de Coppel usando Gemini.

⏱️  Tiempo estimado: 3-5 minutos
    """)

    input("Presiona ENTER para comenzar...")

    # Verificar .env
    if not check_env_file():
        print("\n❌ Error creando archivo .env")
        sys.exit(1)

    # Obtener API key
    api_key = get_api_key()

    # Probar conexión
    if not test_connection(api_key):
        print("\n❌ La configuración no está completa")
        print("   Revisa los errores arriba y vuelve a intentar")
        sys.exit(1)

    # Verificar archivos
    check_files()

    # Mostrar siguientes pasos
    show_next_steps()

    print("\n" + "=" * 60)
    print("  ¡Configuración Completada! ✨")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
