
# 🇨🇴 Colombia 2026 – Dashboard de encuestas presidenciales

Este proyecto extrae datos reales de encuestas para las elecciones presidenciales de Colombia 2026 mediante **web scraping** (con Python) y los muestra en un **dashboard interactivo** creado con Streamlit.

---

##  Contenido del repositorio

| Archivo | Descripción |
|---------|-------------|
| `colombia_2026_scraping.ipynb` | Notebook de Jupyter que realiza el scraping de las páginas web (Infobae, etc.), normaliza los datos y genera los archivos `polls_2026.parquet` y `polls_2026.csv`. |
| `dashboard_streamlit_app.py` | Aplicación principal de Streamlit. Carga los datos scrapeados y muestra gráficos interactivos, filtros, evolución temporal y tablas. |
| `requirements.txt` | Lista de dependencias de Python necesarias para ejecutar el dashboard (`streamlit`, `pandas`, `plotly`, `numpy`). |

---

##  Dashboard en vivo

Puedes ver el dashboard funcionando aquí:  
**[https://colombia-polls-dashboard-v6aejejfddeyjjbf3hmdzg.streamlit.app/](https://colombia-polls-dashboard-v6aejejfddeyjjbf3hmdzg.streamlit.app/)**  

> Nota: Los datos se actualizan cada vez que se ejecuta el notebook de scraping. El dashboard muestra siempre la última versión disponible.

---

