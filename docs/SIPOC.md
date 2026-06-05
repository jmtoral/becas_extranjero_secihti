# SIPOC

## Proceso fase 1

| SIPOC | Elementos |
| --- | --- |
| Suppliers | SECIHTI, archivos historicos de Conacyt/Conahcyt, catalogos manuales del proyecto, series de deflactores base 2020. |
| Inputs | Snapshots `.xls/.xlsx/.csv`, metadata de origen, catalogos de paises, instituciones y grados, reglas por patron de archivo, deflactores base 2020. |
| Process | Descubrir archivos, inventariar snapshots, identificar universo extranjero, extraer hojas y columnas, estandarizar variables, deduplicar conservadoramente, deflactar montos, construir tablas analiticas, exportar sitio y reportes. |
| Outputs | Tabla maestra canónica de becas al extranjero, tablas analiticas por año/pais/institucion, miniweb estatica bilingue, reporte metodologico Quarto. |
| Customers | Investigacion periodistica, analisis de politica publica, sociedad civil, academia, y el propio mantenimiento del proyecto. |

## Puntos de control

1. Ningun archivo crudo se modifica.
2. Toda estandarizacion deja rastro en notas o catalogos.
3. La deduplicacion es conservadora.
4. Solo se usan montos contables publicados.
5. Los precios reales siempre se reportan en base 2020.
