import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
import locale

# Configuración de página completa
st.set_page_config(layout="wide")

# Ocultar menús, headers, y pie de página
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    body {overflow: hidden;}
    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Estilos personalizados
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

# Configuración local para fechas en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain')
    except:
        pass

# Archivo de datos
archivo_csv = "BASE_DATOS.csv"

# Título principal
st.markdown("<h1 style='text-align: center;'>🔍 CARGOS ASIGNADOS SOMYL S.A.</h1>", unsafe_allow_html=True)

if not os.path.exists(archivo_csv):
    st.error(f"❌ El archivo no fue encontrado en la ruta:\n{archivo_csv}")
else:
    df = pd.read_csv(archivo_csv, encoding='latin1')
    df['CANTIDAD ENTREGADO'] = pd.to_numeric(df['CANTIDAD ENTREGADO'], errors='coerce')
    df['COSTO'] = pd.to_numeric(df['COSTO'], errors='coerce')
    df = df.dropna(subset=['CANTIDAD ENTREGADO', 'COSTO'])

    # Lista de nombres
    nombres = sorted(df['NOMBRE'].dropna().unique().tolist())
    opciones_nombres = [""] + nombres

    # Sidebar
    with st.sidebar:
        nombre_seleccionado = st.selectbox(
            "Seleccione el trabajador:",
            options=opciones_nombres,
            index=0,
            format_func=lambda x: "Seleccione..." if x == "" else x
        )

    if nombre_seleccionado:
        df_filtrado = df[(df['NOMBRE'] == nombre_seleccionado) & (df['CANTIDAD ENTREGADO'] > 0)].copy()
        df_filtrado['COSTO TOTAL'] = df_filtrado['CANTIDAD ENTREGADO'] * df_filtrado['COSTO']

        df_filtrado['COSTO'] = df_filtrado['COSTO'].apply(lambda x: f"${x:,.0f}")
        df_filtrado['COSTO TOTAL'] = df_filtrado['COSTO TOTAL'].apply(lambda x: f"${x:,.0f}")

        st.subheader(f"Resultados para: {nombre_seleccionado}")
        columnas = ['HERRAMIENTA', 'CANTIDAD ENTREGADO', 'FECHA ASIGNACION', 'COSTO', 'COSTO TOTAL']
        st.dataframe(df_filtrado[columnas], use_container_width=True)

        if st.button("📄 Exportar a PDF", type="primary"):
            pdf = FPDF()
            pdf.add_page()

            # Logo
            logo_path = "logo somyl.png"
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=10, y=8, w=30)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "INFORME DE CARGOS ASIGNADOS POR SOMYL", ln=True, align="C")
            pdf.ln(15)

            # Datos del trabajador
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 10, f"NOMBRE DE TRABAJADOR: {nombre_seleccionado}", ln=True)

            # Fecha de asignación
            if not df_filtrado.empty:
                fecha = df_filtrado.iloc[0]['FECHA ASIGNACION']
                try:
                    fecha_dt = pd.to_datetime(fecha, dayfirst=True)
                    fecha_es = fecha_dt.strftime('%A, %d de %B de %Y').capitalize()
                except:
                    fecha_es = str(fecha)
                pdf.cell(0, 10, f"FECHA DE ENTREGA: {fecha_es}", ln=True)

            pdf.ln(10)

            # Columnas y posiciones
            col_widths = [70, 15, 25, 25, 30]
            col_x = [pdf.get_x()]
            for i in range(1, len(col_widths)):
                col_x.append(col_x[i-1] + col_widths[i-1])

            row_height = 7
            pdf.set_font("Arial", "B", 10)
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

            # Filas
            pdf.set_font("Arial", "", 9)
            for _, row in df_filtrado.iterrows():
                herramienta = str(row['HERRAMIENTA'])
                cantidad = str(int(row['CANTIDAD ENTREGADO']))
                fecha = str(row['FECHA ASIGNACION'])
                costo = str(row['COSTO'])
                total = str(row['COSTO TOTAL'])

                y_inicio = pdf.get_y()
                pdf.set_x(col_x[0])
                pdf.multi_cell(col_widths[0], row_height * 0.8, herramienta, border=0, align="L")
                y_despues = pdf.get_y()

                altura_fila = y_despues - y_inicio
                pdf.set_y(y_inicio)
                pdf.set_x(col_x[1])
                pdf.cell(col_widths[1], altura_fila, cantidad, border=0, align="C", ln=0)
                pdf.set_x(col_x[2])
                pdf.cell(col_widths[2], altura_fila, fecha, border=0, align="C", ln=0)
                pdf.set_x(col_x[3])
                pdf.cell(col_widths[3], altura_fila, costo, border=0, align="R", ln=0)
                pdf.set_x(col_x[4])
                pdf.cell(col_widths[4], altura_fila, total, border=0, align="R", ln=1)

                pdf.set_y(y_despues)

            # Nota de responsabilidad
            pdf.ln(10)
            pdf.set_font("Arial", "", 10)
            compromiso = (
                "Las herramientas y cargos que aparecen en este informe, representan a aquellas informadas y registradas "
                "previamente por SOMYL S.A., ante cualquier desconocimiento o diferencia, favor informar a su jefe "
                "directo o RR.HH SOMYL S.A."
            )
            pdf.multi_cell(0, 8, compromiso)

            # Guardar archivo
            nombre_pdf = f"CARGOS_{nombre_seleccionado.replace(' ', '_')}.pdf"
            pdf.output(nombre_pdf)

            # Mostrar enlace para descargar
            with open(nombre_pdf, "rb") as f:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=f,
                    file_name=nombre_pdf,
                    mime="application/pdf"
                )
