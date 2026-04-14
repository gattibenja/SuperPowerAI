#Archivo para definir las herramientas que se van a utilizar en el agente de clima, como obtener la temperatura, humedad y velocidad del viento para una ciudad dada. Estas herramientas pueden ser llamadas por el agente para obtener información específica sobre el clima.
#Importamos los models para tener structured outputs, y el agente para poder decorar las funciones como herramientas del agente.
# from ivan_torres import ivan_torres


from pydantic_ai import FunctionToolset, Tool


from .models import (
    GetPacienteParams,  
    PacienteOutput, 
    PacienteLoteInput,
    PacienteLoteOutput,
    PacienteLoteItemOutput,
    RecordatorioInput,
    RecordatorioOutput,
    RecordatorioLoteInput,
    RecordatorioLoteOutput,
    RecordatorioLoteItemOutput,
    TurnosProximasSemanasInput,
    TurnosPeriodoInput,
    TurnosConsultaOutput,
    TurnoItemOutput,
    CompletarTurnoCobradoInput,
    CompletarTurnoCobradoSimpleInput,
    TurnosCobradosConsultaOutput,
    TurnoCobradoItemOutput,
    CobrarTurnosLoteInput,
    CobrarTurnosLoteOutput,
    CobroTurnoLoteItemOutput,
    PacienteRecordatorioLoteInput,
    PacienteRecordatorioLoteOutput,
    PacienteRecordatorioLoteItemOutput,
    MovimientoFinancieroInput,
    MovimientoFinancieroOutput,
    MovimientoFinancieroLoteInput,
    MovimientoFinancieroLoteOutput,
    IngresosProximasSemanasInput,
    IngresosPeriodoInput,
    IngresosConsultaOutput,
    IngresoItemOutput,
    CostoFijoMensualInput,
    CostoFijoMensualOutput,
    InversionFinancieraInput,
    InversionFinancieraOutput,
    ResumenFinancieroInput,
    ResumenFinancieroOutput,
    ROIInput,
    ROIOutput,
)
from app.services import crear_paciente as crear_paciente_service
from app.services import crear_pacientes_lote as crear_pacientes_lote_service
from app.services import crear_pacientes_y_recordatorios_lote as crear_pacientes_y_recordatorios_lote_service
from app.services import obtener_paciente_por_apellido as obtener_paciente_por_apellido_service
from app.services import crear_recordatorio as crear_recordatorio_service
from app.services import obtener_turnos_proximas_semanas as obtener_turnos_proximas_semanas_service
from app.services import obtener_turnos_historicos_por_periodo as obtener_turnos_historicos_por_periodo_service
from app.services import completar_turno_y_cobrar as completar_turno_y_cobrar_service
from app.services import completar_turno_y_cobrar_simple as completar_turno_y_cobrar_simple_service
from app.services import cobrar_turnos_lote as cobrar_turnos_lote_service
from app.services import obtener_turnos_cobrados_por_periodo as obtener_turnos_cobrados_por_periodo_service
from app.services import registrar_ingreso as registrar_ingreso_service
from app.services import registrar_costo_variable as registrar_costo_variable_service
from app.services import registrar_costo_fijo_mensual as registrar_costo_fijo_mensual_service
from app.services import registrar_inversion as registrar_inversion_service
from app.services import obtener_resumen_financiero as obtener_resumen_financiero_service
from app.services import calcular_roi as calcular_roi_service
from app.services import obtener_ingresos_proximas_semanas as obtener_ingresos_proximas_semanas_service
from app.services import obtener_ingresos_por_periodo as obtener_ingresos_por_periodo_service
from app.services import obtener_ingresos_turnos_cobrados_por_periodo as obtener_ingresos_turnos_cobrados_por_periodo_service
from app.db.dBmodels import Paciente
from app.db.db import Session, engine

pacienteTools = FunctionToolset([])


async def crear_paciente_tool(params: GetPacienteParams) -> PacienteOutput:
    """
    Creates a new patient.

    """
    with Session(engine) as session:
      try:
        paciente = await crear_paciente_service(params, session)
      except ValueError as e:
        return PacienteOutput(
          mensaje=str(e),
          id=0,
          nombre=params.nombre,
          apellido=params.apellido
        )
    
    return PacienteOutput(
     mensaje="Paciente creado correctamente",
     id=paciente.id,
     nombre=paciente.nombre,
     apellido=paciente.apellido
)
    
    
async def obtener_paciente_por_apellido_tool(apellido: str) -> list[PacienteOutput]:
    """
    Obtiene pacientes por apellido.
    """
    with Session(engine) as session:
        try:
            pacientes = await obtener_paciente_por_apellido_service(apellido, session)
        except ValueError as e:
            return [PacienteOutput(
                mensaje=str(e),
                id=0,
                nombre="",
                apellido=apellido
            )]
    
    return [
        PacienteOutput(
            mensaje="Paciente encontrado",
            id=paciente.id,
            nombre=paciente.nombre,
            apellido=paciente.apellido
        ) for paciente in pacientes
    ]
    
