from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

#archivo donde se definen los modelos de datos que se van a utilizar en la base de datos, como el modelo de paciente, que es el que se va a utilizar para crear la tabla de pacientes en la base de datos.

class Paciente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    edad: int
    telefono: str
    genero: str
    saldo: float = 0.0
    

class Recordatorio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    paciente_id: int
    fecha: str
    descripcion: str
    estado: str = "pendiente"
    monto_cobrado: float = 0.0
    fecha_cobro: Optional[str] = None


class MovimientoFinanciero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: date
    categoria: str  # ingreso | costo_variable
    concepto: str
    monto: float
    notas: Optional[str] = None


class CostoFijoMensual(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    monto_mensual: float
    activo: bool = True


class InversionFinanciera(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: date
    nombre: str
    monto_invertido: float
    retorno_generado: float = 0.0
    notas: Optional[str] = None


