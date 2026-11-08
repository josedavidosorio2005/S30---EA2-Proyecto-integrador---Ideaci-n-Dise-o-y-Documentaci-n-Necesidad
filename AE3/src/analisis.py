"""Flujo AE3 reproducible. No elimina filas ni imputa valores del CSV de AE2."""
from pathlib import Path
from io import StringIO
import hashlib
import json
import platform
import numpy as np
import pandas as pd

REVISION = 'f4e6dfa1fe791ba84807921c949bd84f02b4bc69'
URL = f'https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned/resolve/{REVISION}/cleaned_cafe_sales.csv'
NOMBRES = {'Transaction ID':'id_transaccion','Item':'producto','Quantity':'cantidad',
 'Price Per Unit':'precio_unitario_usd','Total Spent':'importe_usd',
 'Payment Method':'medio_pago','Location':'modalidad','Transaction Date':'fecha'}
PREGUNTAS = pd.DataFrame([
 ['P1','¿Cómo se distribuyen las unidades vendidas entre productos en 2023?','Item, Quantity, Transaction Date','Producto','Unidades y participación porcentual','p1_unidades_producto.csv'],
 ['P2','¿Cómo se distribuye el importe registrado entre productos en 2023?','Item, Total Spent, Transaction Date','Producto','USD y participación porcentual','p2_importe_producto.csv'],
 ['P3','¿Cómo varían los importes registrados por mes durante 2023?','Transaction Date, Item, Total Spent, Quantity','Mes; complemento mes y producto','USD, unidades y variación mensual porcentual','p3_ventas_mes.csv'],
 ['P4','¿Qué proporción de registros e importes tiene modalidad desconocida?','Location, Total Spent','Modalidad','Registros, USD y porcentajes de cobertura','p4_cobertura_modalidad.csv'],
], columns=['pregunta_id','pregunta','variables_originales','nivel','resultado_esperado','archivo'])

def cargar(raiz):
    ruta = Path(raiz)/'AE3/datos/originales/cleaned_cafe_sales.csv'
    esperado = 'f1271f9ecffdbd4928e21b624c71ff7fe29e1eb79d3f7426e93076e49c4b30ca'
    if hashlib.sha256(ruta.read_bytes()).hexdigest() != esperado:
        raise ValueError('El CSV no coincide con la revisión de AE2; verificar procedencia.')
    return pd.read_csv(ruta), ruta

