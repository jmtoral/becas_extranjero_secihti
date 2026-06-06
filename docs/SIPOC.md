# SIPOC

## Proceso actual

| SIPOC | Elementos |
| --- | --- |
| Suppliers | SECIHTI, archivos históricos de Conacyt/Conahcyt, repositorio histórico del proyecto, catálogos manuales del proyecto, serie de deflactores base 2020. |
| Inputs | Snapshots `.xls/.xlsx/.csv`, metadata de origen, catálogos de países, instituciones y grados, reglas por patrón de archivo, filtros para `S190`, deflactores base 2020. |
| Process | Descubrir archivos, inventariar snapshots, separar candidatos de `extranjero` y `nacionales`, extraer hojas y columnas, filtrar universo analítico, estandarizar variables, deduplicar conservadoramente, deflactar montos, construir tablas analíticas, exportar datos del sitio y reportes. |
| Outputs | Tabla maestra de becas al extranjero, tabla maestra de becas nacionales, tablas analíticas por año/geografía/institución, miniweb estática bilingüe para ambas vistas, reporte metodológico Quarto. |
| Customers | Investigación periodística, análisis de política pública, sociedad civil, academia y mantenimiento del propio proyecto. |

## Puntos de control

1. Ningún archivo crudo se modifica.
2. Toda estandarización deja rastro en notas o catálogos.
3. La deduplicación es conservadora.
4. Solo se usan montos contables publicados.
5. Los precios reales siempre se reportan en base 2020.
6. `2026` debe señalarse explícitamente como cobertura parcial.
7. La rama `nacionales` excluye `posdoctorales`, `sabáticas` y `repatriación`.
