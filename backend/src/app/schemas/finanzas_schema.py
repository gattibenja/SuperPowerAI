from typing import Literal

from pydantic import BaseModel, Field


PeriodoFinanciero = Literal["dia", "semana", "mes", "anio"]


class MovimientoFinancieroCreate(BaseModel):
    fecha: str = Field(description="Fecha con formato DD-MM-YYYY")
    concepto: str = Field(description="Concepto del movimiento")
    monto: float = Field(description="Monto del movimiento")
    notas: str | None = Field(default=None, description="Notas opcionales")


class MovimientoFinancieroLoteCreate(BaseModel):
    categoria: Literal["ingreso", "costo_variable"]
    movimientos: list[MovimientoFinancieroCreate]


class MovimientoFinancieroItemOutput(BaseModel):
    ok: bool
    mensaje: str
    id: int | None = None
    fecha: str
    categoria: str
    concepto: str
    monto: float
    notas: str | None = None


class MovimientoFinancieroLoteOutput(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[MovimientoFinancieroItemOutput]


class CostoFijoMensualCreate(BaseModel):
    nombre: str = Field(description="Nombre del costo fijo")
    monto_mensual: float = Field(description="Monto mensual del costo fijo")
    activo: bool = Field(default=True, description="Si el costo esta activo")


class InversionFinancieraCreate(BaseModel):
    fecha: str = Field(description="Fecha con formato DD-MM-YYYY")
    nombre: str = Field(description="Nombre de la inversion")
    monto_invertido: float = Field(description="Monto invertido")
    retorno_generado: float = Field(default=0.0, description="Retorno acumulado")
    notas: str | None = Field(default=None, description="Notas opcionales")


class ResumenFinancieroParams(BaseModel):
    periodo: PeriodoFinanciero = Field(description="Periodo: dia, semana, mes o anio")
    referencia: str | None = Field(
        default=None,
        description="Fecha de referencia con formato DD-MM-YYYY",
    )


class ROICalculoParams(BaseModel):
    desde: str | None = Field(default=None, description="Desde DD-MM-YYYY")
    hasta: str | None = Field(default=None, description="Hasta DD-MM-YYYY")


class ResumenFinancieroOutput(BaseModel):
    periodo: PeriodoFinanciero
    desde: str
    hasta: str
    ingresos: float
    costos_variables: float
    costos_fijos: float
    utilidad_neta: float
    margen_neto: float


class ROIOutput(BaseModel):
    desde: str | None
    hasta: str | None
    total_invertido: float
    total_retorno: float
    ganancia_neta: float
    roi: float