def transformar(original):
    """Falla ante problemas nuevos: exige revisar el criterio antes de cambiar datos."""
    if set(original.columns) != set(NOMBRES):
        raise ValueError('El esquema difiere de AE2; revisar antes de transformar.')
    df = original.copy(deep=True).rename(columns=NOMBRES)
    controles = []
    def control(nombre, n, criterio, accion='Conservar; no se detectó problema'):
        controles.append([nombre, int(n), criterio, accion])
    nulos = int(df.isna().sum().sum())
    control('Valores nulos en origen',nulos,'No imputar automáticamente')
    if nulos: raise ValueError('Se detectaron nulos; requiere decisión explícita.')
    for c in ['id_transaccion','producto','medio_pago','modalidad']:
        limpia = df[c].astype('string').str.strip()
        n = int((df[c] != limpia).sum())
        control('Espacios externos en '+c,n,'Recortar espacios sin alterar significado','Recorte aplicado' if n else 'Sin cambios de contenido')
        df[c] = limpia
        assert df[c].str.len().gt(0).all(), f'Valores vacíos en {c}'
    dup = int(df.duplicated().sum()); ids = int(df.id_transaccion.duplicated().sum())
    control('Filas duplicadas',dup,'No borrar sin identificar su causa')
    control('Identificadores duplicados',ids,'Se exige identificador único')
    assert dup == ids == 0, 'Duplicados nuevos: revisar antes de continuar'
    fecha = pd.to_datetime(df.fecha,format='%Y-%m-%d',errors='coerce')
    invalidas = int(fecha.isna().sum())
    control('Fechas inválidas',invalidas,'Formato exacto AAAA-MM-DD; detener si falla')
    assert invalidas == 0
    df['fecha'] = fecha
    fuera = int((df.fecha.dt.year != 2023).sum())
    control('Registros fuera de 2023',fuera,'Alcance anual definido en AE2')
    assert fuera == 0
    for c in ['cantidad','precio_unitario_usd','importe_usd']:
        df[c] = pd.to_numeric(df[c],errors='raise')
        n = int((~np.isfinite(df[c]) | df[c].le(0)).sum())
        control('No positivos o no finitos en '+c,n,'Cantidad, precio e importe deben ser positivos')
        assert n == 0
    no_enteras = int((df.cantidad % 1 != 0).sum())
    control('Cantidades fraccionarias',no_enteras,'Convertir a entero solo si no pierde información')
    assert no_enteras == 0
    df['cantidad'] = df.cantidad.astype('Int64')
    esperados = {'producto':{'Coffee','Tea','Cake','Cookie','Sandwich','Salad','Juice','Smoothie'},
                 'medio_pago':{'Cash','Credit Card','Digital Wallet'},
                 'modalidad':{'In-store','Takeaway','Unknown'}}
    for c, categorias in esperados.items():
        n = int((~df[c].isin(categorias)).sum())
        control('Categorías fuera del catálogo en '+c,n,'Catálogo de la ficha fuente; Unknown es categoría válida')
        assert n == 0
        df[c] = df[c].astype('category')
    df['anio'] = df.fecha.dt.year.astype('int16')
    df['mes'] = df.fecha.dt.to_period('M').astype('string')
    df['importe_calculado_usd'] = (df.cantidad.astype(float)*df.precio_unitario_usd).round(2)
    df['diferencia_importe_usd'] = (df.importe_usd-df.importe_calculado_usd).round(2)
    desajustes = int(df.diferencia_importe_usd.abs().gt(0.005).sum())
    control('Desajustes cantidad por precio',desajustes,'Tolerancia medio centavo; no sustituir el importe original')
    assert desajustes == 0
    df['modalidad_conocida'] = df.modalidad.ne('Unknown')
    unknown = int((~df.modalidad_conocida).sum())
    control('Modalidad desconocida',unknown,'No imputar ni excluir; cuantificar la cobertura','Conservar Unknown y añadir indicador booleano')
    assert len(df) == len(original) and df.id_transaccion.is_unique
    calidad = pd.DataFrame(controles,columns=['control','registros_o_valores_detectados','criterio','tratamiento'])
    comparacion = pd.DataFrame([{
       'columna_original':a,'columna_final':b,'tipo_antes':str(original[a].dtype),
       'tipo_despues':str(df[b].dtype),'nulos_antes':int(original[a].isna().sum()),
       'nulos_despues':int(df[b].isna().sum())} for a,b in NOMBRES.items()])
    cambios = pd.DataFrame([
      ['Renombrar 8 columnas',len(df),'Etiquetas en español; no cambia valores'],
      ['Convertir fecha de texto a datetime',len(df),'Permite delimitar el año y agrupar meses'],
      ['Convertir cantidad de float64 a Int64',len(df),'Todas las cantidades son enteras; sin redondeo'],
      ['Tipar producto, pago y modalidad como category',len(df),'Tres campos por fila; se conservan etiquetas y Unknown'],
      ['Recortar espacios externos',sum(x[1] for x in controles if x[0].startswith('Espacios')),'Sin correcciones si el conteo es cero'],
      ['Eliminar filas',0,'No se detectan problemas que justifiquen eliminación'],
      ['Imputar faltantes',0,'El CSV limpio no contiene nulos; Unknown se conserva'],
      ['Cambiar unidad monetaria',0,'Se mantiene USD; no se convierte a COP'],
      ['Añadir cinco variables derivadas',len(df),'Año, mes, importe calculado, diferencia y cobertura'],
    ],columns=['operacion','filas_afectadas','justificacion'])
    return df, calidad, comparacion, cambios

