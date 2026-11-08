# Analítica descriptiva de ventas de cafetería · AE2 y AE3

**Autor:** Jose David Osorio Gallego  
**Asignatura:** Proyecto Integrado III – Analítica de Datos  
**Docente:** Andrés Felipe Callejas · **Grupo:** PREICA2602B020038  
**Institución:** Institución Universitaria Digital de Antioquia

## Entrega AE3

Se conserva **AE2 sin modificaciones** y se añade el avance en `AE3/`, con el mismo proyecto, pregunta central y revisión del dataset. Se incluye la copia local original para reproducir el análisis sin Internet.

- [Word actualizado](AE3/documento/AE3_Jose_David_Osorio_Gallego.docx)
- [Notebook ejecutado con salidas reales](AE3/notebooks/02_transformacion_enriquecimiento.ipynb)
- [Transformaciones y exportación](AE3/src/analisis.py)
- [CSV preparado](AE3/datos/preparados/cafe_2023_preparado.csv)
- [Resumen descriptivo TXT generado por código](AE3/resultados/resumen_dataframe.txt)
- [Manifiesto y SHA256](AE3/resultados/manifiesto_ejecucion.json)

## Necesidad y preguntas

La cafetería es hipotética. Se necesita describir la distribución de unidades e importes entre productos en 2023. P1 y P2 descomponen la pregunta central de AE2; P3 desarrolla su complemento mensual previsto; P4 cuantifica la limitación de modalidad ya identificada.

| Pregunta | Variables originales | Nivel | CSV en AE3/resultados/ |
|---|---|---|---|
| P1 ¿Cómo se distribuyen las unidades entre productos? | Item, Quantity, Transaction Date | Producto | p1_unidades_producto.csv |
| P2 ¿Cómo se distribuye el importe entre productos? | Item, Total Spent, Transaction Date | Producto | p2_importe_producto.csv |
| P3 ¿Cómo varían los importes por mes? | Transaction Date, Item, Quantity, Total Spent | Mes | p3_ventas_mes.csv |
| P4 ¿Qué proporción tiene modalidad desconocida? | Location, Total Spent | Modalidad | p4_cobertura_modalidad.csv |

El complemento `ventas_mes_producto.csv` contiene 96 filas por mes y producto. Las tablas tienen niveles diferentes: no se concatenan para sumar importes, pues representan los mismos registros.

## Fuente y límites

- Aditya Suyal. [Cafe Sales Dataset Cleaned](https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned).
- Revisión de AE2: `f4e6dfa1fe791ba84807921c949bd84f02b4bc69`.
- Original: `AE3/datos/originales/cleaned_cafe_sales.csv`; 597.388 bytes, 9.540 filas y 8 columnas; archivo completo.
- SHA256: `f1271f9ecffdbd4928e21b624c71ff7fe29e1eb79d3f7426e93076e49c4b30ca`.
- Cobertura: 2023-01-01 a 2023-12-31. Moneda USD y licencia MIT declaradas en la [ficha fuente conservada](AE3/datos/originales/FICHA_FUENTE.md); ver `AVISO_FUENTE.txt`.
- Datos **sintéticos**, sin información de personas o una empresa real.
- El publicador imputó productos y pagos por moda, cantidades y precios por mediana, recalculó importes y retiró 460 filas sin fecha válida. AE3 no realiza esa limpieza previa. El archivo limpio no identifica las imputaciones por fila, por lo que no puede medirse su efecto exacto.

No se infieren rentabilidad, causalidad, estacionalidad ni pronósticos. Unknown es una categoría desconocida, aunque pandas no la cuente como nulo.

## Transformaciones y enriquecimiento

Se conserva el CSV original y un respaldo del DataFrame. Se renombran las ocho columnas en español, se convierte la fecha con formato exacto, se convierte cantidad de float64 a Int64 tras comprobar que todos los valores son enteros y se tipan producto, pago y modalidad como categorías conservando etiquetas. Los campos de pago e identificador se retienen para trazabilidad.

No se eliminan filas ni columnas, no se imputan valores ni se convierte USD a COP. Los controles detectan cero nulos, duplicados, fechas inválidas, categorías inesperadas, espacios externos y desajustes cantidad × precio. Los problemas nuevos detienen la ejecución en vez de eliminarse silenciosamente. Unknown permanece en 3.779 filas.

| Variable nueva | Regla | Utilidad |
|---|---|---|
| anio | Año de fecha | Verificar cobertura 2023 |
| mes | Periodo AAAA-MM | Agregación temporal P3 |
| importe_calculado_usd | Cantidad × precio, a dos decimales | Comprobar importes P2 |
| diferencia_importe_usd | Importe menos calculado | Conciliar sin sobrescribir el origen |
| modalidad_conocida | Modalidad distinta de Unknown | Medir cobertura P4 |

