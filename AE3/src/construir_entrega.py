"""Regenera el notebook y el documento desde los mismos resultados de AE3."""
from pathlib import Path
import json
import sys
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
import os
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from analisis import cargar, transformar, resultados, interpretaciones, diccionario, ejecutar

RAIZ=Path(__file__).resolve().parents[2]

def notebook():
    c=[]
    def md(s): c.append(nbf.v4.new_markdown_cell(s))
    def code(s): c.append(nbf.v4.new_code_cell(s))
    md('''# AE3 · Transformación y enriquecimiento de ventas de cafetería
**Autor:** Jose David Osorio Gallego  
**Asignatura:** Proyecto Integrado III – Analítica de Datos · **Grupo:** PREICA2602B020038  
**Docente:** Andrés Felipe Callejas · Institución Universitaria Digital de Antioquia

## Necesidad y continuidad con AE2
La cafetería es un escenario hipotético. Se necesita describir cómo se distribuyen las unidades y los importes entre productos en 2023. Se conserva el dataset completo y la pregunta central de AE2: **¿Cómo se distribuyen las unidades vendidas y el importe total registrado entre los tipos de producto en las transacciones sintéticas de cafetería de 2023?**

P1 y P2 descomponen esa pregunta; P3 desarrolla el complemento mensual ya previsto en AE2. P4 cuantifica la modalidad desconocida para hacer explícita la limitación de calidad identificada en AE2. No reemplaza la pregunta central ni introduce una fuente nueva.

Datos **sintéticos**, con imputaciones previas del publicador: no corresponden a una empresa real. No hay costos, inventarios ni marcas por fila de los valores imputados. Los resultados describen el archivo limpio, no ventas observadas sin intervención.

**Ejecución:** ejecutar todas las celdas desde este directorio o desde la raíz del repositorio. Se utiliza la copia local inalterada del CSV de AE2, con revisión y SHA256 verificados. No requiere Internet para analizar y exportar. El código de transformación completo está en `AE3/src/analisis.py`.''')
    code('''from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Markdown

# Localización relativa: admite Jupyter desde raíz, AE3 o AE3/notebooks.
RAIZ = next((p for p in [Path.cwd(), *Path.cwd().parents]
             if (p / 'AE3/src/analisis.py').is_file()), None)
if RAIZ is None:
    raise FileNotFoundError('Abrir el notebook dentro del repositorio')
sys.path.insert(0, str(RAIZ / 'AE3/src'))
from analisis import (PREGUNTAS, REVISION, URL, cargar, transformar, resultados,
                      interpretaciones, diccionario, exportar, resumen_descriptivo)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_colwidth', 100)
display(PREGUNTAS)''')
    md('''## 1 · Origen y versión sin modificar
Fuente: [Aditya Suyal · Cafe Sales Dataset Cleaned](https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned), revisión `f4e6dfa1fe791ba84807921c949bd84f02b4bc69`, archivo `cleaned_cafe_sales.csv`. La ficha fuente se conserva en `AE3/datos/originales/FICHA_FUENTE.md`; declara licencia MIT y moneda USD. Se mantiene atribución en `AVISO_FUENTE.txt`.

El publicador pasó de 10.000 a 9.540 filas al retirar fechas no válidas; además imputó categorías con la moda y cantidades/precios con medianas, y recalculó `Total Spent`. **AE3 no repite ni atribuye a este trabajo esa limpieza previa.** La concordancia aritmética no constituye una validación independiente de ventas reales.''')
    code('''original, ruta_origen = cargar(RAIZ)
original_respaldo = original.copy(deep=True)
print('Revisión:', REVISION)
print('Origen fijado:', URL)
print('Dimensiones originales:', original.shape)
display(original.head())
display(pd.DataFrame({'tipo': original.dtypes.astype(str), 'nulos': original.isna().sum()}))
original.info()''')
    md('''## 2 · Transformación y reglas de calidad
Se renombra el esquema en español, se convierte la fecha con formato exacto y la cantidad a entero solo tras comprobar que no tiene fracciones. Se tipan las categorías conservando sus etiquetas. Los precios e importes siguen en USD. Los campos de pago e identificador se conservan para trazabilidad, aunque no se utilicen como dimensiones de las preguntas principales.

No se elimina ninguna fila ni columna y no se imputan valores. `Unknown` sigue siendo una categoría explícita. Los controles detienen la ejecución si aparecen nulos, fechas inválidas, duplicados, valores fuera del catálogo, cantidades fraccionarias o desajustes de importe; una anomalía nueva requiere revisar el criterio, no borrarla silenciosamente. El registro de operaciones distingue filas transformadas de problemas detectados.''')
    code('''df, calidad, comparacion, cambios = transformar(original)
pd.testing.assert_frame_equal(original, original_respaldo)
display(cambios)
display(calidad)
display(pd.DataFrame({'etapa':['Original AE2','Preparado AE3'],
                      'filas':[len(original),len(df)],
                      'columnas':[original.shape[1],df.shape[1]],
                      'nulos':[int(original.isna().sum().sum()),int(df.isna().sum().sum())]}))
display(comparacion)''')
    md('''## 3 · Enriquecimiento y diccionario actualizado
Se incorporan cinco variables: `anio = fecha.dt.year`, `mes = fecha.dt.to_period('M')`, `importe_calculado_usd = round(cantidad × precio_unitario_usd, 2)`, `diferencia_importe_usd = round(importe_usd − importe_calculado_usd, 2)` y `modalidad_conocida = modalidad != 'Unknown'`.

Año y mes permiten delimitar y agrupar el periodo; importe calculado y diferencia permiten conciliar las respuestas monetarias sin reemplazar el dato fuente; modalidad conocida permite medir cobertura. No se realizan uniones con otras tablas. Por ello no hay claves de unión ni riesgo de multiplicar filas por un cruce. Los nombres originales y su correspondencia quedan en la comparación de esquema.''')
    code('''display(diccionario(df))
display(df.head())
print('Nulos finales por columna:')
display(df.isna().sum().to_frame('nulos'))''')
    md('''## 4 · Respuestas sustentadas en tablas
Las participaciones se calculan con el total anual completo como denominador. Se conservan valores sin redondear en memoria y se exportan con diez decimales; en las tablas de lectura se muestran dos. Una suma de porcentajes mostrados puede diferir de 100 por redondeo. `registros` cuenta filas, no clientes ni pedidos completos. La variación mensual es `(importe_mes / importe_mes_anterior − 1) × 100`; en enero es no disponible por falta de diciembre de 2022.''')
    code('''tablas, validaciones = resultados(df)
respuestas = interpretaciones(df, tablas)
print('Total de unidades:', int(df.cantidad.sum()))
print(f'Total de importe: USD {df.importe_usd.sum():,.2f}')''')
    for p,nombre in [('P1','p1_unidades_producto'),('P2','p2_importe_producto'),('P3','p3_ventas_mes'),('P4','p4_cobertura_modalidad')]:
        md(f"### {p} · "+str(__import__('analisis').PREGUNTAS.set_index('pregunta_id').loc[p,'pregunta']))
        code(f"display(tablas['{nombre}'].round(2))\ndisplay(Markdown(respuestas['{p}']))")
    md('''### Detalle mensual por producto
Esta tabla complementaria cumple el diseño temporal de AE2 y queda lista para gráficos de AE4. Su nivel es mes y producto; no debe sumarse junto con otras tablas de diferente nivel porque duplicaría los mismos importes.''')
    code("display(tablas['ventas_mes_producto'].head(16))\nprint('Filas del detalle mes-producto:', len(tablas['ventas_mes_producto']))")
    md('''## 5 · Validación y exportación automática
Se comprueba que todas las agrupaciones conserven conteos y, cuando corresponde, unidades e importes. Cada participación suma 100 antes de redondear. Se comprueban los doce meses y las 96 combinaciones mes-producto.

El CSV preparado y todas las tablas se escriben con rutas relativas y se vuelven a leer para contrastar valores. El CSV no conserva los tipos de pandas: el diccionario documenta cómo recuperarlos. El TXT se sobrescribe desde el DataFrame final e incluye dimensiones, tipos, nulos, estadísticas numéricas y temporales y frecuencias categóricas. Se compara su contenido con una nueva generación desde el mismo DataFrame. El manifiesto registra versiones y huellas SHA256.''')
    code('''display(validaciones)
manifiesto = exportar(RAIZ, original, df, calidad, comparacion, cambios,
                      tablas, validaciones, ruta_origen)
print('Validaciones de agrupaciones:', len(validaciones))
print('Archivos CSV exportados y releídos:', manifiesto['exportaciones_releidas'])
print('Resumen descriptivo: AE3/resultados/resumen_dataframe.txt')
print((RAIZ / 'AE3/resultados/resumen_dataframe.txt').read_text(encoding='utf-8'))
display(pd.DataFrame({'archivo':list(manifiesto['archivos_sha256']),
                      'sha256':list(manifiesto['archivos_sha256'].values())}))
pd.testing.assert_frame_equal(original, original_respaldo)
print('Flujo completado: original intacto, resultados conciliados y TXT regenerado.')''')
    md('''## 6 · Conclusiones del avance y límites
Las tablas responden la pregunta central de AE2 mediante sumas y participaciones por producto, y desarrollan el complemento mensual previsto. La modalidad desconocida se cuantifica sin excluirla de los totales. Los resultados quedan preparados para representarse gráficamente en AE4.

La ausencia de nulos de pandas no implica ausencia de incertidumbre: hay `Unknown` y valores imputados previamente por el publicador. No se pueden identificar esas imputaciones fila por fila, restaurar las 460 filas excluidas, medir rentabilidad ni generalizar a una cafetería real. Un único año sintético no acredita estacionalidad ni causalidad.

## Referencias
- Suyal, A. (s. f.). *Cafe Sales Dataset (Cleaned)*. [Ficha y revisión de la fuente](https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned/tree/f4e6dfa1fe791ba84807921c949bd84f02b4bc69).
- pandas. (s. f.). [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html), [to_datetime](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html), [groupby](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html).
- Osorio Gallego, J. D. (2026). *AE2 Ideación, diseño y documentación de una necesidad*. Antecedente conservado en `AE2/`.

Las estadísticas del avance se obtienen de esta ejecución; la ficha fuente fundamenta procedencia, moneda, licencia y tratamiento previo.''')
    nb=nbf.v4.new_notebook(cells=c,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}})
    destino=RAIZ/'AE3/notebooks/02_transformacion_enriquecimiento.ipynb'
    # Ejecuta realmente cada celda en IPython, con captura de stdout y salidas ricas.
    # No necesita abrir sockets; el notebook también se ejecuta normalmente en Jupyter.
    shell=InteractiveShell.instance()
    anterior=Path.cwd()
    try:
        os.chdir(destino.parent)
        for cell in nb.cells:
            if cell.cell_type!='code': continue
            with capture_output(stdout=True,stderr=True,display=True) as salida:
                resultado=shell.run_cell(cell.source,store_history=True)
            if resultado.error_before_exec or resultado.error_in_exec:
                raise RuntimeError('Falló la celda del notebook') from (resultado.error_before_exec or resultado.error_in_exec)
            cell.execution_count=resultado.execution_count
            cell.outputs=[]
            if salida.stdout: cell.outputs.append(nbf.v4.new_output('stream',name='stdout',text=salida.stdout))
            if salida.stderr: cell.outputs.append(nbf.v4.new_output('stream',name='stderr',text=salida.stderr))
            for out in salida.outputs:
                cell.outputs.append(nbf.v4.new_output('display_data',data=out.data,metadata=out.metadata))
    finally:
        os.chdir(anterior)
    nb.metadata['ejecucion']={'motor':'IPython InteractiveShell','modo':'celdas ejecutadas secuencialmente en proceso; salidas reales capturadas'}
    nbf.write(nb,destino)
    return destino

