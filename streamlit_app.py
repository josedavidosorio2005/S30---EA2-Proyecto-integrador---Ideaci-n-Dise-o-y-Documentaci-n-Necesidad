"""Aplicación Streamlit de la entrega AE4."""

import altair as alt
import pandas as pd
import streamlit as st

from AE4.metricas import (
    ARCHIVOS, FUENTE, MESES, MODALIDADES, PERIODO, PREGUNTA_CENTRAL, RESULTADOS,
    calcular_hallazgos, cargar_tablas, formato, nombre_mes, pct, usd,
)


COLOR = "#11695C"
DESTACADO = "#A85C25"
REPO = (
    "https://github.com/josedavidosorio2005/"
    "S30---EA2-Proyecto-integrador---Ideaci-n-Dise-o-y-Documentaci-n-Necesidad"
)
st.set_page_config(page_title="Ventas de cafetería | Proyecto integrador", page_icon="☕", layout="wide")


@st.cache_data
def datos(version_archivos):
    """Invalida la caché si se regeneran los CSV del notebook."""
    return cargar_tablas()


def barras_productos(tabla, campo, unidad, titulo, info):
    lider = tabla.loc[tabla[campo].idxmax(), "producto"]
    return (
        alt.Chart(tabla, title=f"{titulo} · 2023")
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X(f"{campo}:Q", title=unidad, scale=alt.Scale(zero=True)),
            y=alt.Y("producto:N", sort="-x", title="Producto"),
            color=alt.condition(alt.datum.producto == lider, alt.value(COLOR), alt.value("#90B6AC")),
            tooltip=[alt.Tooltip("producto:N", title="Producto"), *info],
        )
        .properties(height=302)
    )


def tabla_detalle(tabla, clave):
    columnas = {
        "producto": "Producto", "registros": "Registros", "unidades": "Unidades",
        "importe_usd": "Importe (USD)", "participacion_unidades_pct": "% de unidades anuales",
        "participacion_importe_pct": "% del importe anual",
        "participacion_registros_pct": "% de registros anuales",
        "variacion_mensual_pct": "Variación vs. mes anterior (%)",
        "mes": "Mes", "modalidad": "Modalidad",
    }
    vista = tabla.copy()
    if "modalidad" in vista:
        vista["modalidad"] = vista["modalidad"].map(MODALIDADES)
    for columna in vista.columns:
        if columna.endswith("_pct"):
            vista[columna] = vista[columna].map(
                lambda x: "No disponible" if pd.isna(x) else formato(x, 2)
            )
        elif columna in ("unidades", "registros", "importe_usd"):
            decimales = 2 if columna == "importe_usd" else 0
            vista[columna] = vista[columna].map(lambda x: formato(x, decimales))
    with st.expander("Ver tabla de resultados y descargar CSV"):
        st.dataframe(vista.rename(columns=columnas), hide_index=True, width="stretch")
        st.download_button(
            "Descargar CSV de AE3",
            (RESULTADOS / ARCHIVOS[clave]).read_bytes(),
            ARCHIVOS[clave],
            mime="text/csv",
            key=f"descarga-{clave}",
        )


def notas(decision, limite):
    st.markdown(f"**Decisión que podría apoyar.** {decision}")
    st.caption(f"Limitación. {limite}")


try:
    rutas = [RESULTADOS / nombre for nombre in (*ARCHIVOS.values(), "matriz_preguntas.csv")]
    tablas, preguntas = datos(tuple(ruta.stat().st_mtime_ns for ruta in rutas))
    resumen = calcular_hallazgos(tablas)
except (OSError, ValueError, KeyError) as error:
    st.error(f"No se pudieron leer las tablas de AE3. Revisa las rutas del README. {error}")
    st.stop()

st.caption("PROYECTO INTEGRADO III · ANALÍTICA DE DATOS")
st.title("Ventas de cafetería en 2023")
st.markdown("Unidades, importes y cobertura de modalidad en un conjunto **sintético**.")
k1, k2, k3 = st.columns(3)
k1.metric("Registros de venta", formato(resumen["registros"]))
k2.metric("Unidades vendidas", formato(resumen["unidades"]))
k3.metric("Importe total registrado", usd(resumen["importe"]))

inicio, unidades, importe, meses, modalidad, cierre = st.tabs([
    "Contexto", "P1 · Unidades", "P2 · Importe", "P3 · Meses",
    "P4 · Modalidad", "Conclusiones",
])

