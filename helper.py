# Calcula segundos hasta la próxima ejecución
from datetime import datetime, timedelta


def seconds_until(hour: int, minute: int = 0):
    now = datetime.now() # Toma la hora del servidor
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()