def resultados(df):
    unidades = df.groupby('producto',observed=True).agg(registros=('id_transaccion','size'),unidades=('cantidad','sum')).reset_index()
    unidades['participacion_unidades_pct'] = unidades.unidades / df.cantidad.sum()*100
    unidades = unidades.sort_values(['unidades','producto'],ascending=[False,True]).reset_index(drop=True)
    importes = df.groupby('producto',observed=True).agg(registros=('id_transaccion','size'),importe_usd=('importe_usd','sum')).reset_index()
    importes['participacion_importe_pct'] = importes.importe_usd / df.importe_usd.sum()*100
    importes = importes.sort_values(['importe_usd','producto'],ascending=[False,True]).reset_index(drop=True)
    mes = df.groupby('mes',observed=True).agg(registros=('id_transaccion','size'),unidades=('cantidad','sum'),importe_usd=('importe_usd','sum')).reset_index().sort_values('mes')
    mes['participacion_importe_pct'] = mes.importe_usd / df.importe_usd.sum()*100
    mes['variacion_mensual_pct'] = mes.importe_usd.pct_change(fill_method=None)*100
    # Enero queda vacío porque diciembre de 2022 no está disponible; no se imputa cero.
    modalidad = df.groupby('modalidad',observed=True).agg(registros=('id_transaccion','size'),importe_usd=('importe_usd','sum')).reset_index()
    modalidad['participacion_registros_pct'] = modalidad.registros/len(df)*100
    modalidad['participacion_importe_pct'] = modalidad.importe_usd/df.importe_usd.sum()*100
    detalle = df.groupby(['mes','producto'],observed=True).agg(registros=('id_transaccion','size'),unidades=('cantidad','sum'),importe_usd=('importe_usd','sum')).reset_index()
    tablas = dict(p1_unidades_producto=unidades,p2_importe_producto=importes,p3_ventas_mes=mes,p4_cobertura_modalidad=modalidad,ventas_mes_producto=detalle)
    verificaciones=[]
    def verificar(nombre,condicion):
        assert condicion, nombre
        verificaciones.append({'validacion':nombre,'resultado':'APROBADA'})
    for nombre,t in tablas.items():
        verificar(nombre+' conserva registros', int(t.registros.sum())==len(df))
        if 'importe_usd' in t:
            verificar(nombre+' conserva total USD',np.isclose(t.importe_usd.sum(),df.importe_usd.sum(),atol=0.005,rtol=0))
        if 'unidades' in t:
            verificar(nombre+' conserva unidades',int(t.unidades.sum())==int(df.cantidad.sum()))
        for c in t.columns:
            if c.startswith('participacion_'):
                verificar(nombre+' '+c+' suma 100',np.isclose(t[c].sum(),100,atol=1e-10,rtol=0))
    verificar('Los doce meses de 2023 están presentes',list(mes.mes)==[f'2023-{m:02}' for m in range(1,13)])
    verificar('Detalle contiene 12 meses por 8 productos',len(detalle)==96)
    verificar('Solo enero carece de variación intermensual',mes.variacion_mensual_pct.isna().sum()==1 and pd.isna(mes.iloc[0].variacion_mensual_pct))
    return tablas,pd.DataFrame(verificaciones)

def interpretaciones(df,tablas):
    u=tablas['p1_unidades_producto'].iloc[0]; v=tablas['p2_importe_producto'].iloc[0]
    m=tablas['p3_ventas_mes']; mayor=m.loc[m.importe_usd.idxmax()]; menor=m.loc[m.importe_usd.idxmin()]
    pico=m.loc[m.variacion_mensual_pct.idxmax()]; caida=m.loc[m.variacion_mensual_pct.idxmin()]
    inc=tablas['p4_cobertura_modalidad'].query("modalidad == 'Unknown'").iloc[0]
    return {
    'P1':f"{u.producto} concentra el mayor número de unidades: {int(u.unidades):,}, equivalentes al {u.participacion_unidades_pct:.2f}% de {int(df.cantidad.sum()):,} unidades anuales. Esta distribución permite comparar el volumen del menú en el escenario académico. No representa demanda real: el publicador imputó productos con la moda y cantidades con la mediana; el archivo limpio no identifica qué filas fueron imputadas.",
    'P2':f"{v.producto} aporta el mayor importe: USD {v.importe_usd:,.2f}, el {v.participacion_importe_pct:.2f}% de USD {df.importe_usd.sum():,.2f}. El liderazgo por importe y por unidades puede diferir porque interviene el precio unitario. La tabla sirve para comparar composición de importes, sin concluir rentabilidad. El total fue recalculado por el publicador a partir de cantidades y precios, algunos imputados.",
    'P3':f"El mayor importe mensual corresponde a {mayor.mes}, con USD {mayor.importe_usd:,.2f}; el menor, a {menor.mes}, con USD {menor.importe_usd:,.2f}. El mayor aumento frente al mes previo ocurre en {pico.mes} ({pico.variacion_mensual_pct:.2f}%) y la mayor caída en {caida.mes} ({caida.variacion_mensual_pct:.2f}%). Enero no tiene variación calculable por falta de diciembre de 2022. Esta tabla permite planear la comparación temporal de AE4. Un solo año sintético no demuestra estacionalidad ni permite atribuir causas; los meses tienen distinta duración.",
    'P4':f"Unknown agrupa {int(inc.registros):,} registros ({inc.participacion_registros_pct:.2f}%) y USD {inc.importe_usd:,.2f} ({inc.participacion_importe_pct:.2f}% del importe). La cobertura limita cualquier comparación entre consumo en local y para llevar. Estos registros se mantienen en los totales por producto y por mes; no se redistribuyen a una modalidad conocida.",
    }