with inicio:
    st.header("Necesidad del proyecto")
    st.write(
        "En una cafetería hipotética, la administración requiere conocer cómo se "
        "distribuyen las unidades y los importes del menú para orientar su revisión."
    )
    st.markdown(f"**Pregunta central.** {PREGUNTA_CENTRAL}")
    for clave, pregunta in preguntas.items():
        st.markdown(f"- **{clave}** · {pregunta}")
    st.subheader("Datos utilizados")
    st.write(
        f"Cafe Sales Dataset (Cleaned), publicado por Aditya Suyal. "
        f"El archivo limpio contiene {formato(resumen['registros'])} registros y "
        f"{resumen['productos']} productos de {PERIODO}. La unidad de análisis es una fila "
        "de producto y los importes se expresan en USD."
    )
    st.caption(
        "AE2 exploró la fuente. AE3 conservó las filas, tipó los campos y exportó las "
        "tablas. Esta aplicación lee esas exportaciones locales."
    )
    st.markdown(f"[Ficha del dataset]({FUENTE}) · [Repositorio del proyecto]({REPO})")

with unidades:
    st.header(preguntas["P1"])
    lider = resumen["unidades_lider"]
    st.markdown(
        f"**{lider.producto}** lidera con **{formato(lider.unidades)} unidades**, "
        f"equivalentes al **{pct(lider.participacion_unidades_pct)}** del total anual."
    )
    st.caption("Métrica. Suma de cantidades por producto (unidades) y su porcentaje del total anual.")
    vista = st.radio("Mostrar", ["Unidades", "Participación (%)"], horizontal=True, key="vista-p1")
    campo = "unidades" if vista == "Unidades" else "participacion_unidades_pct"
    st.altair_chart(
        barras_productos(tablas["P1"], campo, vista, "Volumen vendido por producto", [
            alt.Tooltip("unidades:Q", title="Unidades", format=",.0f"),
            alt.Tooltip("participacion_unidades_pct:Q", title="% de unidades anuales", format=".2f"),
        ]),
        width="stretch",
    )
    notas(
        "Priorizar qué productos revisar primero al planear el abastecimiento, "
        "contrastando el resultado con inventario y demanda observada.",
        "Datos sintéticos. El publicador imputó productos y cantidades y el archivo "
        "no conserva marcas por fila de esas imputaciones.",
    )
    tabla_detalle(tablas["P1"], "P1")

with importe:
    st.header(preguntas["P2"])
    lider = resumen["importe_lider"]
    posicion = tablas["P2"]["importe_usd"].rank(ascending=False, method="min").astype(int)
    cafe = tablas["P2"].assign(puesto=posicion).set_index("producto").loc["Coffee"]
    st.markdown(
        f"**{lider.producto}** suma **{usd(lider.importe_usd)}**, "
        f"el **{pct(lider.participacion_importe_pct)}** anual. "
        f"Coffee aporta {usd(cafe.importe_usd)} y ocupa el puesto {cafe.puesto} por importe."
    )
    st.caption("Métrica. Suma del importe registrado por producto (USD) y su porcentaje del total anual.")
    vista = st.radio("Mostrar", ["Importe (USD)", "Participación (%)"], horizontal=True, key="vista-p2")
    campo = "importe_usd" if vista == "Importe (USD)" else "participacion_importe_pct"
    st.altair_chart(
        barras_productos(tablas["P2"], campo, vista, "Importe registrado por producto", [
            alt.Tooltip("importe_usd:Q", title="Importe (USD)", format=",.2f"),
            alt.Tooltip("participacion_importe_pct:Q", title="% del importe anual", format=".2f"),
        ]),
        width="stretch",
    )
    notas(
        "Revisar la composición monetaria del menú junto al volumen por producto.",
        "El importe de venta mide ingresos registrados. Para estimar márgenes se "
        "necesitan costos. El publicador recalculó importes a partir de cantidades y precios.",
    )
    tabla_detalle(tablas["P2"], "P2")

