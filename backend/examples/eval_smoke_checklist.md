# Evaluacion Smoke - Agente Clinica

Casos recomendados para validar antes de entregar:

1. Crear paciente nuevo

- Esperado: `mensaje` exitoso e `id > 0`.

2. Crear paciente duplicado

- Esperado: error controlado, sin crash de servidor.

3. Agendar recordatorio lote

- Esperado: `total`, `exitosos`, `fallidos` consistentes con la lista.

4. Resumen financiero sin movimientos

- Esperado: ingresos y costos variables en 0, sin excepcion.

5. Resumen financiero con periodo invalido

- Esperado: respuesta 400 con mensaje claro.

6. ROI con inversion inicial y retorno

- Esperado: `roi` calculado y redondeado.

7. Frontend streaming AG-UI

- Esperado: texto incremental y estado de actividad visible.

Registrar evidencia minima: 3 capturas de pantalla y 1 corrida completa de demo.
