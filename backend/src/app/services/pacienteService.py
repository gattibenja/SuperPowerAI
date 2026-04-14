from datetime import date, datetime, timedelta

from app.db.dBmodels import Paciente, Recordatorio
from sqlmodel import Session, select
from app.schemas.paciente_schema import PacienteCreate


def _parse_fecha_recordatorio(fecha: str) -> date:
    formatos = ("%d-%m-%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S")
    for formato in formatos:
        try:
            return datetime.strptime(fecha, formato).date()
        except ValueError:
            continue
    raise ValueError("La fecha del recordatorio debe tener formato DD-MM-YYYY")


async def crear_paciente(data: PacienteCreate, session: Session):
    # Chequear duplicado por nombre + apellido + telefono
    existente = session.exec(
        select(Paciente).where(
            Paciente.nombre == data.nombre,
            Paciente.apellido == data.apellido,
            Paciente.telefono == data.telefono,
        )
    ).first()

    if existente:
        raise ValueError(
            f"Ya existe un paciente con nombre '{data.nombre} {data.apellido}' y teléfono '{data.telefono}' (ID: {existente.id})"
        )

    nuevo_paciente = Paciente(
        nombre=data.nombre,
        apellido=data.apellido,
        edad=data.edad,
        telefono=data.telefono,
        genero=data.genero,
        saldo=data.saldo,
    )
    session.add(nuevo_paciente)
    session.commit()
    session.refresh(nuevo_paciente)
    return nuevo_paciente


async def obtener_pacientes(session: Session):
    return session.exec(select(Paciente)).all()


async def obtener_paciente_por_apellido(paciente_apellido: str, session: Session):
    paciente = session.exec(
        select(Paciente).where(Paciente.apellido == paciente_apellido)
    ).all()
    if not paciente:
        raise ValueError(f"No se encontró un paciente con apellido {paciente_apellido}")
    return paciente


async def crear_recordatorio(paciente_apellido: str, fecha: str, descripcion: str, session: Session):
    paciente = session.exec(
        select(Paciente).where(Paciente.apellido == paciente_apellido)
    ).first()
    if not paciente:
        raise ValueError(f"No se encontró un paciente con apellido {paciente_apellido}")
    
    nuevo_recordatorio = Recordatorio(
        paciente_id=paciente.id,
        fecha=fecha,
        descripcion=descripcion,
        estado="pendiente",
        monto_cobrado=0.0,
        fecha_cobro=None,
    )
    session.add(nuevo_recordatorio)
    session.commit()
    session.refresh(nuevo_recordatorio)
    return nuevo_recordatorio


async def crear_pacientes_lote(datos: list[PacienteCreate], session: Session):
    resultados: list[dict] = []
    nuevos_pacientes: list[Paciente] = []

    for data in datos:
        existente = session.exec(
            select(Paciente).where(
                Paciente.nombre == data.nombre,
                Paciente.apellido == data.apellido,
                Paciente.telefono == data.telefono,
            )
        ).first()

        if existente:
            resultados.append(
                {
                    "ok": False,
                    "mensaje": (
                        f"Ya existe un paciente con nombre '{data.nombre} {data.apellido}' "
                        f"y telefono '{data.telefono}' (ID: {existente.id})"
                    ),
                    "id": existente.id,
                    "nombre": data.nombre,
                    "apellido": data.apellido,
                }
            )
            continue

        nuevos_pacientes.append(
            Paciente(
                nombre=data.nombre,
                apellido=data.apellido,
                edad=data.edad,
                telefono=data.telefono,
                genero=data.genero,
                saldo=data.saldo,
            )
        )

    if nuevos_pacientes:
        session.add_all(nuevos_pacientes)
        session.commit()
        for paciente in nuevos_pacientes:
            session.refresh(paciente)
            resultados.append(
                {
                    "ok": True,
                    "mensaje": "Paciente creado correctamente",
                    "id": paciente.id,
                    "nombre": paciente.nombre,
                    "apellido": paciente.apellido,
                }
            )

    return resultados


