# Proyecto integrador de analítica descriptiva de ventas de cafetería

**Autor:** José David Osorio Gallego  
**Actividad:** S30 - EA2 - Ideación, diseño y documentación de una necesidad analítica  
**Asignatura:** Proyecto Integrado III - Analítica de Datos  
**Docente:** Andrés Felipe Callejas  
**Grupo:** PREICA2602B020038

## Propósito

Este proyecto plantea una necesidad de información para una cafetería hipotética: identificar cómo se distribuyen las unidades vendidas y los importes de ventas entre tipos de productos durante 2023. La etapa AE2 se limita a reconocer los datos, documentar el problema propuesto y establecer el diseño de un futuro análisis descriptivo.

## Dataset

- Repositorio: [`adityasuyal/cafe-sales-cleaned`](https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned)
- Archivo: `cleaned_cafe_sales.csv`; el visor de Hugging Face lo presenta como split `train`.
- Revisión fijada: `f4e6dfa1fe791ba84807921c949bd84f02b4bc69`.
- Licencia indicada: MIT.
- Procedencia: datos sintéticos de transacciones de cafetería, limpiados y publicados en Hugging Face.
- Cobertura de la versión seleccionada: 9.540 filas, 8 columnas y fechas de 2023. **Se usa el archivo limpio completo**, no una muestra elaborada en este proyecto.

Estos registros no corresponden a una cafetería colombiana ni son evidencia de un problema real de ventas. Sirven para diseñar y practicar un análisis descriptivo.

## Estructura

```text
AE2/
  documento/
    EA2_S30_Jose_David_Osorio_Gallego.docx
  notebooks/
    01_reconocimiento_dataset.ipynb
  resultados/
    resumen_dataframe.txt
README.md
requirements.txt
.gitignore
```

## Ejecución

1. Descargar o clonar este repositorio.
2. Abrir una terminal desde su carpeta raíz.
3. Crear un entorno virtual (recomendado) e instalar las dependencias: `python -m pip install -r requirements.txt`.
4. Iniciar Jupyter: `jupyter notebook` o `jupyter lab`.
5. Abrir `AE2/notebooks/01_reconocimiento_dataset.ipynb` y ejecutar todas las celdas en orden.
6. Verificar que el notebook muestre las primeras filas, dimensiones, tipos, columnas y conteos de nulos, y que regenere `AE2/resultados/resumen_dataframe.txt`.

La primera ejecución necesita conexión a Internet para obtener el CSV público desde Hugging Face. La URL está fijada a una revisión específica para reproducibilidad. No se necesita token de acceso.

## Criterios de interpretación

- `Total Spent` se expresa en USD según la ficha del publicador y no representa ingresos de una empresa real.
- La etiqueta literal `Unknown` en `Location` no es `NaN`: se conserva como categoría y se documenta como limitación.
- No se calculan rentabilidad, costos, márgenes, causalidad ni pronósticos porque el dataset no permite respaldar esas afirmaciones.
- La etapa AE2 diseña la pregunta y verifica la viabilidad de los datos; los resultados analíticos profundos quedan para etapas posteriores.

## Referencias

- [Ficha del dataset en Hugging Face](https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned)
- [Documentación de carga de datasets](https://huggingface.co/docs/datasets/en/loading)
- [Documentación de DataFrame en pandas](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)

## Entrega

Adjuntar el documento Word por separado en la plataforma y pegar allí el enlace de este repositorio. Se recomienda realizar commits descriptivos después de cada avance.
