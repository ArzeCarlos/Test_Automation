from datetime import datetime, timedelta

def seconds_until(hour: int, minute: int = 0) -> float:
    """Calcula los segundos hasta la próxima ocurrencia de hour:minute (modo diario)."""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    delta = (target - now).total_seconds()
    return max(delta, 1.0)

def seconds_until_first_run() -> float:
    """Calcula los segundos hasta el próximo múltiplo de 5 minutos (primera ejecución).
    
    Ejemplo: si son las 1:38 → espera hasta las 1:40.
    """
    now = datetime.now()
    next_multiple = (now.minute // 5 + 1) * 5
    next_time = now.replace(second=0, microsecond=0) + timedelta(minutes=(next_multiple - now.minute))
    return max((next_time - now).total_seconds(), 1.0)

def seconds_until_interval(interval_minutes: int) -> float:
    """Espera exactamente interval_minutes desde la última ejecución."""
    return interval_minutes * 60.0