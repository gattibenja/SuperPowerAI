#archivo donde se validan las inputs del frontend y lo que devuelve la api en si 


from typing import Literal

from pydantic import BaseModel, Field

class PacienteCreate(BaseModel): 
    nombre: str = Field(description="El nombre del paciente")
    apellido: str = Field(description="El apellido del paciente")
    edad: int = Field(description="La edad del paciente")
    telefono: str = Field(description="El telefono del paciente")
    genero: str = Field(description="El genero del paciente")
    saldo: float = Field(description="El saldo del paciente")


class PacienteLoteCreate(BaseModel):
    pacientes: list[PacienteCreate]


class PacienteLoteItemResponse(BaseModel):
    ok: bool
    mensaje: str
    id: int | None = None
    nombre: str
    apellido: str


class PacienteLoteResponse(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[PacienteLoteItemResponse]


class PacienteRecordatorioLoteItemCreate(BaseModel):
    paciente: PacienteCreate
    fecha: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha del recordatorio con formato DD-MM-YYYY",
    )
    descripcion: str


class PacienteRecordatorioLoteCreate(BaseModel):
    items: list[PacienteRecordatorioLoteItemCreate]


class PacienteRecordatorioLoteItemResponse(BaseModel):
    ok: bool
    mensaje: str
    paciente_id: int | None = None
    recordatorio_id: int | None = None
    apellido: str


class PacienteRecordatorioLoteResponse(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[PacienteRecordatorioLoteItemResponse]


class CobrarTurnoLoteItemCreate(BaseModel):
    recordatorio_id: int = Field(ge=1)
    monto_cobrado: float = Field(gt=0)
    fecha_cobro: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha de cobro DD-MM-YYYY opcional",
    )


class CobrarTurnoLoteCreate(BaseModel):
    cobros: list[CobrarTurnoLoteItemCreate]


class CobrarTurnoLoteItemResponse(BaseModel):
    ok: bool
    mensaje: str
    recordatorio_id: int
    id: int | None = None
    paciente_id: int | None = None
    paciente_apellido: str | None = None
    fecha_turno: str | None = None
    fecha_cobro: str | None = None
    descripcion: str | None = None
    monto_cobrado: float | None = None


class CobrarTurnoLoteResponse(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[CobrarTurnoLoteItemResponse]
    
