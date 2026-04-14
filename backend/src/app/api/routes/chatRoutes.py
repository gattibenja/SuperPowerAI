from fastapi import APIRouter, Depends, HTTPException
from app.agents.estetica.models import (
    GetPacienteParams,
    RecordatorioInput,
    RecordatorioOutput,
    RecordatorioLoteInput,
    RecordatorioLoteOutput,
    RecordatorioLoteItemOutput,
)
from app.services.pacienteService import crear_paciente as crear_paciente_service
from app.services.pacienteService import obtener_paciente_por_apellido as obtener_pacientes_por_apellido_service
from app.services.pacienteService import crear_recordatorio as crear_recordatorio_service
from app.services.finanzasService import (
    registrar_ingreso as registrar_ingreso_service,
    registrar_costo_variable as registrar_costo_variable_service,
    registrar_costo_fijo_mensual as registrar_costo_fijo_mensual_service,
    registrar_inversion as registrar_inversion_service,
    obtener_resumen_financiero as obtener_resumen_financiero_service,
    calcular_roi as calcular_roi_service,
)
from app.schemas.finanzas_schema import (
    MovimientoFinancieroCreate,
    MovimientoFinancieroLoteCreate,
    MovimientoFinancieroLoteOutput,
    MovimientoFinancieroItemOutput,
    CostoFijoMensualCreate,
    InversionFinancieraCreate,
    PeriodoFinanciero,
)
from app.schemas.paciente_schema import (
    PacienteLoteCreate,
    PacienteLoteResponse,
    PacienteLoteItemResponse,
    PacienteRecordatorioLoteCreate,
    PacienteRecordatorioLoteResponse,
    PacienteRecordatorioLoteItemResponse,
    CobrarTurnoLoteCreate,
    CobrarTurnoLoteResponse,
    CobrarTurnoLoteItemResponse,
)
from app.services.pacienteService import (
    crear_pacientes_lote as crear_pacientes_lote_service,
    crear_pacientes_y_recordatorios_lote as crear_pacientes_y_recordatorios_lote_service,
    cobrar_turnos_lote as cobrar_turnos_lote_service,
)
from sqlmodel import Session
from app.db.db import get_session

router = APIRouter()

@router.post("/crearPacientes")
async def crear_paciente_route(data: GetPacienteParams, session: Session = Depends(get_session)):
    try:
        return await crear_paciente_service(data, session)
    except ValueError as e:
        print(f"Error creating patient: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/crearPacientesLote", response_model=PacienteLoteResponse)
async def crear_pacientes_lote_route(
    data: PacienteLoteCreate, session: Session = Depends(get_session)
):
    resultados_raw = await crear_pacientes_lote_service(data.pacientes, session)
    resultados = [PacienteLoteItemResponse(**item) for item in resultados_raw]
    exitosos = sum(1 for item in resultados if item.ok)
    fallidos = len(resultados) - exitosos
    return PacienteLoteResponse(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )


@router.post(
    "/crearPacientesYRecordatoriosLote",
    response_model=PacienteRecordatorioLoteResponse,
)
async def crear_pacientes_y_recordatorios_lote_route(
    data: PacienteRecordatorioLoteCreate,
    session: Session = Depends(get_session),
):
    items = [
        {
            "paciente": item.paciente.model_dump(),
            "fecha": item.fecha,
            "descripcion": item.descripcion,
        }
        for item in data.items
    ]
    resultados_raw = await crear_pacientes_y_recordatorios_lote_service(items, session)
    resultados = [
        PacienteRecordatorioLoteItemResponse(**item) for item in resultados_raw
    ]
    exitosos = sum(1 for item in resultados if item.ok)
    fallidos = len(resultados) - exitosos
    return PacienteRecordatorioLoteResponse(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )
    
@router.get("/obtenerPaciente")
async def obtener_paciente_route( apellido: str, session: Session = Depends(get_session)):
    try:
        return await obtener_pacientes_por_apellido_service(apellido, session)
    except ValueError as e:
        print(f"Error fetching patient: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agendarRecordatorio", response_model=RecordatorioOutput)
async def agendar_recordatorio_route(data: RecordatorioInput, session: Session = Depends(get_session)):
    try:
        recordatorio = await crear_recordatorio_service(
            data.paciente_apellido,
            data.fecha,
            data.descripcion,
            session,
        )
        return RecordatorioOutput(
            mensaje="Recordatorio creado correctamente",
            id=recordatorio.id,
            paciente_apellido=data.paciente_apellido,
            fecha=recordatorio.fecha,
            descripcion=recordatorio.descripcion,
        )
    except ValueError as e:
        print(f"Error scheduling reminder: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agendarRecordatoriosLote", response_model=RecordatorioLoteOutput)
