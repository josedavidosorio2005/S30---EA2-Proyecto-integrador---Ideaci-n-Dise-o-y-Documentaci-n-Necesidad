# Caracterización de ventas por producto en una cafetería mediante analítica descriptiva

**Proyecto integrador de analítica de datos**  
**S30 – EA2 – Ideación, diseño y documentación de una necesidad**

**Estudiante:** José David Osorio Gallego  
**Grupo:** PREICA2602B020038  
**Asignatura:** Proyecto Integrado III - Analítica de Datos  
**Docente:** Andrés Felipe Callejas  
**Institución:** Institución Universitaria Digital de Antioquia  
**Fecha:** 24 de octubre de 2026

## Tabla de contenido

1. Introducción
2. Planteamiento de la necesidad
3. Justificación
4. Objetivos
5. Marco teórico inicial
6. Metodología de la etapa 1
7. Reconocimiento del dataset
8. Referencias

**Índice de tablas:** Tabla 1. Ficha del dataset. Tabla 2. Diccionario inicial de variables. Tabla 3. Diseño inicial del análisis.

## 1. Introducción

En una cafetería se realizan transacciones todos los días, pero tener los registros no significa que la información esté organizada para tomar decisiones. Por ejemplo, un encargado puede conocer el total vendido y no tener claro cuáles productos concentraron más unidades o un importe mayor. Responderlo exige revisar las variables existentes y comprobar qué significa cada una.

Para este proyecto elegí **Cafe Sales Dataset (Cleaned)**, publicado por Aditya Suyal en Hugging Face. Su ficha presenta registros **sintéticos** de ventas de una cafetería durante 2023. La versión limpia contiene 9.540 filas y ocho columnas; usaré este archivo completo, sin tomar una muestra propia (Suyal, s. f.).

El propósito de esta primera etapa es formular una necesidad concreta, establecer una pregunta que pueda contestarse con los datos y diseñar un análisis descriptivo posterior. Como evidencia técnica, un notebook obtiene el CSV desde Hugging Face, lo carga en un DataFrame de pandas, muestra su estructura y genera automáticamente un TXT con el resumen.

## 2. Planteamiento de la necesidad

**Contexto y beneficiario.** Planteo un escenario hipotético: una cafetería pequeña quiere revisar sus registros al terminar el año. La persona encargada de administrarla sería quien utilizaría el análisis, porque necesita saber cómo se distribuyen las cantidades vendidas y los importes por producto. Este escenario no proviene de una entrevista ni corresponde a un problema observado en un negocio real.

**Necesidad.** La información requerida consiste en conocer la cantidad de unidades y el importe total que registra cada categoría de producto durante un periodo definido. Un resumen de este tipo podría orientar conversaciones sobre la oferta del menú; no demostraría, por sí solo, cuáles productos dejan mayor utilidad o por qué se venden de cierta manera.

**Pregunta de análisis.** ¿Cómo se distribuyen las unidades vendidas y el importe total registrado entre los tipos de producto en las transacciones sintéticas de cafetería correspondientes al año 2023?

La pregunta se puede responder mediante las columnas `Item`, `Quantity`, `Total Spent` y `Transaction Date`. El interés es describir y comparar registros, no pronosticar ventas ni establecer relaciones de causa y efecto.

## 3. Justificación

Seleccioné este conjunto porque combina variables de negocio fáciles de interpretar y un tamaño manejable para mi computador. Cada registro asocia un producto con su cantidad, precio e importe, lo que permite diseñar tablas de ventas por categoría. Al estar disponible de forma pública, también facilita que otra persona reproduzca la etapa de reconocimiento.

El análisis propuesto aportaría una forma ordenada de revisar qué proporción de unidades y de importes corresponde a cada producto. Sin embargo, la información no incluye inventario, costos ni márgenes, por lo que no sería responsable utilizarla para afirmar qué artículo es más rentable. Tampoco sería correcto presentar los resultados como ventas de una cafetería colombiana: la ficha identifica expresamente que los registros son sintéticos (Suyal, s. f.).

La utilidad académica está en conectar una pregunta comprensible con variables realmente disponibles, dejando evidencia del origen, la revisión utilizada y las limitaciones antes de pasar a los gráficos. La ficha indica una licencia MIT, que permite utilizar el recurso bajo sus condiciones declaradas.

## 4. Objetivos

