import streamlit as st
import pandas as pd
import os

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

        # Entrada de texto para buscar trabajador
        texto_busqueda = st.sidebar.text_input("Buscar parte del nombre del trabajador:", "").strip().upper()

        # Obtener nombres únicos que contienen el texto ingresado
        nombres_filtrados = sorted([nombre for nombre in df['NOMBRE'].dropna().unique() if texto_busqueda in nombre.upper()])

        # Mostrar dropdown solo si hay coincidencias
        nombre_seleccionado = None
        if nombres_filtrados:
            nombre_seleccionado = st.sidebar.selectbox("Seleccione el nombre exacto:", nombres_filtrados)
        elif texto_busqueda:
            st.sidebar.info("No se encontraron coincidencias.")

        if nombre_seleccionado:
            df_filtrado = df[
                (df['NOMBRE'] == nombre_seleccionado) & (df['CANTIDAD ENTREGADO'] > 0)
            ]
            df_filtrado['COSTO TOTAL'] = df_filtrado['CANTIDAD ENTREGADO'] * df_filtrado['COSTO']
            st.subheader(f"Resultados para: {nombre_seleccionado}")
            st.dataframe(df_filtrado[['NOMBRE', 'HERRAMIENTA', 'CANTIDAD ENTREGADO', 'FECHA ASIGNACION', 'COSTO', 'COSTO TOTAL']])
        else:
            st.info("Ingrese parte del nombre para mostrar coincidencias.")

    except Exception as e:
        st.error(f"⚠️ Error al procesar los datos:\n{e}")