async def crear_pacientes_y_recordatorios_lote(
    items: list[dict], session: Session
):
    resultados: list[dict] = []

    for item in items:
        try:
            data = PacienteCreate(**item["paciente"])
            fecha = item["fecha"]
            descripcion = item["descripcion"]

            existente = session.exec(
                select(Paciente).where(
                    Paciente.nombre == data.nombre,
                    Paciente.apellido == data.apellido,
                    Paciente.telefono == data.telefono,
                )
            ).first()

            if not existente:
                existente = Paciente(
                    nombre=data.nombre,
                    apellido=data.apellido,
                    edad=data.edad,
                    telefono=data.telefono,
                    genero=data.genero,
                    saldo=data.saldo,
                )
                session.add(existente)
                session.commit()
                session.refresh(existente)

            recordatorio = Recordatorio(
                paciente_id=existente.id,
                fecha=fecha,
                descripcion=descripcion,
                estado="pendiente",
                monto_cobrado=0.0,
                fecha_cobro=None,
            )
            session.add(recordatorio)
            session.commit()
            session.refresh(recordatorio)

            resultados.append(
                {
                    "ok": True,
                    "mensaje": "Paciente y recordatorio procesados correctamente",
                    "paciente_id": existente.id,
                    "recordatorio_id": recordatorio.id,
                    "apellido": existente.apellido,
                }
            )
        except Exception as e:
            resultados.append(
                {
                    "ok": False,
                    "mensaje": str(e),
                    "paciente_id": None,
                    "recordatorio_id": None,
                    "apellido": item.get("paciente", {}).get("apellido", ""),
                }
            )

    return resultados


async def obtener_turnos_proximas_semanas(
    *, semanas: int, session: Session, referencia: str | None = None, limite: int = 50
):
    if semanas <= 0:
        raise ValueError("El numero de semanas debe ser mayor a 0")
    if limite <= 0:
        raise ValueError("El limite debe ser mayor a 0")

    fecha_inicio = _parse_fecha_recordatorio(referencia) if referencia else date.today()
    fecha_fin = fecha_inicio + timedelta(days=semanas * 7)

    recordatorios = session.exec(select(Recordatorio)).all()
    turnos = []

    for recordatorio in recordatorios:
        try:
            fecha_turno = _parse_fecha_recordatorio(recordatorio.fecha)
        except ValueError:
            continue
        if fecha_inicio <= fecha_turno <= fecha_fin:
            paciente = session.get(Paciente, recordatorio.paciente_id)
            turnos.append(
                {
                    "id": recordatorio.id,
                    "paciente_id": recordatorio.paciente_id,
                    "paciente_apellido": paciente.apellido if paciente else "",
                    "fecha": recordatorio.fecha,
                    "descripcion": recordatorio.descripcion,
                }
            )

    turnos.sort(key=lambda item: datetime.strptime(item["fecha"], "%d-%m-%Y"))
    turnos = turnos[:limite]

    return {
        "desde": fecha_inicio.strftime("%d-%m-%Y"),
        "hasta": fecha_fin.strftime("%d-%m-%Y"),
        "total": len(turnos),
        "turnos": turnos,
    }


async def obtener_turnos_historicos_por_periodo(
    *, desde: str, hasta: str, session: Session, limite: int = 50
):
    fecha_inicio = _parse_fecha_recordatorio(desde)
    fecha_fin = _parse_fecha_recordatorio(hasta)
    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha desde no puede ser mayor que la fecha hasta")
    if limite <= 0:
        raise ValueError("El limite debe ser mayor a 0")

    hoy = date.today()
    tope_hasta = min(fecha_fin, hoy)

    recordatorios = session.exec(select(Recordatorio)).all()
    turnos = []

    for recordatorio in recordatorios:
        try:
            fecha_turno = _parse_fecha_recordatorio(recordatorio.fecha)
        except ValueError:
            continue
        if fecha_inicio <= fecha_turno <= tope_hasta:
            paciente = session.get(Paciente, recordatorio.paciente_id)
            turnos.append(
                {
                    "id": recordatorio.id,
                    "paciente_id": recordatorio.paciente_id,
                    "paciente_apellido": paciente.apellido if paciente else "",
                    "fecha": recordatorio.fecha,
                    "descripcion": recordatorio.descripcion,
                }
            )

    turnos.sort(key=lambda item: datetime.strptime(item["fecha"], "%d-%m-%Y"))
    turnos = turnos[:limite]

    return {
        "desde": fecha_inicio.strftime("%d-%m-%Y"),
        "hasta": tope_hasta.strftime("%d-%m-%Y"),
        "total": len(turnos),
        "turnos": turnos,
    }


async def completar_turno_y_cobrar(
    *, recordatorio_id: int, monto_cobrado: float, session: Session, fecha_cobro: str | None = None
):
    if monto_cobrado <= 0:
        raise ValueError("El monto cobrado debe ser mayor a 0")

    recordatorio = session.get(Recordatorio, recordatorio_id)
    if not recordatorio:
        raise ValueError(f"No existe recordatorio con id {recordatorio_id}")

    if recordatorio.estado == "cobrado":
        raise ValueError("Ese turno ya fue marcado como cobrado")

    fecha_cobro_final = fecha_cobro or date.today().strftime("%d-%m-%Y")
    _parse_fecha_recordatorio(fecha_cobro_final)

    recordatorio.estado = "cobrado"
    recordatorio.monto_cobrado = monto_cobrado
    recordatorio.fecha_cobro = fecha_cobro_final

    session.commit()
    session.refresh(recordatorio)
    return recordatorio


