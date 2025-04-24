import streamlit as st
import pandas as pd
import os
import difflib  # Para coincidencias aproximadas

archivo_csv = "BASE_DATOS.csv"

st.title("🔍 CARGOS ASIGNADOS SOMYL S.A.")
st.subheader("Registros encontrados.")

if not os.path.exists(archivo_csv):
    st.error(f"❌ El archivo no fue encontrado en la ruta:\n{archivo_csv}")
else:
    try:
        df = pd.read_csv(archivo_csv, encoding='latin1')
        df['CANTIDAD ENTREGADO'] = pd.to_numeric(df['CANTIDAD ENTREGADO'], errors='coerce')
        df['COSTO'] = pd.to_numeric(df['COSTO'], errors='coerce')
        df = df.dropna(subset=['CANTIDAD ENTREGADO', 'COSTO'])

        nombre_trabajador = st.sidebar.text_input("Ingrese trabajador a consultar:", "")

        df_filtrado = pd.DataFrame()

        if nombre_trabajador:
            # Lista de nombres únicos
            nombres = df['NOMBRE'].dropna().unique().tolist()

            # Buscar los nombres más similares
            coincidencias = difflib.get_close_matches(nombre_trabajador.upper(), nombres, n=10, cutoff=0.4)

            if coincidencias:
                df_filtrado = df[
                    (df['NOMBRE'].isin(coincidencias)) & (df['CANTIDAD ENTREGADO'] > 0)
                ]
                df_filtrado['COSTO TOTAL'] = df_filtrado['CANTIDAD ENTREGADO'] * df_filtrado['COSTO']
                st.subheader(f"Resultados aproximados para: {nombre_trabajador}")
                st.dataframe(df_filtrado[['NOMBRE', 'HERRAMIENTA', 'CANTIDAD ENTREGADO', 'FECHA ASIGNACION', 'COSTO', 'COSTO TOTAL']])
            else:
                st.info(f"No se encontraron coincidencias para: '{nombre_trabajador}'.")
        else:
            st.info("Ingrese un nombre en la barra lateral para buscar herramientas asignadas.")

    except Exception as e:
        st.error(f"⚠️ Error al procesar los datos:\n{e}")