async def agendar_recordatorios_lote_route(
    data: RecordatorioLoteInput, session: Session = Depends(get_session)
):
    resultados: list[RecordatorioLoteItemOutput] = []

    for apellido in data.pacientes_apellidos:
        try:
            recordatorio = await crear_recordatorio_service(
                apellido,
                data.fecha,
                data.descripcion,
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


@router.post("/cobrarTurnosLote", response_model=CobrarTurnoLoteResponse)
async def cobrar_turnos_lote_route(
    data: CobrarTurnoLoteCreate,
    session: Session = Depends(get_session),
):
    cobros = [item.model_dump() for item in data.cobros]
    resultados_raw = await cobrar_turnos_lote_service(cobros=cobros, session=session)
    resultados = [CobrarTurnoLoteItemResponse(**item) for item in resultados_raw]
    exitosos = sum(1 for item in resultados if item.ok)
    fallidos = len(resultados) - exitosos
    return CobrarTurnoLoteResponse(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )


@router.post("/finanzas/ingreso")
async def registrar_ingreso_route(
    data: MovimientoFinancieroCreate, session: Session = Depends(get_session)
):
    try:
        movimiento = await registrar_ingreso_service(
            fecha=data.fecha,
            concepto=data.concepto,
            monto=data.monto,
            notas=data.notas,
            session=session,
        )
        return {
            "id": movimiento.id,
            "fecha": movimiento.fecha.isoformat(),
            "categoria": movimiento.categoria,
            "concepto": movimiento.concepto,
            "monto": movimiento.monto,
            "notas": movimiento.notas,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/finanzas/costo-variable")
async def registrar_costo_variable_route(
    data: MovimientoFinancieroCreate, session: Session = Depends(get_session)
):
    try:
        movimiento = await registrar_costo_variable_service(
            fecha=data.fecha,
            concepto=data.concepto,
            monto=data.monto,
            notas=data.notas,
            session=session,
        )
        return {
            "id": movimiento.id,
            "fecha": movimiento.fecha.isoformat(),
            "categoria": movimiento.categoria,
            "concepto": movimiento.concepto,
            "monto": movimiento.monto,
            "notas": movimiento.notas,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/finanzas/movimientos-lote",
    response_model=MovimientoFinancieroLoteOutput,
)
async def registrar_movimientos_lote_route(
    data: MovimientoFinancieroLoteCreate,
    session: Session = Depends(get_session),
):
    resultados: list[MovimientoFinancieroItemOutput] = []

    for movimiento in data.movimientos:
        try:
            if data.categoria == "ingreso":
                created = await registrar_ingreso_service(
                    fecha=movimiento.fecha,
                    concepto=movimiento.concepto,
                    monto=movimiento.monto,
                    notas=movimiento.notas,
                    session=session,
                )
            else:
                created = await registrar_costo_variable_service(
                    fecha=movimiento.fecha,
                    concepto=movimiento.concepto,
                    monto=movimiento.monto,
                    notas=movimiento.notas,
                    session=session,
                )

            resultados.append(
                MovimientoFinancieroItemOutput(
                    ok=True,
                    mensaje="Movimiento registrado correctamente",
                    id=created.id,
                    fecha=created.fecha.isoformat(),
                    categoria=created.categoria,
                    concepto=created.concepto,
                    monto=created.monto,
                    notas=created.notas,
                )
            )
        except ValueError as e:
            resultados.append(
                MovimientoFinancieroItemOutput(
                    ok=False,
                    mensaje=str(e),
                    id=None,
                    fecha=movimiento.fecha,
                    categoria=data.categoria,
                    concepto=movimiento.concepto,
                    monto=movimiento.monto,
                    notas=movimiento.notas,
                )
            )

    exitosos = sum(1 for item in resultados if item.ok)
    fallidos = len(resultados) - exitosos

    return MovimientoFinancieroLoteOutput(
        total=len(resultados),
        exitosos=exitosos,
        fallidos=fallidos,
        resultados=resultados,
    )


@router.post("/finanzas/costo-fijo")
async def registrar_costo_fijo_route(
    data: CostoFijoMensualCreate, session: Session = Depends(get_session)
):
    try:
        costo_fijo = await registrar_costo_fijo_mensual_service(
            nombre=data.nombre,
            monto_mensual=data.monto_mensual,
            activo=data.activo,
            session=session,
        )
        return {
            "id": costo_fijo.id,
            "nombre": costo_fijo.nombre,
            "monto_mensual": costo_fijo.monto_mensual,
            "activo": costo_fijo.activo,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/finanzas/inversion")
async def registrar_inversion_route(
    data: InversionFinancieraCreate, session: Session = Depends(get_session)
):
    try:
        inversion = await registrar_inversion_service(
            fecha=data.fecha,
            nombre=data.nombre,
            monto_invertido=data.monto_invertido,
            retorno_generado=data.retorno_generado,
            notas=data.notas,
            session=session,
        )
        return {
            "id": inversion.id,
            "fecha": inversion.fecha.isoformat(),
            "nombre": inversion.nombre,
            "monto_invertido": inversion.monto_invertido,
            "retorno_generado": inversion.retorno_generado,
            "notas": inversion.notas,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/finanzas/resumen")
async def obtener_resumen_financiero_route(
    periodo: PeriodoFinanciero,
    referencia: str | None = None,
    session: Session = Depends(get_session),
):
    try:
        return await obtener_resumen_financiero_service(
            periodo=periodo,
            referencia=referencia,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/finanzas/roi")
async def calcular_roi_route(
    desde: str | None = None,
    hasta: str | None = None,
    session: Session = Depends(get_session),
):
    try:
        return await calcular_roi_service(
            desde=desde,
            hasta=hasta,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))