**Objetivo general.** Diseñar un proyecto de analítica descriptiva para caracterizar la distribución de unidades vendidas y del importe registrado por tipo de producto, a partir de las transacciones sintéticas de una cafetería durante 2023.

**Objetivos específicos.**

1. Obtener desde Hugging Face el archivo limpio completo, documentando su procedencia, cobertura y licencia.
2. Reconocer en Jupyter sus primeras filas, dimensiones, columnas, tipos de datos y valores nulos.
3. Definir un procedimiento para agrupar posteriormente las unidades y los importes por producto y, como complemento, por mes.
4. Explicar las limitaciones de la información, en especial la naturaleza sintética y las categorías que contienen datos desconocidos.
5. Generar desde el DataFrame revisado un archivo TXT reproducible que coincida con el notebook y este documento.

## 5. Marco teórico inicial

**Transacción de venta.** En este proyecto se entiende como un registro de producto, cantidad, precio unitario e importe. No se presume que una fila represente toda la compra de un cliente; la unidad observada es la fila tal como aparece en el CSV.

**Unidades e importe.** Las unidades son la suma de `Quantity`. El importe registrado es la suma de `Total Spent`, definido en la ficha como cantidad multiplicada por precio por unidad, expresado en USD. Este importe no equivale a utilidad, pues no incluye costos (Suyal, s. f.).

**Analítica descriptiva.** Consiste aquí en organizar registros existentes mediante conteos, sumas, porcentajes y comparaciones por categorías para responder qué se registró. El manual de NIST/SEMATECH explica que el análisis exploratorio ayuda a reconocer características de los datos con técnicas estadísticas y gráficas. En esta etapa solo se realiza el reconocimiento necesario para formular el diseño inicial (NIST/SEMATECH, s. f.).

**Variables y calidad de datos.** `Item` clasifica productos, mientras que `Quantity` y `Total Spent` son variables numéricas. `Transaction Date` llega como texto y se podría convertir a fecha en la siguiente etapa. pandas permite conservar estos campos en un DataFrame y comprobar tipos y valores nulos. La función `isna()` identifica nulos, pero no interpreta automáticamente el texto literal `Unknown` como uno de ellos (pandas, s. f.).

## 6. Metodología de la etapa 1

### 6.1 Selección y ficha del dataset

Revisé la ficha pública de Hugging Face, sus variables y condiciones de uso. Elegí el archivo limpio, que es lo suficientemente pequeño para trabajar con pandas. Según el publicador, el conjunto original tenía 10.000 registros y, después de la limpieza realizada por él, quedaron 9.540. No se repite esa limpieza ni se toma una muestra nueva en este proyecto.

**Tabla 1. Ficha del dataset**

| Elemento | Descripción |
|---|---|
| Nombre | Cafe Sales Dataset (Cleaned) |
| Identificador | `adityasuyal/cafe-sales-cleaned` |
| URL directa | https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned |
| Publicador | Aditya Suyal |
| Procedencia | Versión limpia de datos **sintéticos** de ventas de cafetería |
| Archivo | `cleaned_cafe_sales.csv` |
| Split o configuración | `train` en el visor, obtenido como CSV completo |
| Revisión | `f4e6dfa1fe791ba84807921c949bd84f02b4bc69` |
| Tamaño descargado | 597.388 bytes, aproximadamente 0,57 MiB |
| Registros y columnas | 9.540 filas y 8 columnas; sin submuestreo propio |
| Periodo | Del 1 de enero al 31 de diciembre de 2023 |
| Licencia declarada | MIT |
| Fecha de consulta | 24 de octubre de 2026 |

### 6.2 Unidad de análisis y diccionario inicial

Cada fila es un registro de transacción de un producto, con el identificador y los demás campos documentados en la ficha. Conservé los nombres originales para que el documento y el notebook se puedan contrastar fácilmente.

**Tabla 2. Diccionario inicial de variables**

| Variable | Significado | Tipo observado | Unidad o formato |
|---|---|---|---|
| `Transaction ID` | Identificador de transacción | `object` | Sin unidad |
| `Item` | Producto comprado | `object` | Categoría |
| `Quantity` | Cantidad comprada | `float64` | Unidades |
| `Price Per Unit` | Precio por unidad | `float64` | USD por unidad |
| `Total Spent` | Importe total del registro | `float64` | USD |
| `Payment Method` | Medio de pago | `object` | Categoría |
| `Location` | Modalidad o ubicación de venta | `object` | `In-store`, `Takeaway`, `Unknown` |
| `Transaction Date` | Fecha de transacción | `object` | `AAAA-MM-DD` |

