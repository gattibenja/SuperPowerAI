# Backend - Clinica Estetica AG-UI

Backend FastAPI con agente Pydantic AI y endpoints de negocio para pacientes, recordatorios y finanzas.

## Requisitos

- Python 3.10+
- Variables de entorno para el proveedor de LLM (por ejemplo `GOOGLE_API_KEY`)

## Instalacion

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r ..\ai-crash-course-main\ai-crash-course-main\final_project\requirements.txt
pip install sqlmodel python-dotenv logfire
```

## Ejecutar

```bash
cd backend
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

AG-UI queda montado en:

- `POST /doctorAgent/`

API REST de soporte:

- `POST /api/crearPacientes`
- `POST /api/crearPacientesLote`
- `POST /api/crearPacientesYRecordatoriosLote`
- `GET /api/obtenerPaciente?apellido=...`
- `POST /api/agendarRecordatorio`
- `POST /api/agendarRecordatoriosLote`
- `POST /api/finanzas/ingreso`
- `POST /api/finanzas/costo-variable`
- `POST /api/finanzas/movimientos-lote`
- `POST /api/finanzas/costo-fijo`
- `POST /api/finanzas/inversion`
- `GET /api/finanzas/resumen?periodo=dia|semana|mes|anio&referencia=DD-MM-YYYY`
- `GET /api/finanzas/roi?desde=DD-MM-YYYY&hasta=DD-MM-YYYY`

## Script de demo rapido

1. Crear paciente.
2. Agendar recordatorio simple o lote.
3. Registrar ingreso/costo.
4. Consultar resumen financiero mensual.
5. Consultar ROI del periodo.

Con eso cubres funcionalidad, arquitectura y demo de la rubrica del proyecto final.