No se unen otras fuentes. El resultado tiene **9.540 filas y 13 columnas**. En `AE3/resultados/` se exportan también `registro_transformaciones.csv`, `controles_calidad.csv`, `comparacion_esquema.csv`, `diccionario_datos.csv`, `matriz_preguntas.csv`, `validaciones.csv` e `interpretaciones.json`. Los conteos de filas afectadas por distintas conversiones no son aditivos.

## Resultados y verificaciones

- Total: **28.850 unidades y USD 85.246,50**.
- Juice: **6.141 unidades (21,29 %) y USD 18.249,00 (21,41 %)**; encabeza ambas distribuciones.
- Mayor importe mensual: junio, **USD 7.417,50**. Menor: febrero, **USD 6.673,00**.
- Unknown: **3.779 registros (39,61 %) y USD 33.818,50 (39,67 %)**; permanece en todos los totales.

Se aprueban 20 conciliaciones de agrupaciones. Se exportan y releen 12 CSV, incluido el preparado, para contrastar valores; se reconstruyen tipos y se compara el DataFrame completo. El TXT se sobrescribe desde el DataFrame final en cada ejecución e incluye dimensiones, columnas, tipos, nulos, estadísticas numéricas y temporales y frecuencias categóricas. Se compara con una nueva generación desde el mismo DataFrame.

Las participaciones usan el total anual completo. La variación mensual es (importe actual / anterior − 1) × 100; enero queda vacío porque falta diciembre de 2022, sin imputar cero. Los CSV de resultados conservan diez decimales y el Word muestra dos: la suma de porcentajes mostrados puede diferir mínimamente de 100 por redondeo. Registros significa filas, no clientes.

## Ejecución desde la raíz

Recomendado: Python 3.11 o 3.12, con un entorno virtual.

```bash
python -m venv .venv
```

Activar en PowerShell: `.\.venv\Scripts\Activate.ps1`. En Linux/macOS: `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python -m jupyter lab
```

Abrir `AE3/notebooks/02_transformacion_enriquecimiento.ipynb` y ejecutar **todas las celdas**. Las rutas son relativas al repositorio y admiten iniciar desde raíz, AE3 o AE3/notebooks. No requiere Internet tras instalar dependencias; los datos ya están incluidos.

Para regenerar solo CSV, TXT e interpretaciones:

```bash
python AE3/src/analisis.py
```

Para regenerar además notebook ejecutado y Word:

```bash
python -m pip install -r AE3/requirements_documento.txt
python AE3/src/construir_entrega.py
```

El constructor ejecuta realmente cada celda con IPython en proceso y captura texto, salidas enriquecidas y contadores. Este modo evita depender de sockets. El notebook también funciona en Jupyter convencional; no se insertan resultados simulados. Las versiones efectivas están en `AE3/resultados/manifiesto_ejecucion.json`.

El notebook histórico `AE2/notebooks/01_reconocimiento_dataset.ipynb` sigue disponible sin cambios y sí necesita Internet para descargar su CSV.

## Rutas principales

| Ruta | Contenido |
|---|---|
| AE2/ | Entrega anterior conservada |
| AE3/datos/originales/ | CSV original, ficha y atribución |
| AE3/datos/preparados/cafe_2023_preparado.csv | Base final |
| AE3/notebooks/02_transformacion_enriquecimiento.ipynb | Notebook ejecutado |
| AE3/src/ | analisis.py y construir_entrega.py |
| AE3/documento/AE3_Jose_David_Osorio_Gallego.docx | Avance actualizado |
| AE3/resultados/ | Tablas por pregunta, controles, diccionario, TXT y manifiesto |
| AE3/requirements_documento.txt | Dependencias adicionales para regenerar Word |

## Entrega y acceso

Adjuntar el Word en la plataforma y compartir el enlace de **este repositorio**, que conserva AE2 y AE3. Para comprobar acceso del docente, abrir el enlace y los archivos en una ventana privada sin iniciar sesión. La publicación en GitHub no confirma el envío en la plataforma: el estudiante debe realizarlo dentro del plazo.

## Referencias

- Suyal, A. (s. f.). [Cafe Sales Dataset Cleaned](https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned). Revisión fijada y ficha conservadas con el original.
- pandas. (s. f.). [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html), [to_datetime](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html) y [groupby](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html).
- Osorio Gallego, J. D. (2026). Avance AE2, conservado en este repositorio.
