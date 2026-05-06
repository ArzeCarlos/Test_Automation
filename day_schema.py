from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

class Schedule(BaseModel):
    daily: bool
    # Para modo diario (daily=True)
    hour: Optional[int] = None
    minute: Optional[int] = 0
    # Para modo intra-diario (daily=False)
    interval_minutes: Optional[int] = None

    @field_validator('hour')
    @classmethod
    def hour_valid(cls, v):
        if v is not None and not 0 <= v <= 23:
            raise ValueError("La hora debe estar entre 0 y 23")
        return v

    @field_validator('minute')
    @classmethod
    def minute_valid(cls, v):
        if v is not None and not 0 <= v <= 59:
            raise ValueError("Los minutos deben estar entre 0 y 59")
        return v

    @field_validator('interval_minutes')
    @classmethod
    def interval_valid(cls, v):
        if v is not None and v < 1:
            raise ValueError("El intervalo debe ser al menos 1 minuto")
        return v

    @model_validator(mode='after')
    def check_mode_fields(self):
        if self.daily:
            if self.hour is None:
                raise ValueError("En modo diario se requiere --hour")
        else:
            if self.interval_minutes is None:
                raise ValueError("En modo intra-diario se requiere --interval")
        return self