def diccionario(df):
    textos = {
    'id_transaccion':('Identificador del registro original','Sin unidad','Transaction ID; conservar unicidad'),
    'producto':('Producto del menú','Categoría','Item; mismas ocho etiquetas'),
    'cantidad':('Unidades del registro','Unidades','Quantity; conversión exacta a entero'),
    'precio_unitario_usd':('Precio por unidad','USD/unidad','Price Per Unit; sin conversión monetaria'),
    'importe_usd':('Importe del registro en el CSV limpio','USD','Total Spent; se conserva'),
    'medio_pago':('Medio de pago registrado','Categoría','Payment Method; etiquetas originales'),
    'modalidad':('Modalidad declarada o desconocida','Categoría','Location; Unknown se mantiene'),
    'fecha':('Fecha de la transacción','AAAA-MM-DD','Transaction Date; pd.to_datetime con formato exacto'),
    'anio':('Año de cobertura','Año','fecha.dt.year; verifica alcance 2023'),
    'mes':('Periodo de agregación','AAAA-MM','fecha.dt.to_period("M"); responde P3'),
    'importe_calculado_usd':('Importe independiente de comprobación','USD','round(cantidad × precio_unitario_usd, 2); valida P2'),
    'diferencia_importe_usd':('Diferencia de conciliación','USD','round(importe_usd − importe_calculado_usd, 2); valida P2'),
    'modalidad_conocida':('Indicador de cobertura','Booleano','modalidad != "Unknown"; responde P4'),
    }
    return pd.DataFrame([dict(variable=c,significado=textos[c][0],tipo=str(df[c].dtype),unidad=textos[c][1],origen_o_regla=textos[c][2]) for c in df])

def resumen_descriptivo(df,ruta_origen):
    info=StringIO(); df.info(buf=info)
    esquema=pd.DataFrame({'tipo':df.dtypes.astype(str),'nulos':df.isna().sum(),'porcentaje_nulos':df.isna().mean()*100})
    categoricas='\n\n'.join(c+'\n'+df[c].value_counts(dropna=False).to_string() for c in ['producto','medio_pago','modalidad','modalidad_conocida'])
    texto=(f'AE3 | Jose David Osorio Gallego\nDataset: adityasuyal/cafe-sales-cleaned\nRevisión: {REVISION}\n'
       f'SHA256 CSV original: {hashlib.sha256(Path(ruta_origen).read_bytes()).hexdigest()}\n'
       f'Filas: {len(df)}\nColumnas: {len(df.columns)}\n'
       f'Periodo: {df.fecha.min():%Y-%m-%d} a {df.fecha.max():%Y-%m-%d}\n'
       f'Unidades totales: {int(df.cantidad.sum())}\nImporte total USD: {df.importe_usd.sum():.2f}\n'
       f'Modalidad Unknown: {int((~df.modalidad_conocida).sum())}\n\nESQUEMA Y NULOS\n{esquema.to_string()}\n\n'
       f'DATAFRAME.INFO\n{info.getvalue()}\nESTADÍSTICAS NUMÉRICAS\n{df.select_dtypes("number").describe().to_string()}\n\n'
       f'ESTADÍSTICAS TEMPORALES\n{df[["fecha"]].describe().to_string()}\n\n'
       f'FRECUENCIAS CATEGÓRICAS\n{categoricas}\n\n'
       'LIMITACIONES\nDatos sintéticos. No se infieren rentabilidad, causalidad ni estacionalidad.\n'
       'El publicador imputó variables y recalculó importes; no hay marcas de imputación por fila.\n'
       'Unknown expresa información desconocida aunque isna() reporte cero.\n')
    return texto