def documento():
    df,tablas,man=ejecutar(RAIZ)
    original,_=cargar(RAIZ); _,calidad,comparacion,cambios=transformar(original)
    respuestas=interpretaciones(df,tablas)
    d=Document()
    sec=d.sections[0]; sec.page_width=Inches(8.5); sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=Inches(.7); sec.left_margin=sec.right_margin=Inches(.8)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
        st=d.styles[name]; st.font.name='Calibri'; st.font.color.rgb=RGBColor(0,0,0)
    # Elimina bordes heredados de la plantilla de Word, incluida la línea del título.
    for st in d.styles:
        for borde in list(st.element.iter(qn('w:pBdr'))):
            borde.getparent().remove(borde)
    normal=d.styles['Normal']; normal.font.size=Pt(10.5); normal.paragraph_format.space_after=Pt(6)
    normal.paragraph_format.line_spacing=1.08
    d.styles['Title'].font.size=Pt(25)
    d.styles['Heading 1'].font.size=Pt(16); d.styles['Heading 2'].font.size=Pt(12)
    d.core_properties.author='Jose David Osorio Gallego'
    d.core_properties.title='Caracterización de ventas de cafetería mediante transformación y enriquecimiento de datos'
    header=sec.header.paragraphs[0]; header.text='PROYECTO INTEGRADO III  |  AVANCE AE3'; header.runs[0].font.size=Pt(8)
    footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run('Jose David Osorio Gallego  ·  ')
    fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); footer._p.append(fld)
    def p(s,style=None):return d.add_paragraph(s,style)
    def h(s):d.add_heading(s,level=1)
    def nueva(s):d.add_page_break();h(s)
    def tabla(numero,titulo,datos,anchos=None):
        cp=p(f'Tabla {numero}. {titulo}'); cp.paragraph_format.keep_with_next=True
        for r in cp.runs:r.bold=True;r.font.size=Pt(10)
        t=d.add_table(rows=1,cols=len(datos.columns));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
        if anchos:
            for col,w in zip(t.columns,anchos):col.width=Inches(w)
        for cell,txt in zip(t.rows[0].cells,datos.columns):cell.text=str(txt)
        for row in datos.itertuples(index=False,name=None):
            cells=t.add_row().cells
            for cell,v in zip(cells,row):
                if pd.isna(v): text='No disponible'
                elif isinstance(v,float):text=f'{v:,.2f}'
                else:text=str(v)
                cell.text=text
        for i,row in enumerate(t.rows):
            trPr=row._tr.get_or_add_trPr()
            avoid=OxmlElement('w:cantSplit');trPr.append(avoid)
            if i==0:
                rep=OxmlElement('w:tblHeader');trPr.append(rep)
            for j,cell in enumerate(row.cells):
                if anchos:cell.width=Inches(anchos[j])
                cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                tcPr=cell._tc.get_or_add_tcPr()
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DCE6F1' if i==0 else ('F5F7FA' if i%2==0 else 'FFFFFF'));tcPr.append(shade)
                borders=OxmlElement('w:tcBorders')
                for side in ['top','left','bottom','right']:
                    edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
                tcPr.append(borders)
                margins=OxmlElement('w:tcMar')
                for side in ['top','left','bottom','right']:
                    z=OxmlElement('w:'+side);z.set(qn('w:w'),'75');z.set(qn('w:type'),'dxa');margins.append(z)
                tcPr.append(margins)
                for par in cell.paragraphs:
                    par.paragraph_format.space_after=Pt(2);par.paragraph_format.space_before=Pt(2);par.paragraph_format.line_spacing=1.0
                    if j>0 and len(str(cell.text))<18:par.alignment=WD_ALIGN_PARAGRAPH.CENTER
                    for run in par.runs:run.font.size=Pt(9);run.bold=(i==0)
        p('Fuente: elaboración propia a partir del CSV limpio de Suyal, revisión fijada en AE2.').runs[0].font.size=Pt(8)

    d.add_heading('Caracterización de ventas de cafetería mediante transformación y enriquecimiento de datos',0)
    p('S30 AE3 · Proyecto integrador de analítica de datos','Subtitle')
    p('Jose David Osorio Gallego\nGrupo PREICA2602B020038\nProyecto Integrado III – Analítica de Datos\nDocente Andrés Felipe Callejas\nInstitución Universitaria Digital de Antioquia\n7 de noviembre de 2026')
    d.add_heading('Resumen del avance',1)
    p(f'Este avance continúa la necesidad y el dataset de AE2. A partir de {len(df):,} registros sintéticos de cafetería de 2023, preparo una base de 13 variables, verifico su calidad y construyo tablas por producto y por mes. El conjunto registra {int(df.cantidad.sum()):,} unidades y un importe de USD {df.importe_usd.sum():,.2f}. No elimino filas ni imputo valores en esta etapa.')
    p('Juice concentra 21,29 % de las unidades y 21,41 % del importe. La modalidad desconocida afecta 39,61 % de las filas y se conserva en todos los totales. Estos resultados describen un archivo sintético previamente limpiado e imputado por su publicador; no representan ventas de una empresa real ni permiten calcular rentabilidad.')
    p('La entrega incluye notebook ejecutado, código Python, CSV original y preparado, tablas de resultados, controles, diccionario y resumen TXT generado desde el DataFrame final. Se preserva AE2 en el mismo repositorio.')

    nueva('Contenido e índice de tablas')
    secciones=['1 Necesidad y diseño del análisis','2 Metodología y transformaciones','3 Validación y comparación de calidad','4 Diccionario actualizado','5 Enriquecimiento y procedimiento de respuesta','6 Resultados por producto','7 Resultados por mes','8 Cobertura y discusión','9 Conclusiones y reproducción','10 Referencias']
    for s,pagina in zip(secciones,[3,4,5,6,7,8,9,10,11,11]):
        p(s+f'    ·    página {pagina}')
    d.add_heading('Índice de tablas',2)
    titulos=['1 Relación entre preguntas y variables','2 Transformaciones y registros afectados','3 Controles de calidad y hallazgos','4 Comparación de tipos y nulos','5 Diccionario de variables finales','6 Reglas y utilidad del enriquecimiento','7 Unidades por producto','8 Importe por producto','9 Resultados mensuales','10 Cobertura de modalidad']
    for s,pagina in zip(titulos,[3,4,5,5,6,7,8,8,9,10]):
        p('Tabla '+s+f'    ·    página {pagina}')
    p('Los títulos de las secciones y las tablas permiten localizarlas mediante el panel de navegación y la búsqueda de Word. Las tablas completas reutilizables se incluyen como CSV; el detalle mes y producto se entrega en ventas_mes_producto.csv.')

    nueva('1 Necesidad y diseño del análisis')
    p('En AE2 planteé una cafetería hipotética cuyo administrador necesita conocer cómo se distribuyen las unidades y los importes entre productos durante 2023. La necesidad es organizar los registros para comparar la composición del menú. No deriva de una entrevista ni de una empresa real.')
    p('Mantengo la pregunta central de AE2: ¿cómo se distribuyen las unidades vendidas y el importe total registrado entre los tipos de producto en las transacciones sintéticas de cafetería correspondientes al año 2023? P1 y P2 la descomponen; P3 desarrolla el análisis mensual ya previsto y P4 hace explícita la cobertura de modalidad, limitación identificada en AE2.')
    p('El objetivo de este avance es transformar y enriquecer el archivo seleccionado, responder las preguntas mediante tablas verificadas y dejar los datos preparados para AE4. La unidad de análisis es cada fila del CSV: no se interpreta automáticamente como un cliente o una compra completa.')
    preguntas=pd.DataFrame([
      ['P1 Unidades por producto','Item y Quantity','Producto','Unidades y % anual'],
      ['P2 Importe por producto','Item y Total Spent','Producto','USD y % anual'],
      ['P3 Variación mensual','Transaction Date, Item, Quantity y Total Spent','Mes; detalle mes y producto','USD, unidades y cambio %'],
      ['P4 Modalidad desconocida','Location y Total Spent','Modalidad','Registros, USD y cobertura %'],
    ],columns=['Pregunta','Variables originales','Nivel','Resultado'])
    tabla(1,'Relación entre preguntas y variables',preguntas,[1.45,2.15,1.35,1.95])
    p('Todas las preguntas usan Transaction Date para delimitar el año. No incorporo otra fuente de datos, conversiones a COP ni inferencias de costos. El marco conceptual de AE2 se conserva: las sumas describen unidades e importes, no márgenes; los porcentajes expresan composición y la fecha permite comparar periodos.')

    nueva('2 Metodología y transformaciones')
    p('Utilizo el archivo limpio completo cleaned_cafe_sales.csv de adityasuyal/cafe-sales-cleaned, revisión f4e6dfa1fe791ba84807921c949bd84f02b4bc69, igual a AE2. La copia original ocupa 597.388 bytes y cubre del 1 de enero al 31 de diciembre de 2023. Su SHA256 es f1271f9ecffdbd4928e21b624c71ff7fe29e1eb79d3f7426e93076e49c4b30ca. El código verifica esta huella antes de cargarlo y conserva un respaldo del DataFrame sin modificar.')
    p('La ficha declara datos sintéticos, importes en USD y licencia MIT. El publicador eliminó 460 filas sin fecha válida, imputó productos y pagos con la moda, cantidades y precios con la mediana, y recalculó los importes. Son decisiones anteriores al proyecto: no las presento como transformaciones propias. La ficha se conserva junto al CSV para que se pueda revisar esta procedencia.')
    tabla(2,'Transformaciones y registros afectados',cambios.rename(columns={'operacion':'Operación','filas_afectadas':'Filas','justificacion':'Justificación'}),[2.5,.55,3.85])
    p('Las filas afectadas por las operaciones no son aditivas: una misma fila recibe varias conversiones. El control de espacios registra cero valores corregidos. El cambio de tipos no modifica las cantidades ni los importes. Se conservan los ocho campos originales mediante nombres en español y se añaden cinco derivados; no se aplican filtros ni uniones.')

    nueva('3 Validación y comparación de calidad')
    p('Los controles se ejecutan antes de exportar. Un problema inesperado detiene el flujo para revisar el criterio. No se descartan filas ni se reemplazan valores para forzar una validación. Unknown se trata como información desconocida y no como una modalidad observada.')
    resumen=pd.DataFrame([
      ['Nulos de pandas en origen y final','0 y 0','Sin imputación'],
      ['Filas duplicadas e identificadores repetidos','0 y 0','Conservar todas las filas'],
      ['Fechas inválidas o fuera de 2023','0 y 0','Conversión exacta'],
      ['Cantidades fraccionarias; numéricos no positivos','0; 0','Enteros exactos; sin corrección'],
      ['Categorías fuera del catálogo; espacios externos','0; 0','Conservar etiquetas'],
      ['Importe distinto de cantidad por precio','0','Sin sustituir el importe'],
      ['Modalidad Unknown','3.779 filas','Conservar y medir cobertura'],
      ['Filas y columnas antes → después','9.540 × 8 → 9.540 × 13','Cinco variables nuevas'],
    ],columns=['Control','Resultado','Decisión'])
    tabla(3,'Controles de calidad y hallazgos',resumen,[3.1,1.35,2.45])
    comp=comparacion[['columna_final','tipo_antes','tipo_despues','nulos_antes','nulos_despues']].copy()
    comp.columns=['Variable final','Tipo antes','Tipo después','Nulos antes','Nulos después']
    tabla(4,'Comparación de tipos y nulos',comp,[2.1,1.05,1.35,1.0,1.0])
    p('Los cinco campos derivados no tienen nulos en el DataFrame final. La variación mensual de enero, calculada en la tabla de resultados y no en la base preparada, sí queda vacía porque falta el periodo anterior. La consistencia cantidad por precio es esperable: el publicador recalculó esa relación; no demuestra exactitud respecto de una venta real.')

    nueva('4 Diccionario actualizado')
    dic=diccionario(df)[['variable','significado','tipo','unidad']]
    dic.columns=['Variable','Significado','Tipo final','Unidad o formato']
    tabla(5,'Diccionario de variables finales',dic,[1.95,2.4,1.1,1.45])
    p('Las etiquetas de producto se conservan en inglés para asegurar correspondencia con la fuente: Coffee, Tea, Cake, Cookie, Sandwich, Salad, Juice y Smoothie. Payment Method conserva Cash, Credit Card y Digital Wallet; modalidad conserva In-store, Takeaway y Unknown. El identificador no se suma y el año se usa como delimitador, no como magnitud comercial.')
    p('El CSV guarda fechas como AAAA-MM-DD y no preserva los tipos category, Int64 o datetime de pandas. El diccionario y analisis.py documentan la reconstrucción. El diccionario exportado añade la columna origen_o_regla, con la correspondencia de nombres y las fórmulas.')

    nueva('5 Enriquecimiento y procedimiento de respuesta')
    enriquecimiento=pd.DataFrame([
      ['anio','Año extraído de fecha','Comprobar el alcance 2023'],
      ['mes','Periodo mensual de fecha en AAAA-MM','Agrupar y ordenar P3 sin mezclar años'],
      ['importe_calculado_usd','round(cantidad × precio_unitario_usd, 2)','Conciliar los importes de P2'],
      ['diferencia_importe_usd','round(importe_usd − importe_calculado_usd, 2)','Detectar desajustes sin sobrescribir el origen'],
      ['modalidad_conocida','modalidad diferente de Unknown','Medir la cobertura de P4'],
    ],columns=['Variable añadida','Fórmula o regla','Significado y utilidad'])
    tabla(6,'Reglas y utilidad del enriquecimiento',enriquecimiento,[1.9,2.5,2.5])
    p('Para P1 agrupo por producto y sumo cantidad. Divido las unidades de cada producto por las unidades anuales y multiplico por 100. Ordeno de mayor a menor y conservo el conteo de registros como contexto.')
    p('Para P2 agrupo por producto y sumo importe_usd. La participación es importe del producto dividido por el importe anual, por 100. Los importes son ingresos registrados en el archivo sintético, no utilidades; la comparación no incorpora costos.')
    p('Para P3 agrupo por mes y sumo registros, unidades e importes. La variación mensual es (importe actual / importe del mes anterior − 1) × 100. Enero se deja no disponible; no se imputa cero. Exporto además 96 filas al nivel mes y producto, conforme al diseño de AE2.')
    p('Para P4 agrupo por modalidad y calculo participación de registros e importes usando como denominador el conjunto completo, incluida Unknown. El indicador modalidad_conocida se utiliza para cuantificar la información desconocida; no se redistribuye ese grupo.')
    p('No hay uniones con otras tablas. Todas las sumas se concilian con la misma base de 9.540 filas. Las participaciones se validan antes de redondear y se exportan con diez decimales; las tablas del documento muestran dos. Puede existir una diferencia mínima al sumar porcentajes mostrados por efecto del redondeo.')

    nueva('6 Resultados por producto')
    p('P1 responde cómo se distribuyen las unidades entre los ocho productos durante 2023. El denominador es 28.850 unidades; registros indica filas del CSV.')
    u=tablas['p1_unidades_producto'].copy();u.columns=['Producto','Registros','Unidades','Participación unidades %']
    tabla(7,'Unidades por producto',u,[1.65,1.1,1.2,2.95])
    p(respuestas['P1'])
    p('P2 responde cómo se distribuyen USD 85.246,50 de importe anual entre los mismos productos.')
    v=tablas['p2_importe_producto'].copy();v.columns=['Producto','Registros','Importe USD','Participación importe %']
    tabla(8,'Importe por producto',v,[1.65,1.1,1.6,2.55])
    p(respuestas['P2'])

    nueva('7 Resultados por mes')
    p('P3 desarrolla el complemento temporal previsto en AE2. Cada fila representa un mes completo de 2023. Las unidades y los importes se agregan sin excluir modalidad desconocida. La participación usa el importe anual como denominador.')
    m=tablas['p3_ventas_mes'].copy();m.columns=['Mes','Registros','Unidades','Importe USD','Participación %','Variación mensual %']
    tabla(9,'Resultados mensuales',m,[.85,.8,.8,1.35,1.45,1.65])
    p(respuestas['P3'])
    p('El detalle adicional ventas_mes_producto.csv tiene 96 combinaciones de los doce meses y los ocho productos. Sus sumas concilian con la tabla mensual y el total anual. Esta estructura permite elaborar en AE4 líneas mensuales o comparaciones por producto sin volver a limpiar el archivo.')
    p('La tabla permite localizar máximos, mínimos y cambios relativos registrados. No se interpreta la diferencia entre meses como efecto de una promoción, del clima o de una decisión administrativa: esas variables no existen en la base. Comparar meses de distinta duración tampoco permite afirmar mayor intensidad diaria de ventas sin un cálculo específico.')

    nueva('8 Cobertura y discusión')
    p('P4 amplía el control de calidad ya señalado en AE2. Su propósito es dimensionar la limitación de modalidad, no atribuir ventas desconocidas a consumo en local o para llevar.')
    q=tablas['p4_cobertura_modalidad'].copy();q.columns=['Modalidad','Registros','Importe USD','Registros %','Importe %']
    tabla(10,'Cobertura de modalidad',q,[1.35,1.05,1.6,1.45,1.45])
    p(respuestas['P4'])
    d.add_heading('Discusión de la necesidad',2)
    p('El análisis ya permite responder la necesidad de composición por producto. Juice ocupa el primer lugar tanto en unidades como en importe. La coincidencia no debe extrapolarse a otros negocios: el archivo es sintético y contiene imputaciones previas que pueden modificar las posiciones relativas. El menú puede compararse descriptivamente, pero no se puede recomendar retirar un producto por rentabilidad sin información de costos.')
    p('La ausencia de nulos no equivale a completitud informativa. Unknown mantiene visible que falta modalidad en 39,61 % de las filas. Además, el publicador imputó variables sin entregar un indicador de imputación por registro. No es posible distinguir con este CSV qué productos, pagos, cantidades o precios fueron imputados ni calcular una sensibilidad exacta excluyendo solo esas filas.')
    p('Los 460 registros retirados por el publicador no están en la versión seleccionada. Por tanto, los resultados se refieren únicamente al archivo limpio de AE2. No se estima la composición de esos registros ni se reconstruyen fechas artificiales. La consistencia aritmética valida el flujo interno, pero no corrige estas limitaciones de procedencia.')

    nueva('9 Conclusiones y reproducción')
    p('La transformación conserva todas las filas de AE2 y permite pasar de ocho campos a trece variables documentadas. Las fechas y cantidades quedan tipadas para el análisis, los importes se mantienen en USD y cada control registra el número detectado, incluidos los resultados cero. No se necesitó eliminar registros, imputar nulos ni incorporar datos externos.')
    p('Las respuestas quedan sustentadas en tablas: Juice concentra 6.141 unidades y USD 18.249,00; junio presenta el mayor importe mensual, USD 7.417,50. Las sumas anuales concilian con 28.850 unidades y USD 85.246,50. La modalidad desconocida se conserva y se cuantifica como una limitación, con USD 33.818,50 de importe asociado.')
    p('El alcance pendiente es la representación gráfica de AE4 y, para un uso comercial real, obtener datos observados, costos y una mejor cobertura de modalidad. El avance no resuelve utilidad, inventarios, causalidad o estacionalidad. Tampoco identifica qué filas fueron imputadas por el publicador.')
    d.add_heading('Procedimiento de reproducción',2)
    for s in ['1. Clonar el repositorio de AE2 y abrir una terminal en su raíz. AE2 se conserva sin modificaciones y el avance está en AE3.',
      '2. Instalar requirements.txt en un entorno Python 3.11 o 3.12. Para regenerar el documento, instalar también AE3/requirements_documento.txt.',
      '3. Abrir AE3/notebooks/02_transformacion_enriquecimiento.ipynb y ejecutar todas las celdas. El CSV original ya está incluido, por lo que el flujo de análisis funciona sin Internet.',
      '4. Revisar AE3/datos/preparados/cafe_2023_preparado.csv y AE3/resultados. El TXT se regenera en cada ejecución y el manifiesto registra versiones y SHA256.',
      '5. Para regenerar notebook y Word desde el mismo código, ejecutar python AE3/src/construir_entrega.py. El README contiene los comandos y las rutas.']:
        p(s)
    p(f'La ejecución completa aprueba {man["validaciones_agrupaciones"]} conciliaciones de agrupaciones y comprueba mediante relectura {man["exportaciones_releidas"]} archivos CSV, incluido el dataset preparado. Se contrasta el contenido del TXT con el DataFrame final. El original permanece intacto. El manifiesto documenta las versiones efectivas de Python, pandas y NumPy; la ausencia de una semilla aleatoria no afecta el flujo porque no hay muestreo ni operaciones aleatorias.')
    d.add_heading('10 Referencias',1)
    for s in ['Osorio Gallego, J. D. (2026). Caracterización de ventas por producto en una cafetería mediante analítica descriptiva. AE2. Documento antecedente en AE2/documento/EA2_S30_Jose_David_Osorio_Gallego.docx.',
      'Suyal, A. (s. f.). Cafe Sales Dataset (Cleaned) [Dataset sintético]. Hugging Face. https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned. Revisión f4e6dfa1fe791ba84807921c949bd84f02b4bc69. Ficha consultada el 7 de noviembre de 2026 y conservada en AE3/datos/originales/FICHA_FUENTE.md.',
      'pandas. (s. f.). DataFrame, to_datetime y groupby. Documentación oficial. https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html ; https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html ; https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html .']:
        p(s)
    ruta=RAIZ/'AE3/documento/AE3_Jose_David_Osorio_Gallego.docx';d.save(ruta)
    return ruta

if __name__=='__main__':
    print('Notebook ejecutado:',notebook())
    print('Documento actualizado:',documento())