async def completar_turno_y_cobrar_simple(
    *,
    paciente_apellido: str,
    monto_cobrado: float,
    session: Session,
    fecha_turno: str | None = None,
    fecha_cobro: str | None = None,
):
    paciente = session.exec(
        select(Paciente).where(Paciente.apellido == paciente_apellido)
    ).first()
    if not paciente:
        raise ValueError(f"No se encontro un paciente con apellido {paciente_apellido}")

    recordatorios = session.exec(
        select(Recordatorio).where(Recordatorio.paciente_id == paciente.id)
    ).all()

    pendientes = [
        r for r in recordatorios if r.estado != "cobrado"
    ]

    if fecha_turno:
        _parse_fecha_recordatorio(fecha_turno)
        pendientes = [r for r in pendientes if r.fecha == fecha_turno]

    if not pendientes:
        raise ValueError("No hay turnos pendientes para ese paciente con ese criterio")

    if len(pendientes) > 1:
        raise ValueError(
            "Hay mas de un turno pendiente. Indica fecha_turno DD-MM-YYYY para cobrar el correcto"
        )

    return await completar_turno_y_cobrar(
        recordatorio_id=pendientes[0].id,
        monto_cobrado=monto_cobrado,
        fecha_cobro=fecha_cobro,
        session=session,
    )


async def cobrar_turnos_lote(*, cobros: list[dict], session: Session):
    resultados: list[dict] = []

    for item in cobros:
        recordatorio_id = item["recordatorio_id"]
        monto_cobrado = item["monto_cobrado"]
        fecha_cobro = item.get("fecha_cobro")

        try:
            turno = await completar_turno_y_cobrar(
                recordatorio_id=recordatorio_id,
                monto_cobrado=monto_cobrado,
                fecha_cobro=fecha_cobro,
                session=session,
            )
            paciente = session.get(Paciente, turno.paciente_id)
            resultados.append(
                {
                    "ok": True,
                    "mensaje": "Turno cobrado correctamente",
                    "recordatorio_id": recordatorio_id,
                    "id": turno.id,
                    "paciente_id": turno.paciente_id,
                    "paciente_apellido": paciente.apellido if paciente else "",
                    "fecha_turno": turno.fecha,
                    "fecha_cobro": turno.fecha_cobro,
                    "descripcion": turno.descripcion,
                    "monto_cobrado": turno.monto_cobrado,
                }
            )
        except ValueError as e:
            resultados.append(
                {
                    "ok": False,
                    "mensaje": str(e),
                    "recordatorio_id": recordatorio_id,
                    "id": None,
                    "paciente_id": None,
                    "paciente_apellido": None,
                    "fecha_turno": None,
                    "fecha_cobro": fecha_cobro,
                    "descripcion": None,
                    "monto_cobrado": monto_cobrado,
                }
            )

    return resultados


async def obtener_turnos_cobrados_por_periodo(
    *, desde: str, hasta: str, session: Session, limite: int = 100
):
    fecha_inicio = _parse_fecha_recordatorio(desde)
    fecha_fin = _parse_fecha_recordatorio(hasta)
    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha desde no puede ser mayor que la fecha hasta")
    if limite <= 0:
        raise ValueError("El limite debe ser mayor a 0")

    cobrados = session.exec(select(Recordatorio)).all()
    resultados = []
    total_monto = 0.0

    for recordatorio in cobrados:
        if recordatorio.estado != "cobrado" or not recordatorio.fecha_cobro:
            continue
        try:
            fecha_pago = _parse_fecha_recordatorio(recordatorio.fecha_cobro)
        except ValueError:
            continue
        if fecha_inicio <= fecha_pago <= fecha_fin:
            paciente = session.get(Paciente, recordatorio.paciente_id)
            resultados.append(
                {
                    "id": recordatorio.id,
                    "recordatorio_id": recordatorio.id,
                    "paciente_id": recordatorio.paciente_id,
                    "paciente_apellido": paciente.apellido if paciente else "",
                    "fecha_turno": recordatorio.fecha,
                    "fecha_cobro": recordatorio.fecha_cobro,
                    "descripcion": recordatorio.descripcion,
                    "monto_cobrado": recordatorio.monto_cobrado,
                }
            )
            total_monto += recordatorio.monto_cobrado

    resultados = resultados[:limite]
    return {
        "desde": fecha_inicio.strftime("%d-%m-%Y"),
        "hasta": fecha_fin.strftime("%d-%m-%Y"),
        "total": len(resultados),
        "total_cobrado": round(total_monto, 2),
        "turnos_cobrados": resultados,
    }

