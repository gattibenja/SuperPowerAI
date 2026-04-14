#Archivo para definir los modelos de datos que se van a utilizar en el agente de clima, como los parámetros de entrada para las herramientas y el formato de salida del agente.
#Para structured outputs unicamente referido al llm 

from typing import Literal

from pydantic import BaseModel, Field

class cecilia_cura_Output(BaseModel):
    title: str = Field(description="El titulo de la respuesta")
    description: str = Field(description="La descripción de la respuesta")
    tools: list[str] = Field(description="Las herramientas que se han utilizado")


#Clase para definir los parámetros de entrada para las herramientas para el llm
class GetPacienteParams(BaseModel):
    nombre: str = Field(description="El nombre del paciente")
    apellido: str = Field(description="El apellido del paciente")
    edad: int = Field(description="La edad del paciente")
    telefono: str = Field(description="El telefono del paciente")
    genero: str = Field(description="El genero del paciente")
    saldo: float = Field(description="El saldo del paciente")

#Clase para definir el formato de salida del la tool para el llm
class PacienteOutput(BaseModel):
    mensaje: str = Field(description="El mensaje de la respuesta")
    id: int = Field(description="The ID of the patient.")
    nombre: str = Field(description="The name of the patient.")
    apellido: str = Field(description="The surname of the patient.")


class PacienteLoteInput(BaseModel):
    pacientes: list[GetPacienteParams] = Field(
        description="Lista de pacientes para crear en lote"
    )


class PacienteLoteItemOutput(BaseModel):
    ok: bool
    mensaje: str
    id: int | None = None
    nombre: str
    apellido: str


class PacienteLoteOutput(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[PacienteLoteItemOutput]


class RecordatorioInput(BaseModel):
    paciente_apellido: str = Field(
        description="Apellido del paciente al que se le crea el recordatorio"
    )
    fecha: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha del recordatorio con formato DD-MM-YYYY",
    )
    descripcion: str = Field(description="Descripcion del recordatorio")


class RecordatorioOutput(BaseModel):
    mensaje: str = Field(description="Resultado de la operacion")
    id: int = Field(description="ID del recordatorio creado o 0 si hubo error")
    paciente_apellido: str = Field(description="Apellido del paciente")
    fecha: str = Field(description="Fecha del recordatorio")
    descripcion: str = Field(description="Descripcion del recordatorio")


class RecordatorioLoteInput(BaseModel):
    fecha: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha del recordatorio con formato DD-MM-YYYY",
    )
    descripcion: str = Field(description="Descripcion del recordatorio")
    pacientes_apellidos: list[str] = Field(
        description="Lista de apellidos para crear recordatorios en lote"
    )


class RecordatorioLoteItemOutput(BaseModel):
    paciente_apellido: str
    ok: bool
    mensaje: str
    id: int | None = None


class RecordatorioLoteOutput(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[RecordatorioLoteItemOutput]


class TurnosProximasSemanasInput(BaseModel):
    semanas: int = Field(description="Cantidad de semanas a futuro", ge=1)
    limite: int = Field(default=50, ge=1, le=500)
    referencia: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha base DD-MM-YYYY opcional",
    )


class TurnosPeriodoInput(BaseModel):
    desde: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha inicio DD-MM-YYYY",
    )
    hasta: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha fin DD-MM-YYYY",
    )
    limite: int = Field(default=50, ge=1, le=500)


class TurnoItemOutput(BaseModel):
    id: int
    paciente_id: int
    paciente_apellido: str
    fecha: str
    descripcion: str


class TurnosConsultaOutput(BaseModel):
    desde: str
    hasta: str
    total: int
    turnos: list[TurnoItemOutput]


class CompletarTurnoCobradoInput(BaseModel):
    recordatorio_id: int = Field(ge=1)
    monto_cobrado: float = Field(gt=0)
    fecha_cobro: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha de cobro DD-MM-YYYY opcional",
    )


class CompletarTurnoCobradoSimpleInput(BaseModel):
    paciente_apellido: str = Field(description="Apellido del paciente")
    monto_cobrado: float = Field(gt=0)
    fecha_turno: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha del turno DD-MM-YYYY opcional para desambiguar",
    )
    fecha_cobro: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha de cobro DD-MM-YYYY opcional",
    )


class TurnoCobradoItemOutput(BaseModel):
    id: int
    recordatorio_id: int
    paciente_id: int
    paciente_apellido: str
    fecha_turno: str
    fecha_cobro: str
    descripcion: str
    monto_cobrado: float


class TurnosCobradosConsultaOutput(BaseModel):
    desde: str
    hasta: str
    total: int
    total_cobrado: float
    turnos_cobrados: list[TurnoCobradoItemOutput]


class CobrarTurnosLoteInput(BaseModel):
    cobros: list[CompletarTurnoCobradoInput]


class CobroTurnoLoteItemOutput(BaseModel):
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


