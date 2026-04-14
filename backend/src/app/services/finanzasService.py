from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Literal

from sqlmodel import Session, select

from app.db.dBmodels import CostoFijoMensual, InversionFinanciera, MovimientoFinanciero, Recordatorio


PeriodoFinanciero = Literal["dia", "semana", "mes", "anio"]


def _parse_fecha(fecha: str) -> date:
    try:
        return datetime.strptime(fecha, "%d-%m-%Y").date()
    except ValueError as exc:
        raise ValueError("La fecha debe tener formato DD-MM-YYYY") from exc


def _rango_periodo(periodo: PeriodoFinanciero, referencia: date) -> tuple[date, date]:
    if periodo == "dia":
        return referencia, referencia

    if periodo == "semana":
        inicio = referencia - timedelta(days=referencia.weekday())
        fin = inicio + timedelta(days=6)
        return inicio, fin

    if periodo == "mes":
        inicio = referencia.replace(day=1)
        fin = referencia.replace(day=monthrange(referencia.year, referencia.month)[1])
        return inicio, fin

    if periodo == "anio":
        return date(referencia.year, 1, 1), date(referencia.year, 12, 31)

    raise ValueError("Periodo invalido. Usa: dia, semana, mes o anio")


async def registrar_ingreso(
    *,
    fecha: str,
    concepto: str,
    monto: float,
    session: Session,
    notas: str | None = None,
):
    if monto <= 0:
        raise ValueError("El monto del ingreso debe ser mayor a 0")

    movimiento = MovimientoFinanciero(
        fecha=_parse_fecha(fecha),
        categoria="ingreso",
        concepto=concepto,
        monto=monto,
        notas=notas,
    )
    session.add(movimiento)
    session.commit()
    session.refresh(movimiento)
    return movimiento


async def registrar_costo_variable(
    *,
    fecha: str,
    concepto: str,
    monto: float,
    session: Session,
    notas: str | None = None,
):
    if monto <= 0:
        raise ValueError("El monto del costo variable debe ser mayor a 0")

    movimiento = MovimientoFinanciero(
        fecha=_parse_fecha(fecha),
        categoria="costo_variable",
        concepto=concepto,
        monto=monto,
        notas=notas,
    )
    session.add(movimiento)
    session.commit()
    session.refresh(movimiento)
    return movimiento


async def registrar_costo_fijo_mensual(
    *, nombre: str, monto_mensual: float, session: Session, activo: bool = True
):
    if monto_mensual <= 0:
        raise ValueError("El costo fijo mensual debe ser mayor a 0")

    costo_fijo = CostoFijoMensual(
        nombre=nombre,
        monto_mensual=monto_mensual,
        activo=activo,
    )
    session.add(costo_fijo)
    session.commit()
    session.refresh(costo_fijo)
    return costo_fijo


async def registrar_inversion(
    *,
    fecha: str,
    nombre: str,
    monto_invertido: float,
    session: Session,
    retorno_generado: float = 0.0,
    notas: str | None = None,
):
    if monto_invertido <= 0:
        raise ValueError("El monto invertido debe ser mayor a 0")

    inversion = InversionFinanciera(
        fecha=_parse_fecha(fecha),
        nombre=nombre,
        monto_invertido=monto_invertido,
        retorno_generado=retorno_generado,
        notas=notas,
    )
    session.add(inversion)
    session.commit()
    session.refresh(inversion)
    return inversion


async def obtener_resumen_financiero(
    *,
    periodo: PeriodoFinanciero,
    session: Session,
    referencia: str | None = None,
):
    fecha_referencia = _parse_fecha(referencia) if referencia else date.today()
    inicio, fin = _rango_periodo(periodo, fecha_referencia)

    movimientos = session.exec(
        select(MovimientoFinanciero).where(
            MovimientoFinanciero.fecha >= inicio,
            MovimientoFinanciero.fecha <= fin,
        )
    ).all()

    recordatorios = session.exec(select(Recordatorio)).all()
    ingresos = 0.0
    for recordatorio in recordatorios:
        if recordatorio.estado != "cobrado" or not recordatorio.fecha_cobro:
            continue
        try:
            fecha_cobro = _parse_fecha(recordatorio.fecha_cobro)
        except ValueError:
            continue
        if inicio <= fecha_cobro <= fin:
            ingresos += recordatorio.monto_cobrado

    costos_variables = sum(m.monto for m in movimientos if m.categoria == "costo_variable")

    costos_fijos_activos = session.exec(
        select(CostoFijoMensual).where(CostoFijoMensual.activo == True)
    ).all()
    total_fijo_mensual = sum(c.monto_mensual for c in costos_fijos_activos)

    if periodo == "dia":
        dias_mes = monthrange(fecha_referencia.year, fecha_referencia.month)[1]
        costos_fijos = total_fijo_mensual / dias_mes
    elif periodo == "semana":
        dias_mes = monthrange(fecha_referencia.year, fecha_referencia.month)[1]
        costos_fijos = total_fijo_mensual * (7 / dias_mes)
    elif periodo == "mes":
        costos_fijos = total_fijo_mensual
    else:
        costos_fijos = total_fijo_mensual * 12

    utilidad_neta = ingresos - costos_variables - costos_fijos
    margen_neto = (utilidad_neta / ingresos) if ingresos > 0 else 0.0

    return {
        "periodo": periodo,
        "desde": inicio.isoformat(),
        "hasta": fin.isoformat(),
        "ingresos": round(ingresos, 2),
        "costos_variables": round(costos_variables, 2),
        "costos_fijos": round(costos_fijos, 2),
        "utilidad_neta": round(utilidad_neta, 2),
        "margen_neto": round(margen_neto, 4),
    }


