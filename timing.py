#!/usr/bin/env python3
"""
Script de Optimización y Gestión de Tiempos para Extracción de Atributos con Gemini
Basado en extraccion_optimizada.ipynb

Características:
- Análisis de tiempos de respuesta
- Optimización automática de rate limiting
- Estimación de tiempo para grandes volúmenes
- Gestión inteligente de cuotas y límites
- Métricas detalladas de rendimiento
"""

import os
import time
import logging
import statistics
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

import pandas as pd
from google import genai
from google.genai import types
from tqdm.auto import tqdm
from dotenv import load_dotenv


@dataclass
class TimingMetrics:
    """Métricas de tiempo y rendimiento"""
    request_times: List[float]
    success_count: int
    error_count: int
    quota_errors: int
    rate_limit_errors: int
    total_processing_time: float
    average_response_time: float
    median_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_minute: float
    estimated_time_per_1000: float


@dataclass
class OptimizationConfig:
    """Configuración optimizada basada en métricas"""
    optimal_delay: float
    batch_size: int
    max_concurrent: int
    checkpoint_frequency: int
    recommended_daily_limit: int


class TimingOptimizer:
    """Optimizador de tiempos y gestión de cuotas"""
    
    def __init__(self):
        self.setup_logging()
        self.load_config()
        self.initialize_client()
        self.metrics_history: List[TimingMetrics] = []
        self.current_session_times: List[float] = []
        self.session_start = time.time()
        
    def setup_logging(self):
        """Configurar logging con más detalles"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'timing_optimization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Cargar configuración"""
        load_dotenv()
        
        # Configuración base de la notebook
        self.GEMINI_MODEL = 'gemini-2.5-flash'
        self.MAX_RETRIES = 5
        self.BASE_DELAY = 1.5  # Empezar más agresivo
        self.INITIAL_RATE_LIMIT = 1.0  # Delay inicial más bajo
        self.IMAGE_DIRECTORY = Path('images')
        self.PROMPT_FILE = Path('prompt_api.txt')
        
        # Nuevas configuraciones para optimización
        self.QUOTA_LIMIT_FREE_TIER = 10  # Requests per minute for free tier
        self.OPTIMIZATION_SAMPLE_SIZE = 10  # Número de requests para calcular métricas
        self.TARGET_SUCCESS_RATE = 0.95  # 95% de éxito objetivo
        
    def initialize_client(self):
        """Inicializar cliente de Gemini"""
        try:
            self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
            self.logger.info("Cliente de Gemini inicializado correctamente")
        except Exception as e:
            self.logger.error(f"Error al inicializar cliente de Gemini: {e}")
            raise
            
    def load_prompt(self) -> str:
        """Cargar prompt desde archivo"""
        try:
            with open(self.PROMPT_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.logger.error(f"Error al cargar prompt: {e}")
            raise
            
    def get_mime_type(self, image_path: Path) -> str:
        """Determinar tipo MIME de imagen"""
        extension = image_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return mime_types.get(extension, 'image/jpeg')
        
    def process_single_request(self, image_path: Path, prompt: str) -> Tuple[str, float, bool]:
        """
        Procesar una sola request midiendo tiempo y éxito
        
        Returns:
            (response, time_taken, success)
        """
        if not image_path.exists():
            return f"ERROR_IMAGEN: Archivo no encontrado", 0.0, False
            
        try:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
        except Exception as e:
            return f"ERROR_LECTURA: {str(e)}", 0.0, False
            
        mime_type = self.get_mime_type(image_path)
        contents = [
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(text=prompt)
        ]
        
        start_time = time.time()
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.GEMINI_MODEL,
                    contents=contents
                )
                
                end_time = time.time()
                time_taken = end_time - start_time
                
                return response.text.strip().replace('\n', ' '), time_taken, True
                
            except Exception as e:
                error_message = str(e)
                
                # Detectar errores de cuota
                if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                    self.logger.warning(f"Cuota excedida en intento {attempt + 1}")
                    if attempt < self.MAX_RETRIES - 1:
                        # Esperar más tiempo en errores de cuota
                        wait_time = self.BASE_DELAY * (3 ** attempt)  # Backoff más agresivo
                        self.logger.info(f"Esperando {wait_time}s por cuota...")
                        time.sleep(wait_time)
                    continue
                    
                # Otros errores
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.BASE_DELAY * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    end_time = time.time()
                    return f"ERROR_API: {error_message}", end_time - start_time, False
                    
        return "ERROR_INESPERADO", time.time() - start_time, False
        
    def run_timing_test(self, num_samples: int = 10) -> TimingMetrics:
        """
        Ejecutar test de timing con un número específico de muestras
        """
        self.logger.info(f"🚀 Iniciando test de timing con {num_samples} muestras")
        
        # Cargar prompt
        prompt = self.load_prompt()
        
        # Obtener imágenes de muestra
        sample_images = list(self.IMAGE_DIRECTORY.glob("*.jpg"))[:num_samples]
        if len(sample_images) < num_samples:
            self.logger.warning(f"Solo se encontraron {len(sample_images)} imágenes de {num_samples} solicitadas")
            
        request_times = []
        success_count = 0
        error_count = 0
        quota_errors = 0
        rate_limit_errors = 0
        
        test_start = time.time()
        
        with tqdm(total=len(sample_images), desc="Test de timing") as pbar:
            for i, image_path in enumerate(sample_images):
                self.logger.info(f"Procesando muestra {i+1}/{len(sample_images)}: {image_path.name}")
                
                response, time_taken, success = self.process_single_request(image_path, prompt)
                
                request_times.append(time_taken)
                
                if success:
                    success_count += 1
                    self.logger.info(f"✅ Éxito en {time_taken:.2f}s")
                else:
                    error_count += 1
                    if "429" in response or "RESOURCE_EXHAUSTED" in response:
                        quota_errors += 1
                    elif "RATE_LIMIT" in response:
                        rate_limit_errors += 1
                    self.logger.error(f"❌ Error: {response[:100]}")
                    
                # Rate limiting adaptativo
                if i < len(sample_images) - 1:  # No esperar después del último
                    delay = self.calculate_adaptive_delay(request_times, success_count, error_count)
                    time.sleep(delay)
                    
                pbar.update(1)
                
        total_time = time.time() - test_start
        
        # Calcular métricas
        if request_times:
            avg_time = statistics.mean(request_times)
            median_time = statistics.median(request_times)
            min_time = min(request_times)
            max_time = max(request_times)
            requests_per_minute = len(request_times) / (total_time / 60)
            estimated_time_per_1000 = (avg_time + self.INITIAL_RATE_LIMIT) * 1000 / 60  # en minutos
        else:
            avg_time = median_time = min_time = max_time = 0
            requests_per_minute = 0
            estimated_time_per_1000 = 0
            
        metrics = TimingMetrics(
            request_times=request_times,
            success_count=success_count,
            error_count=error_count,
            quota_errors=quota_errors,
            rate_limit_errors=rate_limit_errors,
            total_processing_time=total_time,
            average_response_time=avg_time,
            median_response_time=median_time,
            min_response_time=min_time,
            max_response_time=max_time,
            requests_per_minute=requests_per_minute,
            estimated_time_per_1000=estimated_time_per_1000
        )
        
        self.metrics_history.append(metrics)
        return metrics
        
    def calculate_adaptive_delay(self, recent_times: List[float], success_count: int, error_count: int) -> float:
        """Calcular delay adaptativo basado en métricas recientes"""
        if not recent_times:
            return self.INITIAL_RATE_LIMIT
            
        # Tasa de éxito actual
        total_requests = success_count + error_count
        success_rate = success_count / total_requests if total_requests > 0 else 0
        
        # Tiempo promedio reciente (últimas 5 requests)
        recent_avg = statistics.mean(recent_times[-5:]) if len(recent_times) >= 5 else statistics.mean(recent_times)
        
        # Ajustar delay basado en tasa de éxito y tiempo de respuesta
        if success_rate >= self.TARGET_SUCCESS_RATE:
            # Si va bien, ser más agresivo
            adaptive_delay = max(0.5, self.INITIAL_RATE_LIMIT * 0.8)
        elif success_rate >= 0.8:
            # Mantener delay actual
            adaptive_delay = self.INITIAL_RATE_LIMIT
        else:
            # Si hay muchos errores, ser más conservador
            adaptive_delay = self.INITIAL_RATE_LIMIT * 1.5
            
        # Ajustar por tiempo de respuesta (si es muy lento, esperar más)
        if recent_avg > 3.0:  # Si toma más de 3 segundos
            adaptive_delay *= 1.3
            
        return adaptive_delay
        
    def optimize_configuration(self, metrics: TimingMetrics) -> OptimizationConfig:
        """Generar configuración optimizada basada en métricas"""
        success_rate = metrics.success_count / (metrics.success_count + metrics.error_count)
        
        # Calcular delay óptimo
        if success_rate >= 0.95:
            optimal_delay = max(0.5, metrics.average_response_time * 0.1)
        elif success_rate >= 0.8:
            optimal_delay = metrics.average_response_time * 0.3
        else:
            optimal_delay = metrics.average_response_time * 0.5
            
        # Tamaño de batch basado en cuota
        if metrics.quota_errors > 0:
            batch_size = max(5, self.QUOTA_LIMIT_FREE_TIER - 2)
        else:
            batch_size = self.QUOTA_LIMIT_FREE_TIER
            
        # Configuración de checkpoints
        checkpoint_freq = max(1, batch_size // 2)
        
        # Límite diario estimado (considerando cuotas por minuto)
        daily_minutes = 24 * 60
        requests_per_minute_safe = min(batch_size, self.QUOTA_LIMIT_FREE_TIER * 0.8)
        recommended_daily = int(daily_minutes * requests_per_minute_safe * 0.9)  # 90% del máximo teórico
        
        return OptimizationConfig(
            optimal_delay=optimal_delay,
            batch_size=batch_size,
            max_concurrent=1,  # Mantener secuencial para free tier
            checkpoint_frequency=checkpoint_freq,
            recommended_daily_limit=recommended_daily
        )
        
    def estimate_processing_time(self, total_products: int, metrics: TimingMetrics) -> Dict[str, Any]:
        """Estimar tiempo de procesamiento para un volumen dado"""
        if metrics.success_count == 0:
            return {"error": "No hay datos suficientes para estimar"}
            
        # Tiempo promedio por request (incluyendo delays)
        time_per_request = metrics.average_response_time + self.INITIAL_RATE_LIMIT
        
        # Considerar tasa de errores para reintentos
        success_rate = metrics.success_count / (metrics.success_count + metrics.error_count)
        effective_time_per_request = time_per_request / success_rate
        
        # Cálculos de tiempo
        total_seconds = total_products * effective_time_per_request
        total_minutes = total_seconds / 60
        total_hours = total_minutes / 60
        total_days = total_hours / 24
        
        # Considerando límites de cuota
        daily_limit = self.QUOTA_LIMIT_FREE_TIER * 60 * 24 * 0.8  # 80% del límite teórico
        days_by_quota = total_products / daily_limit
        
        # El tiempo real será el mayor entre el tiempo de procesamiento y las restricciones de cuota
        realistic_days = max(total_days, days_by_quota)
        
        return {
            "total_products": total_products,
            "estimated_time": {
                "seconds": total_seconds,
                "minutes": total_minutes,
                "hours": total_hours,
                "days": total_days
            },
            "quota_limited_time": {
                "days": days_by_quota,
                "realistic_days": realistic_days
            },
            "performance_metrics": {
                "requests_per_minute": metrics.requests_per_minute,
                "success_rate": success_rate,
                "average_response_time": metrics.average_response_time
            },
            "recommendations": {
                "daily_processing_limit": int(daily_limit),
                "optimal_batch_size": min(50, int(daily_limit / 20)),
                "checkpoint_frequency": "cada 10 productos"
            }
        }
        
    def print_detailed_report(self, metrics: TimingMetrics, optimization: OptimizationConfig):
        """Imprimir reporte detallado"""
        print("\n" + "="*80)
        print("📊 REPORTE DETALLADO DE TIMING Y OPTIMIZACIÓN")
        print("="*80)
        
        # Métricas de rendimiento
        print(f"\n🚀 MÉTRICAS DE RENDIMIENTO:")
        print(f"  Total de requests: {metrics.success_count + metrics.error_count}")
        print(f"  ✅ Exitosos: {metrics.success_count}")
        print(f"  ❌ Errores: {metrics.error_count}")
        print(f"  📈 Tasa de éxito: {metrics.success_count/(metrics.success_count + metrics.error_count)*100:.1f}%")
        
        print(f"\n⏱️  TIEMPOS DE RESPUESTA:")
        print(f"  Promedio: {metrics.average_response_time:.2f}s")
        print(f"  Mediana: {metrics.median_response_time:.2f}s")
        print(f"  Mínimo: {metrics.min_response_time:.2f}s")
        print(f"  Máximo: {metrics.max_response_time:.2f}s")
        
        print(f"\n📊 THROUGHPUT:")
        print(f"  Requests por minuto: {metrics.requests_per_minute:.1f}")
        print(f"  Tiempo estimado por 1000 productos: {metrics.estimated_time_per_1000:.1f} minutos")
        
        print(f"\n🔧 CONFIGURACIÓN OPTIMIZADA:")
        print(f"  Delay óptimo: {optimization.optimal_delay:.2f}s")
        print(f"  Tamaño de batch: {optimization.batch_size}")
        print(f"  Frecuencia de checkpoint: cada {optimization.checkpoint_frequency} productos")
        print(f"  Límite diario recomendado: {optimization.recommended_daily_limit:,} productos")
        
        # Errores específicos
        if metrics.quota_errors > 0:
            print(f"\n⚠️  ERRORES DE CUOTA: {metrics.quota_errors}")
            print("  Recomendación: Aumentar delays o considerar upgrade de plan")
            
        if metrics.rate_limit_errors > 0:
            print(f"\n⚠️  ERRORES DE RATE LIMIT: {metrics.rate_limit_errors}")
            print("  Recomendación: Implementar backoff exponencial más agresivo")
            
    def run_volume_estimation(self, volumes: List[int] = None):
        """Ejecutar estimaciones para diferentes volúmenes"""
        if volumes is None:
            volumes = [100, 1000, 10000, 50000, 100000]
            
        if not self.metrics_history:
            self.logger.error("No hay métricas disponibles. Ejecuta primero un test de timing.")
            return
            
        latest_metrics = self.metrics_history[-1]
        
        print("\n" + "="*80)
        print("📈 ESTIMACIONES DE TIEMPO PARA DIFERENTES VOLÚMENES")
        print("="*80)
        
        for volume in volumes:
            estimation = self.estimate_processing_time(volume, latest_metrics)
            if "error" in estimation:
                print(f"\n❌ Error para {volume:,} productos: {estimation['error']}")
                continue
                
            print(f"\n📦 VOLUMEN: {volume:,} productos")
            print(f"  ⏱️  Tiempo estimado: {estimation['estimated_time']['days']:.1f} días")
            print(f"  🚦 Tiempo realista (con cuotas): {estimation['quota_limited_time']['realistic_days']:.1f} días")
            print(f"  📊 Límite diario recomendado: {estimation['recommendations']['daily_processing_limit']:,}")
            
    def save_metrics_report(self, filename: str = None):
        """Guardar reporte de métricas en JSON"""
        if filename is None:
            filename = f"timing_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        if not self.metrics_history:
            self.logger.warning("No hay métricas para guardar")
            return
            
        # Convertir métricas a diccionario serializable
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_configuration": {
                "model": self.GEMINI_MODEL,
                "quota_limit": self.QUOTA_LIMIT_FREE_TIER,
                "sample_size": len(self.metrics_history[-1].request_times)
            },
            "metrics": [asdict(m) for m in self.metrics_history],
            "optimization": asdict(self.optimize_configuration(self.metrics_history[-1]))
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"📄 Reporte guardado en: {filename}")


def main():
    """Función principal del script"""
    print("🚀 Iniciando Optimizador de Timing para Extracción de Atributos")
    print("="*80)
    
    optimizer = TimingOptimizer()
    
    # Configurar número de muestras para el test
    sample_sizes = [5, 10, 20]  # Diferentes tamaños de muestra
    
    for sample_size in sample_sizes:
        print(f"\n🧪 Ejecutando test con {sample_size} muestras...")
        
        try:
            # Ejecutar test de timing
            metrics = optimizer.run_timing_test(sample_size)
            
            # Generar configuración optimizada
            optimization = optimizer.optimize_configuration(metrics)
            
            # Mostrar reporte
            optimizer.print_detailed_report(metrics, optimization)
            
            # Estimaciones de volumen
            optimizer.run_volume_estimation()
            
            # Guardar métricas
            optimizer.save_metrics_report(f"timing_report_{sample_size}_samples.json")
            
        except Exception as e:
            optimizer.logger.error(f"Error en test de {sample_size} muestras: {e}")
            continue
    
    print("\n✅ Optimización completada. Revisa los archivos de reporte generados.")


if __name__ == "__main__":
    main()