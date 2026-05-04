from pydantic import BaseModel, field_validator

class Schedule(BaseModel):
    hour: int
    minute: int = 0

    @field_validator('hour')
    @classmethod
    def hour_valid(cls, v):
        if not 0 <= v <= 23:
            raise ValueError("La hora debe estar entre 0 y 23")
        return v

    @field_validator('minute')
    @classmethod
    def minute_valid(cls, v):
        if not 0 <= v <= 59:
            raise ValueError("Los minutos deben estar entre 0 y 59")
        return v