async def calcular_roi(
    *,
    session: Session,
    desde: str | None = None,
    hasta: str | None = None,
):
    fecha_inicio = _parse_fecha(desde) if desde else date.min
    fecha_fin = _parse_fecha(hasta) if hasta else date.max

    inversiones = session.exec(
        select(InversionFinanciera).where(
            InversionFinanciera.fecha >= fecha_inicio,
            InversionFinanciera.fecha <= fecha_fin,
        )
    ).all()

    total_invertido = sum(i.monto_invertido for i in inversiones)
    total_retorno = sum(i.retorno_generado for i in inversiones)
    ganancia_neta = total_retorno - total_invertido

    roi = (ganancia_neta / total_invertido) if total_invertido > 0 else 0.0

    return {
        "desde": fecha_inicio.isoformat() if desde else None,
        "hasta": fecha_fin.isoformat() if hasta else None,
        "total_invertido": round(total_invertido, 2),
        "total_retorno": round(total_retorno, 2),
        "ganancia_neta": round(ganancia_neta, 2),
        "roi": round(roi, 4),
    }


async def obtener_ingresos_proximas_semanas(
    *, semanas: int, session: Session, referencia: str | None = None, limite: int = 100
):
    if semanas <= 0:
        raise ValueError("El numero de semanas debe ser mayor a 0")
    if limite <= 0:
        raise ValueError("El limite debe ser mayor a 0")

    fecha_inicio = _parse_fecha(referencia) if referencia else date.today()
    fecha_fin = fecha_inicio + timedelta(days=semanas * 7)

    recordatorios = session.exec(select(Recordatorio)).all()
    ingresos = []

    for recordatorio in recordatorios:
        if recordatorio.estado != "cobrado" or not recordatorio.fecha_cobro:
            continue
        try:
            fecha_cobro = _parse_fecha(recordatorio.fecha_cobro)
        except ValueError:
            continue
        if fecha_inicio <= fecha_cobro <= fecha_fin:
            ingresos.append(
                {
                    "id": recordatorio.id,
                    "fecha": recordatorio.fecha_cobro,
                    "concepto": f"Turno cobrado #{recordatorio.id}",
                    "monto": recordatorio.monto_cobrado,
                    "notas": recordatorio.descripcion,
                }
            )

    total = sum(i["monto"] for i in ingresos)
    ingresos = ingresos[:limite]

    return {
        "desde": fecha_inicio.strftime("%d-%m-%Y"),
        "hasta": fecha_fin.strftime("%d-%m-%Y"),
        "total": len(ingresos),
        "total_ingresos": round(total, 2),
        "ingresos": ingresos,
    }


async def obtener_ingresos_por_periodo(
    *, desde: str, hasta: str, session: Session, limite: int = 100
):
    fecha_inicio = _parse_fecha(desde)
    fecha_fin = _parse_fecha(hasta)

    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha desde no puede ser mayor que la fecha hasta")
    if limite <= 0:
        raise ValueError("El limite debe ser mayor a 0")

    recordatorios = session.exec(select(Recordatorio)).all()
    ingresos = []

    for recordatorio in recordatorios:
        if recordatorio.estado != "cobrado" or not recordatorio.fecha_cobro:
            continue
        try:
            fecha_cobro = _parse_fecha(recordatorio.fecha_cobro)
        except ValueError:
            continue
        if fecha_inicio <= fecha_cobro <= fecha_fin:
            ingresos.append(
                {
                    "id": recordatorio.id,
                    "fecha": recordatorio.fecha_cobro,
                    "concepto": f"Turno cobrado #{recordatorio.id}",
                    "monto": recordatorio.monto_cobrado,
                    "notas": recordatorio.descripcion,
                }
            )

    total = sum(i["monto"] for i in ingresos)
    ingresos = ingresos[:limite]

    return {
        "desde": fecha_inicio.strftime("%d-%m-%Y"),
        "hasta": fecha_fin.strftime("%d-%m-%Y"),
        "total": len(ingresos),
        "total_ingresos": round(total, 2),
        "ingresos": ingresos,
    }


async def obtener_ingresos_turnos_cobrados_por_periodo(
    *, desde: str, hasta: str, session: Session
):
    fecha_inicio = _parse_fecha(desde)
    fecha_fin = _parse_fecha(hasta)

    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha desde no puede ser mayor que la fecha hasta")

    turnos_cobrados = session.exec(select(Recordatorio)).all()
    ingresos = []

    for turno in turnos_cobrados:
        if turno.estado != "cobrado" or not turno.fecha_cobro:
            continue
        try:
            fecha_cobro = _parse_fecha(turno.fecha_cobro)
        except ValueError:
            continue
        if fecha_inicio <= fecha_cobro <= fecha_fin:
            ingresos.append(
                {
                    "id": turno.id,
                    "fecha": turno.fecha_cobro,
                    "concepto": f"Turno cobrado #{turno.id}",
                    "monto": turno.monto_cobrado,
                    "notas": turno.descripcion,
                }
            )

    total = sum(item["monto"] for item in ingresos)

    return {
        "desde": fecha_inicio.strftime("%d-%m-%Y"),
        "hasta": fecha_fin.strftime("%d-%m-%Y"),
        "total": len(ingresos),
        "total_ingresos": round(total, 2),
        "ingresos": ingresos,
    }