async def crear_recordatorio_tool(params: RecordatorioInput) -> RecordatorioOutput:
    """
     Crea un recordatorio para un paciente dado su apellido, fecha, y descripcion.
    """
    with Session(engine) as session:
        try:
            recordatorio = await crear_recordatorio_service(
                params.paciente_apellido,
                params.fecha,
                params.descripcion,
                session,
            )
        except ValueError as e:
            return RecordatorioOutput(
                mensaje=str(e),
                id=0,
                paciente_apellido=params.paciente_apellido,
                fecha=params.fecha,
                descripcion=params.descripcion,
            )
    return RecordatorioOutput(
        mensaje="Recordatorio creado correctamente",
        id=recordatorio.id,
        paciente_apellido=params.paciente_apellido,
        fecha=recordatorio.fecha,
        descripcion=recordatorio.descripcion,
    )


async def crear_pacientes_lote_tool(params: PacienteLoteInput) -> PacienteLoteOutput:
    with Session(engine) as session:
        resultados_raw = await crear_pacientes_lote_service(params.pacientes, session)

    resultados = [
        PacienteLoteItemOutput(
            ok=item["ok"],
            mensaje=item["mensaje"],
            id=item["id"],
            nombre=item["nombre"],
            apellido=item["apellido"],
        )
        for item in resultados_raw
    ]

    exitosos = sum(1 for item in resultados if item.ok)
    fallidos = len(resultados) - exitosos

    return PacienteLoteOutput(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )


async def crear_pacientes_y_recordatorios_lote_tool(
    params: PacienteRecordatorioLoteInput,
) -> PacienteRecordatorioLoteOutput:
    items = [
        {
            "paciente": item.paciente.model_dump(),
            "fecha": item.fecha,
            "descripcion": item.descripcion,
        }
        for item in params.items
    ]

    with Session(engine) as session:
        resultados_raw = await crear_pacientes_y_recordatorios_lote_service(items, session)

    resultados = [
        PacienteRecordatorioLoteItemOutput(
            ok=item["ok"],
            mensaje=item["mensaje"],
            paciente_id=item["paciente_id"],
            recordatorio_id=item["recordatorio_id"],
            apellido=item["apellido"],
        )
        for item in resultados_raw
    ]

    exitosos = sum(1 for item in resultados if item.ok)
    fallidos = len(resultados) - exitosos

    return PacienteRecordatorioLoteOutput(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )


async def crear_recordatorios_lote_tool(
    params: RecordatorioLoteInput,
) -> RecordatorioLoteOutput:
    resultados: list[RecordatorioLoteItemOutput] = []

    with Session(engine) as session:
        for apellido in params.pacientes_apellidos:
            try:
                recordatorio = await crear_recordatorio_service(
                    apellido,
                    params.fecha,
                    params.descripcion,
                    session,
                )
                resultados.append(
                    RecordatorioLoteItemOutput(
                        paciente_apellido=apellido,
                        ok=True,
                        mensaje="Recordatorio creado correctamente",
                        id=recordatorio.id,
                    )
                )
            except ValueError as e:
                resultados.append(
                    RecordatorioLoteItemOutput(
                        paciente_apellido=apellido,
                        ok=False,
                        mensaje=str(e),
                        id=None,
                    )
                )

    exitosos = sum(1 for r in resultados if r.ok)
    fallidos = len(resultados) - exitosos

    return RecordatorioLoteOutput(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )


async def obtener_turnos_proximas_semanas_tool(
    params: TurnosProximasSemanasInput,
) -> TurnosConsultaOutput:
    with Session(engine) as session:
        data = await obtener_turnos_proximas_semanas_service(
            semanas=params.semanas,
            referencia=params.referencia,
            limite=params.limite,
            session=session,
        )

    return TurnosConsultaOutput(
        desde=data["desde"],
        hasta=data["hasta"],
        total=data["total"],
        turnos=[TurnoItemOutput(**item) for item in data["turnos"]],
    )


