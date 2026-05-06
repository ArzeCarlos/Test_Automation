import asyncio
from typing import List
import aiohttp
import logging
import argparse
import traceback
from datetime import datetime

from pydantic import ValidationError
from day_schema import Schedule
from helper import seconds_until, seconds_until_first_run, seconds_until_interval

# Logging: archivo + consola
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("api_calls.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


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


async def call_apis(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [call_api(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                now = datetime.now().isoformat()
                logging.error(f"Excepción no manejada en {urls[i]} a las {now}: {result}")
        return results


async def task(urls: List[str], schedule: Schedule):
    if schedule.daily:
        # Modo diario: espera hasta la hora fijada cada 24h
        logging.info(
            f"Modo DIARIO — ejecución programada a las "
            f"{schedule.hour:02d}:{schedule.minute:02d}"
        )
        while True:
            wait_time = seconds_until(schedule.hour, schedule.minute)
            logging.info(f"Esperando {wait_time:.0f}s hasta la siguiente ejecución diaria")
            await asyncio.sleep(wait_time)
            logging.info("Iniciando llamadas a APIs (modo diario)")
            await call_apis(urls)
    else:
        # Modo intra-diario: primera ejecución en el próximo múltiplo de 5min,
        # luego cada interval_minutes
        logging.info(
            f"Modo INTRA-DIARIO — ejecución cada {schedule.interval_minutes} minuto(s)"
        )
        first = True
        while True:
            if first:
                wait_time = seconds_until_first_run()
                logging.info(f"Esperando {wait_time:.0f}s hasta el próximo múltiplo de 5min")
                first = False
            else:
                wait_time = seconds_until_interval(schedule.interval_minutes)
                logging.info(f"Esperando {wait_time:.0f}s hasta la siguiente ejecución")
            await asyncio.sleep(wait_time)
            logging.info(
                f"Iniciando llamadas a APIs "
                f"(intervalo {schedule.interval_minutes}min)"
            )
            await call_apis(urls)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scheduler de llamadas a APIs (diario o intra-diario)."
    )
    parser.add_argument(
        "--daily",
        type=lambda x: x.lower() in ("true", "1", "yes"),
        required=True,
        help="true = modo diario, false = modo intra-diario",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=None,
        help="Hora de ejecución (0-23). Requerido si --daily=true",
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=0,
        help="Minuto de ejecución (0-59). Usado con --daily=true (default: 0)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        dest="interval_minutes",
        help="Intervalo en minutos entre ejecuciones. Requerido si --daily=false",
    )
    args = parser.parse_args()

    try:
        schedule = Schedule(
            daily=args.daily,
            hour=args.hour,
            minute=args.minute,
            interval_minutes=args.interval_minutes,
        )
        api_urls = [
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://jsonplaceholder.typicode.com/posts/2",
            "https://httpbin.org/status/500",
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