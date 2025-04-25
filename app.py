import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import base64

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Informe de Cargos - SOMYL", layout="centered")

# 🔒 Ocultar menú de configuración, header y footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# TÍTULO
st.title("📋 Informe de Cargos Asignados por SOMYL")

# LOGO (opcional)
# st.image("logo.png", width=150)

# SUBIR ARCHIVO EXCEL
archivo = st.file_uploader("📎 Cargar archivo Excel", type=["xlsx"])

if archivo:
    try:
        # Leer archivo y mostrar hoja a elegir
        xl = pd.ExcelFile(archivo)
        hojas = xl.sheet_names
        hoja_seleccionada = st.selectbox("📄 Selecciona la hoja", hojas)

        df = xl.parse(hoja_seleccionada)

        if df.empty:
            st.warning("La hoja seleccionada está vacía.")
        else:
            # Mostrar tabla
            st.subheader("📊 Datos cargados:")
            st.dataframe(df, use_container_width=True)

            # Botón para generar PDF
            if st.button("📤 Exportar a PDF"):
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=10)

                # Título
                pdf.set_font("Arial", "B", 12)
                pdf.cell(200, 10, txt="Informe de Cargos - SOMYL", ln=True, align='C')
                pdf.ln(10)

                # Encabezados
                pdf.set_font("Arial", "B", 10)
                for col in df.columns:
                    pdf.cell(40, 10, str(col), border=1)
                pdf.ln()

                # Filas
                pdf.set_font("Arial", "", 9)
                for i, row in df.iterrows():
                    for col in row:
                        texto = str(col)
                        if len(texto) > 25:
                            texto = texto[:22] + "..."
                        pdf.cell(40, 10, texto, border=1)
                    pdf.ln()

                # Guardar en memoria
                buffer = BytesIO()
                pdf.output(buffer)
                buffer.seek(0)

                # Generar link de descarga
                b64 = base64.b64encode(buffer.read()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_somyl.pdf">📥 Descargar PDF generado</a>'
                st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

