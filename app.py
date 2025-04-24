import pandas as pd
import streamlit as st
import os

# Ruta del archivo CSV
archivo_csv = r"C:\Users\carlo\OneDrive - SOMYL S.A\CARGOS\BASE_DATOS.csv"

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

        # Filtro por nombre del trabajador
        nombre_trabajador = st.text_input("Buscar por nombre del trabajador:", "")

        if nombre_trabajador:
            df_filtrado = df[
                (df['NOMBRE'].str.contains(nombre_trabajador, case=False, na=False)) &
                (df['CANTIDAD ENTREGADO'] > 0)
            ]
        else:
            df_filtrado = df[df['CANTIDAD ENTREGADO'] > 0]

        # Agregar columna de costo total
        df_filtrado['COSTO TOTAL'] = df_filtrado['CANTIDAD ENTREGADO'] * df_filtrado['COSTO']

        # Mostrar resultados
        st.title(f"📋 Herramientas asignadas a: {nombre_trabajador}" if nombre_trabajador else "📋 Herramientas asignadas")
        st.dataframe(df_filtrado[['NOMBRE', 'HERRAMIENTA', 'CANTIDAD ENTREGADO', 'FECHA ASIGNACION', 'COSTO', 'COSTO TOTAL']])

    except Exception as e:
        st.error(f"⚠️ Error al procesar los datos:\n{e}")
