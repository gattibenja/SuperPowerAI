# Frontend - Clinica Estetica Chat

Frontend React + Vite conectado por streaming AG-UI al backend FastAPI.

## Ejecutar en desarrollo

```bash
cd frontend/viteproject
npm install
npm run dev
```

Si PowerShell bloquea npm, usa:

```bash
npm.cmd run dev
```

## Build

```bash
npm run build
npm run preview
```

## Configuracion de endpoint

Por defecto usa proxy de Vite hacia `http://localhost:8000`.

- AG-UI: `/doctorAgent/`
- API REST: `/api/*`

Opcionalmente puedes definir:

```bash
VITE_AGUI_ENDPOINT=http://localhost:8000/doctorAgent/
```

## Funcionalidades de UI

- Chat en tiempo real con streaming SSE.
- Render incremental de respuesta.
- Estado de ejecucion del agente.
- Indicador de actividad de herramientas.
- Atajos para flujos comunes agenda, finanzas y ROI.

## Checklist de demo final

1. Levantar backend en `:8000`.
2. Levantar frontend con Vite.
3. Enviar mensaje de prueba al agente.
4. Ejecutar un flujo de recordatorios en lote.
5. Ejecutar una consulta de resumen financiero.
