import asyncio
from typing import List
import aiohttp
import logging
import argparse
import traceback
from datetime import datetime

from pydantic import ValidationError
from day_schema import Schedule
from helper import seconds_until

# Logging: archivo + consola
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Handler para archivo
file_handler = logging.FileHandler("api_calls.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# Añadir handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Función async para llamar a la API y registrar fallos con detalle
async def call_api(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            data = await response.text()
            logging.info(f"Éxito: {url}")
            return data
    except Exception as e:
        now = datetime.now().isoformat()
        error_detail = ''.join(traceback.format_exception_only(type(e), e)).strip()
        logging.error(f"Fallo en {url} a las {now}. Motivo: {error_detail}")
        return None

# Función para llamar varias APIs concurrentemente
async def call_apis(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [call_api(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Revisar excepciones no manejadas
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                now = datetime.now().isoformat()
                logging.error(f"Excepción no manejada en {urls[i]} a las {now}: {result}")
        return results

# Scheduler diario
async def task(urls: List[str], schedule: Schedule):
    while True:
        wait_time = seconds_until(schedule.hour, schedule.minute)
        logging.info(f"Esperando {wait_time} segundos hasta la siguiente ejecución")
        await asyncio.sleep(wait_time)
        logging.info("Iniciando llamadas a APIs")
        await call_apis(urls)

# Ejecución principal con argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduler diario de llamadas a APIs.")
    parser.add_argument("--hour", type=int, required=True, help="Hora de ejecución (0-23)")
    parser.add_argument("--minute", type=int, default=0, help="Minuto de ejecución (0-59)")
    args = parser.parse_args()

    try:
        schedule = Schedule(hour=args.hour, minute=args.minute)
        api_urls = [
            "https://jsonplaceholder.typicode.com/posts/1",  # éxito
            "https://jsonplaceholder.typicode.com/posts/2",  # éxito
            "https://httpbin.org/status/500"                 # fallo intencionado
        ]
        try:
            asyncio.run(task(api_urls, schedule))
        except KeyboardInterrupt:
            logging.info("Scheduler detenido por el usuario (Ctrl+C)")
            print("Scheduler detenido por el usuario")
    except ValidationError as ve:
        logging.error(f"Error de configuración: {ve}")
        print("Error de configuración:", ve)
    except Exception as e:
        logging.error(f"Error inesperado en el scheduler: {e}")
        print("Error inesperado:", e)