async def obtener_turnos_historicos_por_periodo_tool(
    params: TurnosPeriodoInput,
) -> TurnosConsultaOutput:
    with Session(engine) as session:
        data = await obtener_turnos_historicos_por_periodo_service(
            desde=params.desde,
            hasta=params.hasta,
            limite=params.limite,
            session=session,
        )

    return TurnosConsultaOutput(
        desde=data["desde"],
        hasta=data["hasta"],
        total=data["total"],
        turnos=[TurnoItemOutput(**item) for item in data["turnos"]],
    )


async def completar_turno_y_cobrar_tool(
    params: CompletarTurnoCobradoInput,
) -> TurnoCobradoItemOutput:
    with Session(engine) as session:
        turno = await completar_turno_y_cobrar_service(
            recordatorio_id=params.recordatorio_id,
            monto_cobrado=params.monto_cobrado,
            fecha_cobro=params.fecha_cobro,
            session=session,
        )
        paciente = session.get(Paciente, turno.paciente_id)

    return TurnoCobradoItemOutput(
        id=turno.id,
        recordatorio_id=turno.id,
        paciente_id=turno.paciente_id,
        paciente_apellido=paciente.apellido if paciente else "",
        fecha_turno=turno.fecha,
        fecha_cobro=turno.fecha_cobro,
        descripcion=turno.descripcion,
        monto_cobrado=turno.monto_cobrado,
    )


async def completar_turno_y_cobrar_simple_tool(
    params: CompletarTurnoCobradoSimpleInput,
) -> TurnoCobradoItemOutput:
    with Session(engine) as session:
        turno = await completar_turno_y_cobrar_simple_service(
            paciente_apellido=params.paciente_apellido,
            monto_cobrado=params.monto_cobrado,
            fecha_turno=params.fecha_turno,
            fecha_cobro=params.fecha_cobro,
            session=session,
        )
        paciente = session.get(Paciente, turno.paciente_id)

    return TurnoCobradoItemOutput(
        id=turno.id,
        recordatorio_id=turno.id,
        paciente_id=turno.paciente_id,
        paciente_apellido=paciente.apellido if paciente else "",
        fecha_turno=turno.fecha,
        fecha_cobro=turno.fecha_cobro,
        descripcion=turno.descripcion,
        monto_cobrado=turno.monto_cobrado,
    )


async def obtener_turnos_cobrados_por_periodo_tool(
    params: TurnosPeriodoInput,
) -> TurnosCobradosConsultaOutput:
    with Session(engine) as session:
        data = await obtener_turnos_cobrados_por_periodo_service(
            desde=params.desde,
            hasta=params.hasta,
            limite=params.limite,
            session=session,
        )

    return TurnosCobradosConsultaOutput(
        desde=data["desde"],
        hasta=data["hasta"],
        total=data["total"],
        total_cobrado=data["total_cobrado"],
        turnos_cobrados=[TurnoCobradoItemOutput(**item) for item in data["turnos_cobrados"]],
    )


async def cobrar_turnos_lote_tool(
    params: CobrarTurnosLoteInput,
) -> CobrarTurnosLoteOutput:
    cobros = [item.model_dump() for item in params.cobros]

    with Session(engine) as session:
        resultados_raw = await cobrar_turnos_lote_service(cobros=cobros, session=session)

    resultados = [CobroTurnoLoteItemOutput(**item) for item in resultados_raw]
    exitosos = sum(1 for item in resultados if item.ok)
    fallidos = len(resultados) - exitosos

    return CobrarTurnosLoteOutput(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )


async def registrar_ingreso_tool(params: MovimientoFinancieroInput) -> MovimientoFinancieroOutput:
    with Session(engine) as session:
        try:
            movimiento = await registrar_ingreso_service(
                fecha=params.fecha,
                concepto=params.concepto,
                monto=params.monto,
                notas=params.notas,
                session=session,
            )
        except ValueError as e:
            return MovimientoFinancieroOutput(
                mensaje=str(e),
                id=0,
                categoria="ingreso",
                fecha=params.fecha,
                concepto=params.concepto,
                monto=params.monto,
                notas=params.notas,
            )

    return MovimientoFinancieroOutput(
        mensaje="Ingreso registrado correctamente",
        id=movimiento.id,
        categoria=movimiento.categoria,
        fecha=movimiento.fecha.isoformat(),
        concepto=movimiento.concepto,
        monto=movimiento.monto,
        notas=movimiento.notas,
    )


