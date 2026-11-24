# Guion de sustentación · Ventas de cafetería en 2023

**José David Osorio Gallego** · Proyecto Integrado III – Analítica de Datos  
**Turno según el cronograma** · martes 24 de noviembre de 2026, 7:00 a 7:10 p. m. (Colombia)

Abre Streamlit en **Contexto** y ten a mano el PDF y el notebook de AE3. Marca los minutos 2:00 y 8:00 durante el ensayo. El cronograma asigna el turno individualmente a José David.

| Tiempo | Qué mostrar | Qué explicar |
|---|---|---|
| 0:00–1:00 | Contexto y pregunta central | La administración de una cafetería hipotética quiere saber cómo se reparten las unidades y los importes del menú. La pregunta central se divide en volumen e importe por producto, con una comparación temporal y otra de calidad. |
| 1:00–2:00 | Indicadores de la cabecera | La fuente es el CSV sintético limpio de Aditya Suyal. Cubre de enero a diciembre de 2023, con 9.540 registros de producto, 28.850 unidades y USD 85.246,50. AE3 conserva todas las filas, transforma los tipos y exporta las tablas. |
| 2:00–3:30 | P1 · Unidades. Cambia a Participación. | Se suma la cantidad por producto y se divide por las unidades anuales para obtener el porcentaje. Juice lidera con 6.141 unidades (21,29 %). Los resultados sirven para revisar el volumen, sujeto a contrastarlo con inventario y demanda observada. |
| 3:30–5:00 | P2 · Importe. Señala Juice y Coffee. | Se suma el importe por producto. Juice registra USD 18.249,00 (21,41 % anual). Coffee es segundo en unidades y sexto en importe. Las dos medidas ordenan el menú de forma distinta. Para calcular utilidad harían falta costos. |
| 5:00–6:30 | P3 · Meses. Cambia a Variación mensual. | Junio tuvo USD 7.417,50 y febrero USD 6.673,00, los extremos observados. La variación divide el importe de un mes por el anterior, resta uno y multiplica por 100. Enero queda sin comparación por falta de diciembre de 2022. |
| 6:30–8:00 | P4 · Modalidad. Abre la tabla debajo del gráfico. | Desconocida reúne 3.779 filas (39,61 %) y USD 33.818,50 (39,67 %). Cada porcentaje tiene su propio total anual. El dato recomienda mejorar la captura antes de comparar consumo en local y para llevar y las filas siguen en los totales. |
| 8:00–9:15 | Conclusiones | Revisar conjuntamente volumen e importe, incorporar costos e inventario y mejorar el registro de modalidad. Para investigar patrones mensuales, conviene comparar años y días de operación. |
| 9:15–10:00 | Alcance y enlace al repositorio | El archivo es sintético, con imputaciones previas no identificadas por fila. Presenta un año. Sirve para describir el caso y no demuestra causas, estacionalidad ni rentabilidad. El repositorio incluye el notebook, los CSV, el PDF y las instrucciones de ejecución. |

## Ensayo

Repite la secuencia de pestañas con cronómetro y confirma que puedes cambiar cada selector sin esperar a la carga de los datos. Para abrir una copia local desde la raíz, usa `python -m streamlit run streamlit_app.py`. Verifica que la cabecera muestre los tres totales y que puedas abrir el informe antes del turno.