class CobrarTurnosLoteOutput(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[CobroTurnoLoteItemOutput]


class PacienteRecordatorioLoteItemInput(BaseModel):
    paciente: GetPacienteParams
    fecha: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha del recordatorio con formato DD-MM-YYYY",
    )
    descripcion: str = Field(description="Descripcion del recordatorio")


class PacienteRecordatorioLoteInput(BaseModel):
    items: list[PacienteRecordatorioLoteItemInput]


class PacienteRecordatorioLoteItemOutput(BaseModel):
    ok: bool
    mensaje: str
    paciente_id: int | None = None
    recordatorio_id: int | None = None
    apellido: str


class PacienteRecordatorioLoteOutput(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[PacienteRecordatorioLoteItemOutput]


class MovimientoFinancieroInput(BaseModel):
    fecha: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha con formato DD-MM-YYYY",
    )
    concepto: str = Field(description="Concepto del movimiento")
    monto: float = Field(description="Monto del movimiento")
    notas: str | None = Field(default=None, description="Notas opcionales")


class MovimientoFinancieroOutput(BaseModel):
    mensaje: str = Field(description="Resultado de la operacion")
    id: int = Field(description="ID del movimiento creado o 0 si hubo error")
    categoria: str = Field(description="Categoria del movimiento")
    fecha: str = Field(description="Fecha del movimiento")
    concepto: str = Field(description="Concepto")
    monto: float = Field(description="Monto")
    notas: str | None = Field(default=None, description="Notas opcionales")


class MovimientoFinancieroLoteInput(BaseModel):
    categoria: Literal["ingreso", "costo_variable"] = Field(
        description="Categoria de movimientos en lote"
    )
    movimientos: list[MovimientoFinancieroInput] = Field(
        description="Lista de movimientos a registrar en lote"
    )


class MovimientoFinancieroLoteOutput(BaseModel):
    total: int
    exitosos: int
    fallidos: int
    resultados: list[MovimientoFinancieroOutput]


class IngresosProximasSemanasInput(BaseModel):
    semanas: int = Field(description="Cantidad de semanas a futuro", ge=1)
    limite: int = Field(default=100, ge=1, le=1000)
    referencia: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha base DD-MM-YYYY opcional",
    )


class IngresosPeriodoInput(BaseModel):
    desde: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha inicio DD-MM-YYYY",
    )
    hasta: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha fin DD-MM-YYYY",
    )
    limite: int = Field(default=100, ge=1, le=1000)


class IngresoItemOutput(BaseModel):
    id: int
    fecha: str
    concepto: str
    monto: float
    notas: str | None = None


class IngresosConsultaOutput(BaseModel):
    desde: str
    hasta: str
    total: int
    total_ingresos: float
    ingresos: list[IngresoItemOutput]


class CostoFijoMensualInput(BaseModel):
    nombre: str = Field(description="Nombre del costo fijo")
    monto_mensual: float = Field(description="Monto mensual")
    activo: bool = Field(default=True, description="Indica si esta activo")


class CostoFijoMensualOutput(BaseModel):
    mensaje: str = Field(description="Resultado de la operacion")
    id: int = Field(description="ID del costo fijo creado o 0 si hubo error")
    nombre: str = Field(description="Nombre del costo fijo")
    monto_mensual: float = Field(description="Monto mensual")
    activo: bool = Field(description="Estado del costo fijo")


class InversionFinancieraInput(BaseModel):
    fecha: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha con formato DD-MM-YYYY",
    )
    nombre: str = Field(description="Nombre de la inversion")
    monto_invertido: float = Field(description="Monto invertido")
    retorno_generado: float = Field(default=0.0, description="Retorno generado")
    notas: str | None = Field(default=None, description="Notas opcionales")


class InversionFinancieraOutput(BaseModel):
    mensaje: str = Field(description="Resultado de la operacion")
    id: int = Field(description="ID de la inversion creada o 0 si hubo error")
    fecha: str = Field(description="Fecha de la inversion")
    nombre: str = Field(description="Nombre de la inversion")
    monto_invertido: float = Field(description="Monto invertido")
    retorno_generado: float = Field(description="Retorno generado")
    notas: str | None = Field(default=None, description="Notas opcionales")


class ResumenFinancieroInput(BaseModel):
    periodo: Literal["dia", "semana", "mes", "anio"] = Field(
        description="Periodo: dia, semana, mes o anio"
    )
    referencia: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha de referencia DD-MM-YYYY",
    )


class ResumenFinancieroOutput(BaseModel):
    periodo: str
    desde: str
    hasta: str
    ingresos: float
    costos_variables: float
    costos_fijos: float
    utilidad_neta: float
    margen_neto: float


class ROIInput(BaseModel):
    desde: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha inicio DD-MM-YYYY",
    )
    hasta: str | None = Field(
        default=None,
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Fecha fin DD-MM-YYYY",
    )


class ROIOutput(BaseModel):
    desde: str | None
    hasta: str | None
    total_invertido: float
    total_retorno: float
    ganancia_neta: float
    roi: float