def exportar(raiz,original,df,calidad,comparacion,cambios,tablas,validaciones,ruta_origen):
    raiz=Path(raiz); salida=raiz/'AE3/resultados'; salida.mkdir(parents=True,exist_ok=True)
    preparado=raiz/'AE3/datos/preparados/cafe_2023_preparado.csv'; preparado.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(preparado,index=False,date_format='%Y-%m-%d',encoding='utf-8',float_format='%.10f')
    archivos={**tablas,'controles_calidad':calidad,'comparacion_esquema':comparacion,'registro_transformaciones':cambios,'diccionario_datos':diccionario(df),'matriz_preguntas':PREGUNTAS,'validaciones':validaciones}
    for nombre,t in archivos.items():
        destino=salida/(nombre+'.csv')
        t.to_csv(destino,index=False,encoding='utf-8',float_format='%.10f')
        releido=pd.read_csv(destino)
        assert list(releido.columns)==list(t.columns) and len(releido)==len(t)
        for c in t.select_dtypes('number').columns:
            assert np.allclose(releido[c].astype(float),t[c].astype(float),atol=1e-8,rtol=0,equal_nan=True), (nombre,c)
        reconstruido=releido.copy()
        for c in t:
            reconstruido[c]=reconstruido[c].astype(t[c].dtype)
        pd.testing.assert_frame_equal(reconstruido,t.reset_index(drop=True),check_exact=False,atol=1e-8,rtol=0)
    releido=pd.read_csv(preparado)
    assert len(releido)==len(df) and list(releido)==list(df)
    assert releido.id_transaccion.tolist()==df.id_transaccion.tolist()
    for c in df.select_dtypes('number'):
        assert np.allclose(releido[c].astype(float),df[c].astype(float),atol=1e-8,rtol=0)
    # Reconstruye tipos de pandas, que el formato CSV no conserva, y compara todas las celdas.
    restaurado=releido.copy()
    for c in df:
        if pd.api.types.is_datetime64_any_dtype(df[c]): restaurado[c]=pd.to_datetime(restaurado[c])
        else: restaurado[c]=restaurado[c].astype(df[c].dtype)
    pd.testing.assert_frame_equal(restaurado,df,check_exact=False,atol=1e-8,rtol=0)
    texto=resumen_descriptivo(df,ruta_origen)
    txt=salida/'resumen_dataframe.txt'; txt.write_text(texto,encoding='utf-8')
    assert txt.read_text(encoding='utf-8')==resumen_descriptivo(df,ruta_origen)
    respuestas=interpretaciones(df,tablas)
    (salida/'interpretaciones.json').write_text(json.dumps(respuestas,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifiesto={'revision_fuente':REVISION,'url_fuente':URL,'sha256_original':hashlib.sha256(Path(ruta_origen).read_bytes()).hexdigest(),
       'filas_antes':len(original),'columnas_antes':len(original.columns),'filas_despues':len(df),'columnas_despues':len(df.columns),
       'unidades':int(df.cantidad.sum()),'importe_usd':float(df.importe_usd.sum()),
       'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,
       'validaciones_agrupaciones':len(validaciones),'exportaciones_releidas':len(archivos)+1,
       'archivos_sha256':{str(p.relative_to(raiz)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [preparado,*sorted(salida.glob('*.csv')),txt,salida/'interpretaciones.json']}}
    (salida/'manifiesto_ejecucion.json').write_text(json.dumps(manifiesto,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifiesto

def ejecutar(raiz):
    original,ruta=cargar(raiz)
    copia=original.copy(deep=True)
    df,calidad,comparacion,cambios=transformar(original)
    pd.testing.assert_frame_equal(original,copia)
    tablas,validaciones=resultados(df)
    manifiesto=exportar(raiz,original,df,calidad,comparacion,cambios,tablas,validaciones,ruta)
    return df,tablas,manifiesto

if __name__=='__main__':
    raiz=Path(__file__).resolve().parents[2]
    _,_,manifiesto=ejecutar(raiz)
    print(json.dumps(manifiesto,ensure_ascii=False,indent=2))
