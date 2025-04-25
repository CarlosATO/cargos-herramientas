import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
import locale
import math

# Configuración de página completa
st.set_page_config(layout="wide")

# Bloquear el menú de configuración, el footer y el header
st.markdown("""
    <style>
    /* Ocultar visualmente */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Bloquear por completo interacción */
    body {
        overflow: hidden;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    [data-testid="stSidebarNav"] {
        pointer-events: none;
    }
    [data-testid="stSidebar"] {
        pointer-events: none;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Tu código de aplicación a partir de aquí ---

# CSS personalizado para la estructura general
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 0rem;
}
.stDataFrame {
    width: 100% !important;
}
.stDataFrame td, .stDataFrame th {
    white-space: normal !important;
    word-wrap: break-word;
}
</style>
""", unsafe_allow_html=True)

# Configurar idioma español para fechas
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain')
    except:
        pass

archivo_csv = "BASE_DATOS.csv"

# Título centrado
st.markdown("<h1 style='text-align: center;'>🔍 CARGOS ASIGNADOS SOMYL S.A.</h1>", unsafe_allow_html=True)

if not os.path.exists(archivo_csv):
    st.error(f"❌ El archivo no fue encontrado en la ruta:\n{archivo_csv}")
else:
    try:
        # Cargar y procesar datos
        df = pd.read_csv(archivo_csv, encoding='latin1')
        df['CANTIDAD ENTREGADO'] = pd.to_numeric(df['CANTIDAD ENTREGADO'], errors='coerce')
        df['COSTO'] = pd.to_numeric(df['COSTO'], errors='coerce')
        df = df.dropna(subset=['CANTIDAD ENTREGADO', 'COSTO'])

        # Obtener lista de nombres únicos
        todos_nombres = sorted(df['NOMBRE'].dropna().unique().tolist())
        opciones_nombres = [""] + todos_nombres

        # Sidebar - Selección de trabajador
        with st.sidebar:
            nombre_seleccionado = st.selectbox(
                "Seleccione el trabajador:",
                options=opciones_nombres,
                index=0,
                format_func=lambda x: "Seleccione..." if x == "" else x
            )

        # Mostrar resultados si se seleccionó un nombre
        if nombre_seleccionado and nombre_seleccionado != "":
            df_filtrado = df[
                (df['NOMBRE'] == nombre_seleccionado) & 
                (df['CANTIDAD ENTREGADO'] > 0)
            ].copy()

            df_filtrado['COSTO TOTAL'] = df_filtrado['CANTIDAD ENTREGADO'] * df_filtrado['COSTO']

            # Formatear valores monetarios
            df_filtrado['COSTO'] = df_filtrado['COSTO'].apply(lambda x: f"${x:,.0f}")
            df_filtrado['COSTO TOTAL'] = df_filtrado['COSTO TOTAL'].apply(lambda x: f"${x:,.0f}")

            st.subheader(f"Resultados para: {nombre_seleccionado}")

            # Mostrar DataFrame
            columnas_a_mostrar = ['HERRAMIENTA', 'CANTIDAD ENTREGADO', 'FECHA ASIGNACION', 'COSTO', 'COSTO TOTAL']
            st.dataframe(
                df_filtrado[columnas_a_mostrar],
                width=1500,
                height=min(600, (len(df_filtrado) + 1) * 35 + 3),
                hide_index=True,
                column_config={
                    "HERRAMIENTA": st.column_config.TextColumn(width="large"),
                    "CANTIDAD ENTREGADO": st.column_config.NumberColumn(width="small"),
                    "FECHA ASIGNACION": st.column_config.DateColumn(width="medium"),
                    "COSTO": st.column_config.NumberColumn(width="medium"),
                    "COSTO TOTAL": st.column_config.NumberColumn(width="medium")
                }
            )

            # Exportar PDF
            if st.button("📄 Exportar a PDF", type="primary"):
                pdf = FPDF()
                pdf.add_page()

                logo_path = "logo somyl.png"
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=10, y=8, w=30)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "INFORME DE CARGOS ASIGNADOS POR SOMYL", ln=True, align="C")
                pdf.ln(15)

                pdf.set_font("Arial", "", 11)
                if not df_filtrado.empty and 'NOMBRE' in df_filtrado.columns:
                    pdf.cell(0, 10, f"NOMBRE DE TRABAJADOR: {nombre_seleccionado}", ln=True)
                else:
                    pdf.cell(0, 10, "NOMBRE DE TRABAJADOR: No disponible", ln=True)

                if not df_filtrado.empty and 'FECHA ASIGNACION' in df_filtrado.columns:
                    fecha_entrega = df_filtrado.iloc[0]['FECHA ASIGNACION']
                    try:
                        fecha_dt = pd.to_datetime(fecha_entrega, dayfirst=True)
                        fecha_es = fecha_dt.strftime('%A, %d de %B de %Y').capitalize()
                    except:
                        fecha_es = fecha_entrega
                    pdf.cell(0, 10, f"FECHA DE ENTREGA: {fecha_es}", ln=True)
                else:
                    pdf.cell(0, 10, "FECHA DE ENTREGA: No disponible", ln=True)

                pdf.ln(10)

                # Tabla
                col_widths = [70, 15, 25, 25, 30]
                col_x = [pdf.get_x()]
                for i in range(1, len(col_widths)):
                    col_x.append(col_x[i-1] + col_widths[i-1])

                row_height = 7
                pdf.set_font("Arial", "B", 10)
                current_x = pdf.get_x()
                pdf.cell(col_widths[0], row_height, "HERRAMIENTA O EPP", border=0, align="L", ln=0)
                pdf.set_x(col_x[1])
                pdf.cell(col_widths[1], row_height, "CANT", border=0, align="C", ln=0)
                pdf.set_x(col_x[2])
                pdf.cell(col_widths[2], row_height, "FECHA", border=0, align="C", ln=0)
                pdf.set_x(col_x[3])
                pdf.cell(col_widths[3], row_height, "COSTO", border=0, align="R", ln=0)
                pdf.set_x(col_x[4])
                pdf.cell(col_widths[4], row_height, "TOTAL", border=0, align="R", ln=1)
                pdf.ln(2)

                pdf.set_font("Arial", "", 9)
                for _, row in df_filtrado.iterrows():
                    herramienta = str(row['HERRAMIENTA'])
                    cantidad = str(int(row['CANTIDAD ENTREGADO']))
                    fecha = str(row['FECHA ASIGNACION'])
                    costo = str(row['COSTO'])
                    total = str(row['COSTO TOTAL'])

                    y_start_logical_row = pdf.get_y()
                    pdf.set_x(col_x[0])
                    pdf.multi_cell(col_widths[0], row_height * 0.8, herramienta, border=0, align="L")

                    y_after_multicell = pdf.get_y()

                    pdf.set_y(y_start_logical_row)
                    pdf.set_x(col_x[1])
                    pdf.cell(col_widths[1], y_after_multicell - y_start_logical_row, cantidad, border=0, align="C", ln=0)
                    pdf.set_x(col_x[2])
                    pdf.cell(col_widths[2], y_after_multicell - y_start_logical_row, fecha, border=0, align="C", ln=0)
                    pdf.set_x(col_x[3])
                    pdf.cell(col_widths[3], y_after_multicell - y_start_logical_row, costo, border=0, align="R", ln=0)
                    pdf.set_x(col_x[4])
                    pdf.cell(col_widths[4], y_after_multicell - y_start_logical_row, total, border=0, align="R", ln=1)
    except Exception as e:
        st.error(f"❌ Error cargando el archivo: {str(e)}")
