"""Contrasta las exportaciones de AE3 con el CSV preparado y la fuente fijada."""

import json
from hashlib import sha256

import pandas as pd

from AE3.src import analisis
from AE4.metricas import ARCHIVOS, PREPARADO, RAIZ, RESULTADOS, cargar_tablas


def verificar():
    original, _ = analisis.cargar(RAIZ)
    preparado, _, _, _ = analisis.transformar(original)
    csv = pd.read_csv(PREPARADO, parse_dates=["fecha"])
    pd.testing.assert_frame_equal(
        csv, preparado, check_dtype=False, check_categorical=False, atol=1e-8, rtol=0
    )

    tablas_app, preguntas = cargar_tablas()
    tablas_recalculadas, conciliaciones = analisis.resultados(csv)
    assert preguntas == analisis.PREGUNTAS.set_index("pregunta_id")["pregunta"].to_dict()
    for clave, archivo in ARCHIVOS.items():
        pd.testing.assert_frame_equal(
            tablas_app[clave], tablas_recalculadas[archivo.removesuffix(".csv")].reset_index(drop=True),
            check_dtype=False, atol=1e-8, rtol=0,
        )

    manifiesto = json.loads((RESULTADOS / "manifiesto_ejecucion.json").read_text(encoding="utf-8"))
    huellas = {ruta.replace("\\", "/"): huella for ruta, huella in manifiesto["archivos_sha256"].items()}
    for ruta in (PREPARADO, *(RESULTADOS / nombre for nombre in ARCHIVOS.values())):
        assert sha256(ruta.read_bytes()).hexdigest() == huellas[ruta.relative_to(RAIZ).as_posix()], ruta
    print(f"AE4: cuatro tablas verificadas, {len(conciliaciones)} conciliaciones y cinco huellas coincidentes.")


if __name__ == "__main__":
    verificar()