with meses:
    st.header(preguntas["P3"])
    mayor, menor = resumen["mes_max"], resumen["mes_min"]
    st.markdown(
        f"El mayor importe fue en **{nombre_mes(mayor.mes)}** "
        f"(**{usd(mayor.importe_usd)}**) y el menor en **{nombre_mes(menor.mes)}** "
        f"(**{usd(menor.importe_usd)}**)."
    )
    st.caption(
        "Métricas. Suma mensual en USD y variación porcentual (importe actual / anterior − 1) × 100. "
        "Enero carece de dato del mes anterior."
    )
    vista = st.radio("Mostrar", ["Importe (USD)", "Variación mensual (%)"], horizontal=True, key="vista-p3")
    campo = "importe_usd" if vista == "Importe (USD)" else "variacion_mensual_pct"
    serie = tablas["P3"].copy()
    serie["mes_corto"] = serie["mes"].map(lambda periodo: nombre_mes(periodo)[:3].capitalize())
    orden = [mes[:3].capitalize() for mes in MESES]
    grafico = (
        alt.Chart(serie, title=f"{vista} por mes · 2023")
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("mes_corto:N", sort=orden, title="Mes de 2023", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{campo}:Q", title=vista, scale=alt.Scale(zero=True)),
            color=alt.condition(alt.datum[campo] < 0, alt.value(DESTACADO), alt.value(COLOR)),
            tooltip=[
                alt.Tooltip("mes:N", title="Mes"),
                alt.Tooltip("importe_usd:Q", title="Importe (USD)", format=",.2f"),
                alt.Tooltip("unidades:Q", title="Unidades", format=",.0f"),
                alt.Tooltip("variacion_mensual_pct:Q", title="Cambio mensual (%)", format=".2f"),
            ],
        )
        .properties(height=285)
    )
    st.altair_chart(grafico, width="stretch")
    notas(
        "Seleccionar periodos para revisar el detalle por producto y comparar contra otros años.",
        "Los meses tienen distinta duración. Un año sintético no demuestra estacionalidad "
        "ni permite atribuir causas a las diferencias.",
    )
    tabla_detalle(tablas["P3"], "P3")

with modalidad:
    st.header(preguntas["P4"])
    inc = resumen["unknown"]
    st.markdown(
        f"**Desconocida (Unknown)** reúne **{formato(inc.registros)} registros** "
        f"(**{pct(inc.participacion_registros_pct)}**) y **{usd(inc.importe_usd)}** "
        f"(**{pct(inc.participacion_importe_pct)}** del importe)."
    )
    st.caption(
        "Métricas. Conteo de filas y suma de importes por modalidad. Los porcentajes "
        "usan todos los registros y todo el importe anual, respectivamente."
    )
    cobertura = tablas["P4"].assign(etiqueta=tablas["P4"]["modalidad"].map(MODALIDADES))
    grafico = (
        alt.Chart(cobertura, title="Cobertura de modalidad por registros e importe · 2023")
        .transform_fold(
            ["participacion_registros_pct", "participacion_importe_pct"], as_=["metrica", "valor"]
        )
        .transform_calculate(medida="datum.metrica === 'participacion_registros_pct' ? 'Registros' : 'Importe'")
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            y=alt.Y("etiqueta:N", sort=list(MODALIDADES.values()), title="Modalidad"),
            yOffset="medida:N",
            x=alt.X("valor:Q", scale=alt.Scale(domain=[0, 100]), title="Participación anual (%)"),
            color=alt.Color("medida:N", title="Denominador", scale=alt.Scale(
                domain=["Registros", "Importe"], range=[COLOR, DESTACADO]
            )),
            tooltip=[
                alt.Tooltip("etiqueta:N", title="Modalidad"),
                alt.Tooltip("medida:N", title="Denominador"),
                alt.Tooltip("valor:Q", title="Participación anual (%)", format=".2f"),
            ],
        )
        .properties(height=245)
    )
    st.altair_chart(grafico, width="stretch")
    notas(
        "Priorizar la captura de modalidad completa antes de dimensionar oferta en local o para llevar.",
        "La modalidad desconocida permanece en los totales. Asignarla a una modalidad "
        "conocida cambiaría las comparaciones sin respaldo en el archivo.",
    )
    tabla_detalle(tablas["P4"], "P4")

with cierre:
    st.header("Conclusiones y recomendaciones")
    rango = resumen["mes_max"].importe_usd - resumen["mes_min"].importe_usd
    st.markdown(
        f"- **Menú.** {resumen['unidades_lider'].producto} lidera el volumen y "
        f"{resumen['importe_lider'].producto} el importe. Revisar ambas medidas junto "
        "con costos e inventarios antes de cambiar la oferta.\n"
        f"- **Tiempo.** La distancia entre el mes de mayor y menor importe fue **{usd(rango)}**. "
        "Comparar más años y días de operación antes de interpretar patrones.\n"
        f"- **Calidad.** Registrar la modalidad de forma consistente y monitorear "
        f"el **{pct(resumen['unknown'].participacion_registros_pct)}** de filas desconocidas "
        "como referencia del caso."
    )
    st.subheader("Alcance")
    st.write(
        "El análisis describe un archivo sintético de un año. La limpieza previa incluyó "
        "imputaciones sin marcas individuales y no hay datos de costos ni de inventario. "
        "Se conservan todos los registros del archivo limpio en los denominadores."
    )
    st.markdown(f"[Notebook y resultados de AE3]({REPO}/tree/main/AE3) · "
                f"[Informe completo (PDF)]({REPO}/blob/main/AE4/documento/Informe_AE4_Cafeteria.pdf)")