`Transaction Date` sigue siendo texto en la exploración inicial. Para un análisis mensual posterior habría que transformarlo explícitamente a fecha. No se inventan significados para campos fuera de lo documentado.

### 6.3 Alcance, limitaciones y diseño inicial

**Alcance.** Se analizan los 9.540 registros limpios del año 2023 como un ejercicio descriptivo. Esta etapa verifica el origen y la estructura; las tablas comparativas y visualizaciones de ventas se proponen para las siguientes etapas.

**Limitaciones.** Los datos son sintéticos, no representan una empresa real ni permiten generalizaciones sobre cafeterías colombianas. Faltan costos, inventarios y variables del contexto. En `Location` aparecen **3.779 registros con la etiqueta `Unknown`**, equivalentes al **39,61 %**: esos textos no son nulos de pandas y deben tratarse como modalidad no conocida. Tampoco es posible determinar desde el archivo limpio cómo habría cambiado el resultado si se incluyeran los 460 registros descartados por la limpieza del publicador.

**Tabla 3. Diseño inicial del análisis**

| Qué se describirá | Variables | Procedimiento futuro | Resultado previsto |
|---|---|---|---|
| Unidades por producto | `Item`, `Quantity` | Agrupar y sumar | Totales y porcentajes por producto |
| Importe por producto | `Item`, `Total Spent` | Agrupar y sumar | Importes y porcentajes en USD |
| Variación por mes | `Transaction Date`, `Item`, `Total Spent` | Convertir fechas y agregar por mes | Tabla temporal descriptiva |
| Calidad básica | Todas; especialmente `Location` | Revisar nulos, tipos y `Unknown` | Notas para interpretar resultados |

El trabajo posterior empezaría validando fechas y variables numéricas, seguiría con tablas agrupadas y participaciones porcentuales, y terminaría con gráficos de barras y una lectura descriptiva. Estas son actividades previstas y no conclusiones que ya se hayan demostrado.

## 7. Reconocimiento del dataset

La ejecución del notebook cargó un DataFrame de **9.540 filas y 8 columnas**, sin valores nulos detectados por `df.isna().sum()`. El intervalo de fechas observado fue `2023-01-01` a `2023-12-31`. La columna `Item` presenta ocho tipos diferentes de producto, entre ellos `Coffee`, `Cake` y `Cookie`.

Cinco columnas se leyeron como `object` (`Transaction ID`, `Item`, `Payment Method`, `Location`, `Transaction Date`) y tres como `float64` (`Quantity`, `Price Per Unit`, `Total Spent`). El resultado de nulos es cero por columna, pero no debe ocultar la presencia de la categoría textual `Unknown` en `Location`.

La correspondencia con la necesidad es directa: `Item` identifica el producto, `Quantity` permite acumular unidades, `Total Spent` permite acumular importes y `Transaction Date` permite delimitar la cobertura. El notebook crea la carpeta `AE2/resultados` cuando es necesario y regenera el archivo `resumen_dataframe.txt` desde el mismo DataFrame, incluyendo identificador, revisión, split, dimensiones, nombres, tipos y nulos. Al finalizar, verifica que ese archivo coincida con los datos revisados.

El reconocimiento permite concluir que la pregunta de análisis es viable con las variables elegidas. Una etapa posterior podría describir su distribución, siempre aclarando que se trata de registros sintéticos y que las sumas no equivalen a rentabilidad ni describen a un negocio real.

## 8. Referencias

Hugging Face. (s. f.). *Dataset Cards*. https://huggingface.co/docs/hub/main/datasets-cards

Hugging Face. (s. f.). *Load datasets*. https://huggingface.co/docs/datasets/en/loading

NIST/SEMATECH. (s. f.). *e-Handbook of Statistical Methods: Exploratory Data Analysis*. https://www.itl.nist.gov/div898/handbook/eda/eda.htm

pandas. (s. f.). *pandas.DataFrame*. https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html

pandas. (s. f.). *pandas.DataFrame.isna*. https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isna.html

Suyal, A. (s. f.). *Cafe Sales Dataset (Cleaned)* [Dataset sintético]. Hugging Face. https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned
