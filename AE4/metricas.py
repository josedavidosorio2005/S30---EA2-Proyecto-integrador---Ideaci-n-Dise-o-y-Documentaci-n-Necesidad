"""Tablas de AE3 y métricas compartidas por Streamlit y el informe."""

from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / "AE3" / "resultados"
PREPARADO = RAIZ / "AE3" / "datos" / "preparados" / "cafe_2023_preparado.csv"
PERIODO = "enero a diciembre de 2023"
FUENTE = "https://huggingface.co/datasets/adityasuyal/cafe-sales-cleaned"
PREGUNTA_CENTRAL = (
    "¿Cómo se distribuyen las unidades vendidas y el importe total registrado "
    "entre los tipos de producto en las transacciones sintéticas de cafetería de 2023?"
)
ARCHIVOS = {
    "P1": "p1_unidades_producto.csv",
    "P2": "p2_importe_producto.csv",
    "P3": "p3_ventas_mes.csv",
    "P4": "p4_cobertura_modalidad.csv",
}
MODALIDADES = {"In-store": "En local", "Takeaway": "Para llevar", "Unknown": "Desconocida"}
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")


def cargar_tablas():
    """Carga las cuatro exportaciones del notebook y sus preguntas."""
    tablas = {clave: pd.read_csv(RESULTADOS / archivo) for clave, archivo in ARCHIVOS.items()}
    preguntas = pd.read_csv(RESULTADOS / "matriz_preguntas.csv").set_index("pregunta_id")
    return tablas, preguntas["pregunta"].to_dict()


def formato(valor, decimales=0):
    """Usa punto de miles y coma decimal para lectura en español."""
    return f"{valor:,.{decimales}f}".translate(str.maketrans(",.", ".,"))


def usd(valor):
    return f"USD {formato(valor, 2)}"


def pct(valor):
    return f"{formato(valor, 2)} %"


def nombre_mes(periodo):
    return MESES[int(periodo[-2:]) - 1]


def calcular_hallazgos(tablas):
    p1, p2, p3, p4 = (tablas[clave] for clave in ARCHIVOS)
    return {
        "registros": int(p4["registros"].sum()),
        "unidades": int(p1["unidades"].sum()),
        "importe": float(p2["importe_usd"].sum()),
        "productos": len(p1),
        "unidades_lider": p1.loc[p1["unidades"].idxmax()],
        "importe_lider": p2.loc[p2["importe_usd"].idxmax()],
        "mes_max": p3.loc[p3["importe_usd"].idxmax()],
        "mes_min": p3.loc[p3["importe_usd"].idxmin()],
        "mes_aumento": p3.loc[p3["variacion_mensual_pct"].idxmax()],
        "mes_caida": p3.loc[p3["variacion_mensual_pct"].idxmin()],
        "unknown": p4.set_index("modalidad").loc["Unknown"],
    }