async def registrar_costo_variable_tool(
    params: MovimientoFinancieroInput,
) -> MovimientoFinancieroOutput:
    with Session(engine) as session:
        try:
            movimiento = await registrar_costo_variable_service(
                fecha=params.fecha,
                concepto=params.concepto,
                monto=params.monto,
                notas=params.notas,
                session=session,
            )
        except ValueError as e:
            return MovimientoFinancieroOutput(
                mensaje=str(e),
                id=0,
                categoria="costo_variable",
                fecha=params.fecha,
                concepto=params.concepto,
                monto=params.monto,
                notas=params.notas,
            )

    return MovimientoFinancieroOutput(
        mensaje="Costo variable registrado correctamente",
        id=movimiento.id,
        categoria=movimiento.categoria,
        fecha=movimiento.fecha.isoformat(),
        concepto=movimiento.concepto,
        monto=movimiento.monto,
        notas=movimiento.notas,
    )


async def registrar_movimientos_lote_tool(
    params: MovimientoFinancieroLoteInput,
) -> MovimientoFinancieroLoteOutput:
    resultados: list[MovimientoFinancieroOutput] = []

    with Session(engine) as session:
        for movimiento in params.movimientos:
            try:
                if params.categoria == "ingreso":
                    created = await registrar_ingreso_service(
                        fecha=movimiento.fecha,
                        concepto=movimiento.concepto,
                        monto=movimiento.monto,
                        notas=movimiento.notas,
                        session=session,
                    )
                    mensaje = "Ingreso registrado correctamente"
                else:
                    created = await registrar_costo_variable_service(
                        fecha=movimiento.fecha,
                        concepto=movimiento.concepto,
                        monto=movimiento.monto,
                        notas=movimiento.notas,
                        session=session,
                    )
                    mensaje = "Costo variable registrado correctamente"

                resultados.append(
                    MovimientoFinancieroOutput(
                        mensaje=mensaje,
                        id=created.id,
                        categoria=created.categoria,
                        fecha=created.fecha.isoformat(),
                        concepto=created.concepto,
                        monto=created.monto,
                        notas=created.notas,
                    )
                )
            except ValueError as e:
                resultados.append(
                    MovimientoFinancieroOutput(
                        mensaje=str(e),
                        id=0,
                        categoria=params.categoria,
                        fecha=movimiento.fecha,
                        concepto=movimiento.concepto,
                        monto=movimiento.monto,
                        notas=movimiento.notas,
                    )
                )

    exitosos = sum(1 for item in resultados if item.id > 0)
    fallidos = len(resultados) - exitosos

    return MovimientoFinancieroLoteOutput(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )


async def obtener_ingresos_proximas_semanas_tool(
    params: IngresosProximasSemanasInput,
) -> IngresosConsultaOutput:
    with Session(engine) as session:
        data = await obtener_ingresos_proximas_semanas_service(
            semanas=params.semanas,
            referencia=params.referencia,
            limite=params.limite,
            session=session,
        )

    return IngresosConsultaOutput(
        desde=data["desde"],
        hasta=data["hasta"],
        total=data["total"],
        total_ingresos=data["total_ingresos"],
        ingresos=[IngresoItemOutput(**item) for item in data["ingresos"]],
    )


async def obtener_ingresos_por_periodo_tool(
    params: IngresosPeriodoInput,
) -> IngresosConsultaOutput:
    with Session(engine) as session:
        data = await obtener_ingresos_por_periodo_service(
            desde=params.desde,
            hasta=params.hasta,
            limite=params.limite,
            session=session,
        )

    return IngresosConsultaOutput(
        desde=data["desde"],
        hasta=data["hasta"],
        total=data["total"],
        total_ingresos=data["total_ingresos"],
        ingresos=[IngresoItemOutput(**item) for item in data["ingresos"]],
    )


async def obtener_ingresos_turnos_cobrados_por_periodo_tool(
    params: IngresosPeriodoInput,
) -> IngresosConsultaOutput:
    with Session(engine) as session:
        data = await obtener_ingresos_turnos_cobrados_por_periodo_service(
            desde=params.desde,
            hasta=params.hasta,
            session=session,
        )

    return IngresosConsultaOutput(
        desde=data["desde"],
        hasta=data["hasta"],
        total=data["total"],
        total_ingresos=data["total_ingresos"],
        ingresos=[IngresoItemOutput(**item) for item in data["ingresos"]],
    )


async def registrar_costo_fijo_mensual_tool(
    params: CostoFijoMensualInput,
) -> CostoFijoMensualOutput:
    with Session(engine) as session:
        try:
            costo_fijo = await registrar_costo_fijo_mensual_service(
                nombre=params.nombre,
                monto_mensual=params.monto_mensual,
                activo=params.activo,
                session=session,
            )
        except ValueError as e:
            return CostoFijoMensualOutput(
                mensaje=str(e),
                id=0,
                nombre=params.nombre,
                monto_mensual=params.monto_mensual,
                activo=params.activo,
            )

    return CostoFijoMensualOutput(
        mensaje="Costo fijo mensual registrado correctamente",
        id=costo_fijo.id,
        nombre=costo_fijo.nombre,
        monto_mensual=costo_fijo.monto_mensual,
        activo=costo_fijo.activo,
    )


