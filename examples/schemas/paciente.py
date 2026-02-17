from pydantic import BaseModel, Field


class Paciente(BaseModel):
    Nombre: str = Field(default="", description="El nombre del paciente")
    Apellido: str = Field(default="", description="El apellido del paciente")
    Enfermedades: list[str] = Field(default=[], description="Las enfermedades del paciente")
    Alergias: list[str] = Field(default=[], description="Las alergias del paciente")
        