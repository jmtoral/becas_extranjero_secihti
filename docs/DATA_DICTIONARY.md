# Diccionario de Datos

## Tabla maestra `scholarships_foreign`

| Columna | Tipo sugerido | Descripcion |
| --- | --- | --- |
| `record_id` | string | Identificador tecnico unico por fila estandarizada. |
| `snapshot_id` | string | Identificador del snapshot local del archivo fuente. |
| `source_year` | int | Año inferido o declarado por el padron. |
| `program_category` | string | Categoria analitica del registro. En fase 1, `becas_extranjero`. |
| `admin_label` | string | Etiqueta institucional observada en la fuente, por ejemplo Conacyt, Conahcyt o Secihti. |
| `person_name_raw` | string | Nombre tal como aparece en la fuente. |
| `person_name_canonical` | string | Nombre normalizado para comparaciones conservadoras. |
| `person_name_key` | string | Llave auxiliar para deduplicacion conservadora. |
| `country_raw` | string | Pais destino tal como aparece en la fuente. |
| `country_canonical` | string | Pais destino armonizado. |
| `country_iso3` | string | Codigo ISO3 del pais, si existe. |
| `institution_raw` | string | Institucion destino original. |
| `institution_canonical` | string | Institucion destino armonizada. |
| `study_program_raw` | string | Nombre del programa de estudios tal como aparece en la fuente. |
| `knowledge_area_raw` | string | Area del conocimiento tal como aparece en la fuente. |
| `degree_raw` | string | Grado o nivel academico en la fuente. |
| `degree_canonical` | string | Grado armonizado. |
| `start_date_raw` | string | Inicio de la beca tal como aparece en la fuente. |
| `end_date_raw` | string | Fin de la beca tal como aparece en la fuente. |
| `amount_nominal_mxn` | float | Monto monetario nominal expresado en MXN cuando la fuente lo permite. |
| `currency_raw` | string | Moneda reportada en la fuente, si existe. |
| `deflator_base_2020` | float | Deflactor del año de origen usando base 2020 = 100. |
| `amount_real_mxn_2020` | float | Monto deflactado a pesos reales base 2020. |
| `source_file_name` | string | Nombre del archivo fuente. |
| `source_file_path` | string | Ruta local del snapshot. |
| `source_sheet_name` | string | Hoja de Excel de donde provino el registro. |
| `source_url` | string | URL publica original, si se documenta. |
| `row_number_source` | int | Fila aproximada del origen. |
| `normalization_notes` | string | Observaciones humanas o tecnicas durante la estandarizacion. |
| `duplicate_review_flag` | boolean | Bandera para revisar posibles duplicados. |
| `is_foreign_scope_confirmed` | boolean | Confirma que el registro pertenece al universo de becas al extranjero. |
| `load_timestamp_utc` | timestamp | Momento de carga al pipeline. |

## Tabla `file_inventory`

| Columna | Tipo sugerido | Descripcion |
| --- | --- | --- |
| `snapshot_id` | string | Llave tecnica por archivo local. |
| `source_file_name` | string | Nombre del archivo. |
| `source_file_path` | string | Ruta absoluta local. |
| `file_extension` | string | Extension detectada. |
| `source_year` | int | Año inferido del nombre del archivo. |
| `program_hint` | string | Sugerencia derivada del nombre del archivo. |
| `is_foreign_candidate` | boolean | Si el nombre del archivo sugiere pertenecer a becas al extranjero. |
| `ingestion_notes` | string | Notas sobre lectura, errores o reglas aplicadas. |

## Regla monetaria

La variable `amount_real_mxn_2020` se calcula como:

`monto_real = monto_nominal * (100 / deflator_base_2020_del_anio_origen)`

Este proyecto **no** estima pagos no publicados. Solo transforma montos explicitamente disponibles.
