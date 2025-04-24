import streamlit as st

st.markdown(
    """
    <style>
    body {
        background-color: #F8F8FF; /* Un color blanco ligeramente grisáceo */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# El resto de tu código de Streamlit aquí...

import pandas as pd
import streamlit as st
import os

# Ruta del archivo CSV
archivo_csv = "BASE_DATOS.csv"

st.title("🔍 Herramientas Asignadas por Trabajador")
st.subheader("Ingrese el nombre del trabajador para ver las herramientas asignadas.")

if not os.path.exists(archivo_csv):
    st.error(f"❌ El archivo no fue encontrado en la ruta:\n{archivo_csv}")
else:
    try:
        # Leer el archivo CSV
        df = pd.read_csv(archivo_csv, encoding='latin1')

        # Convertimos columnas críticas a numéricas (forzando errores a NaN)
        df['CANTIDAD ENTREGADO'] = pd.to_numeric(df['CANTIDAD ENTREGADO'], errors='coerce')
        df['COSTO'] = pd.to_numeric(df['COSTO'], errors='coerce')

        # Eliminamos filas que tengan NaN en CANTIDAD ENTREGADO o COSTO
        df = df.dropna(subset=['CANTIDAD ENTREGADO', 'COSTO'])

        # Filtro por nombre del trabajador en la barra lateral
        nombre_trabajador = st.sidebar.text_input("Buscar por nombre del trabajador:", "")

        df_filtrado = pd.DataFrame()  # Inicializamos un DataFrame vacío

        if nombre_trabajador:
            df_filtrado = df[
                (df['NOMBRE'].str.contains(nombre_trabajador, case=False, na=False)) &
                (df['CANTIDAD ENTREGADO'] > 0)
            ]
            if not df_filtrado.empty:
                # Agregar columna de costo total
                df_filtrado['COSTO TOTAL'] = df_filtrado['CANTIDAD ENTREGADO'] * df_filtrado['COSTO']

                # Mostrar resultados solo si hay un nombre y se encontraron coincidencias
                st.subheader(f"Resultados para: {nombre_trabajador}")
                st.dataframe(df_filtrado[['NOMBRE', 'HERRAMIENTA', 'CANTIDAD ENTREGADO', 'FECHA ASIGNACION', 'COSTO', 'COSTO TOTAL']])
            else:
                st.info(f"No se encontraron herramientas asignadas para el trabajador: '{nombre_trabajador}'.")
        else:
            st.info("Ingrese un nombre en la barra lateral para buscar herramientas asignadas.")

    except Exception as e:
        st.error(f"⚠️ Error al procesar los datos:\n{e}")