async def registrar_inversion_tool(
    params: InversionFinancieraInput,
) -> InversionFinancieraOutput:
    with Session(engine) as session:
        try:
            inversion = await registrar_inversion_service(
                fecha=params.fecha,
                nombre=params.nombre,
                monto_invertido=params.monto_invertido,
                retorno_generado=params.retorno_generado,
                notas=params.notas,
                session=session,
            )
        except ValueError as e:
            return InversionFinancieraOutput(
                mensaje=str(e),
                id=0,
                fecha=params.fecha,
                nombre=params.nombre,
                monto_invertido=params.monto_invertido,
                retorno_generado=params.retorno_generado,
                notas=params.notas,
            )

    return InversionFinancieraOutput(
        mensaje="Inversion registrada correctamente",
        id=inversion.id,
        fecha=inversion.fecha.isoformat(),
        nombre=inversion.nombre,
        monto_invertido=inversion.monto_invertido,
        retorno_generado=inversion.retorno_generado,
        notas=inversion.notas,
    )


async def obtener_resumen_financiero_tool(
    params: ResumenFinancieroInput,
) -> ResumenFinancieroOutput:
    with Session(engine) as session:
        try:
            resumen = await obtener_resumen_financiero_service(
                periodo=params.periodo,
                referencia=params.referencia,
                session=session,
            )
            return ResumenFinancieroOutput(**resumen)
        except ValueError:
            return ResumenFinancieroOutput(
                periodo=params.periodo,
                desde="",
                hasta="",
                ingresos=0.0,
                costos_variables=0.0,
                costos_fijos=0.0,
                utilidad_neta=0.0,
                margen_neto=0.0,
            )


async def calcular_roi_tool(params: ROIInput) -> ROIOutput:
    with Session(engine) as session:
        roi_data = await calcular_roi_service(
            desde=params.desde,
            hasta=params.hasta,
            session=session,
        )
        return ROIOutput(**roi_data)


pacienteTools = FunctionToolset([
    Tool(crear_paciente_tool, name="crear_paciente"),
    Tool(crear_pacientes_lote_tool, name="crear_pacientes_lote"),
    Tool(obtener_paciente_por_apellido_tool, name="obtener_paciente_por_apellido"),
    Tool(crear_recordatorio_tool, name="crear_recordatorio"),
    Tool(crear_recordatorios_lote_tool, name="crear_recordatorios_lote"),
    Tool(
        obtener_turnos_proximas_semanas_tool,
        name="obtener_turnos_proximas_semanas",
    ),
    Tool(
        obtener_turnos_historicos_por_periodo_tool,
        name="obtener_turnos_historicos_por_periodo",
    ),
    Tool(completar_turno_y_cobrar_tool, name="completar_turno_y_cobrar"),
    Tool(completar_turno_y_cobrar_simple_tool, name="completar_turno_y_cobrar_simple"),
    Tool(cobrar_turnos_lote_tool, name="cobrar_turnos_lote"),
    Tool(
        obtener_turnos_cobrados_por_periodo_tool,
        name="obtener_turnos_cobrados_por_periodo",
    ),
    Tool(
        crear_pacientes_y_recordatorios_lote_tool,
        name="crear_pacientes_y_recordatorios_lote",
    ),
    Tool(registrar_ingreso_tool, name="registrar_ingreso"),
    Tool(registrar_costo_variable_tool, name="registrar_costo_variable"),
    Tool(registrar_movimientos_lote_tool, name="registrar_movimientos_lote"),
    Tool(
        obtener_ingresos_proximas_semanas_tool,
        name="obtener_ingresos_proximas_semanas",
    ),
    Tool(obtener_ingresos_por_periodo_tool, name="obtener_ingresos_por_periodo"),
    Tool(
        obtener_ingresos_turnos_cobrados_por_periodo_tool,
        name="obtener_ingresos_turnos_cobrados_por_periodo",
    ),
    Tool(registrar_costo_fijo_mensual_tool, name="registrar_costo_fijo_mensual"),
    Tool(registrar_inversion_tool, name="registrar_inversion"),
    Tool(obtener_resumen_financiero_tool, name="obtener_resumen_financiero"),
    Tool(calcular_roi_tool, name="calcular_roi"),
])