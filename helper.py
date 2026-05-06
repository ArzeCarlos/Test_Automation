from datetime import datetime, timedelta

def seconds_until(hour: int, minute: int = 0) -> float:
    """Calcula los segundos hasta la próxima ocurrencia de hour:minute (modo diario)."""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    delta = (target - now).total_seconds()
    return max(delta, 1.0)

def seconds_until_interval(interval_minutes: int) -> float:
    """Calcula los segundos hasta el próximo múltiplo del intervalo (modo intra-diario).
    
    Ejemplo: con interval_minutes=15, ejecuta en :00, :15, :30, :45 de cada hora.
    """
    now = datetime.now()
    total_minutes = now.hour * 60 + now.minute
    next_slot = (total_minutes // interval_minutes + 1) * interval_minutes

    next_time = now.replace(second=0, microsecond=0) + timedelta(
        minutes=(next_slot - total_minutes)
    )
    delta = (next_time - now).total_seconds()
    return max(delta, 1.0)