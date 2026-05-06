# Scheduler Diario de Llamadas a APIs

Este script en Python permite programar llamadas a APIs de manera **concurrente**, registrando **éxitos y errores** tanto en **archivo de log** como en **consola**.  
Es ideal para automatizar tareas diarias de consulta a APIs.

---

## 📦 Requisitos

- Python 3.8 o superior
- pip

Se recomienda crear un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
⚡ Instalación de dependencias
Crea un archivo requirements.txt con el siguiente contenido:

aiohttp
pydantic
Luego ejecuta:

pip install -r requirements.txt
🛠 Archivos necesarios
main.py → Script principal

helper.py → Contiene la función seconds_until(hour, minute) para calcular segundos hasta la próxima ejecución.

day_schema.py → Contiene la clase Schedule (Pydantic) con hour y minute.

Ejemplo de day_schema.py:

from pydantic import BaseModel

class Schedule(BaseModel):
    hour: int
    minute: int
Ejemplo de helper.py:

from datetime import datetime, timedelta

def seconds_until(hour: int, minute: int) -> int:
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target < now:
        target += timedelta(days=1)
    return int((target - now).total_seconds())
🚀 Cómo ejecutar el script
El script utiliza argumentos CLI para definir la hora y minuto de ejecución diaria.

python main.py --hour <HORA> --minute <MINUTO>
--hour → Hora de ejecución (0-23)

--minute → Minuto de ejecución (0-59, opcional, por defecto 0)

Ejemplo: ejecutar todos los días a las 14:30

python main.py --hour 14 --minute 30
