import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF
from datetime import datetime
import locale

# Configurar idioma español para fechas
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Linux/macOS
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain')  # Windows
    except:
        pass  # En caso de que no funcione, usará el formato por defecto

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

        texto_busqueda = st.sidebar.text_input("Buscar parte del nombre del trabajador:", "").strip().upper()
        nombres_filtrados = sorted([nombre for nombre in df['NOMBRE'].dropna().unique() if texto_busqueda in nombre.upper()])

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

            # 👉 Formato moneda
            df_filtrado['COSTO'] = df_filtrado['COSTO'].apply(lambda x: f"${x:,.0f}")
            df_filtrado['COSTO TOTAL'] = df_filtrado['COSTO TOTAL'].apply(lambda x: f"${x:,.0f}")

            st.subheader(f"Resultados para: {nombre_seleccionado}")

            columnas_a_mostrar = ['HERRAMIENTA', 'CANTIDAD ENTREGADO', 'FECHA ASIGNACION', 'COSTO', 'COSTO TOTAL']
            st.dataframe(df_filtrado[columnas_a_mostrar])

            # 👉 Exportar a PDF con diseño tipo modelo + logo + fecha asignación
            if st.button("📄 Exportar a PDF"):
                pdf = FPDF()
                pdf.add_page()

                # --- Logo ---
                logo_path = "logo somyl.png"
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=10, y=8, w=30)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "ENTREGA DE CARGOS SOMYL", ln=True, align="C")
                pdf.ln(20)

                # Obtener fecha de entrega en español
                fecha_entrega = df_filtrado.iloc[0]['FECHA ASIGNACION']
                try:
                    fecha_dt = pd.to_datetime(fecha_entrega, dayfirst=True)
                    fecha_es = fecha_dt.strftime('%A, %d de %B de %Y').capitalize()
                except:
                    fecha_es = fecha_entrega

                pdf.set_font("Arial", "", 11)
                pdf.cell(0, 10, f"NOMBRE DE TRABAJADOR: {nombre_seleccionado}", ln=True)
                pdf.cell(0, 10, f"FECHA DE ENTREGA: {fecha_es}", ln=True)
                pdf.ln(10)

                # Tabla
                pdf.set_font("Arial", "B", 11)
                pdf.cell(60, 8, "HERRAMIENTA O EPP", border=1)
                pdf.cell(30, 8, "CANTIDAD", border=1)
                pdf.cell(40, 8, "COSTO", border=1)
                pdf.cell(50, 8, "COSTO TOTAL", border=1)
                pdf.ln()

                pdf.set_font("Arial", "", 11)
                for _, row in df_filtrado.iterrows():
                    pdf.cell(60, 8, str(row['HERRAMIENTA']), border=1)
                    pdf.cell(30, 8, str(int(row['CANTIDAD ENTREGADO'])), border=1)
                    pdf.cell(40, 8, str(row['COSTO']), border=1)
                    pdf.cell(50, 8, str(row['COSTO TOTAL']), border=1)
                    pdf.ln()

                pdf.ln(10)

                # Texto compromiso
                pdf.set_font("Arial", "", 10)
                texto_compromiso = (
                    "Declaro haber recibido el equipo detallado anteriormente, en las condiciones señaladas y con todos sus accesorios y, "
                    "me comprometo a cuidarlos y utilizarlos correctamente, exclusivamente, para las actividades que son asignadas o devienen de "
                    "la labor que cumplo dentro de la empresa. Me comprometo a devolverlo cuando tenga que dejar mi cargo o servicio, independientemente del motivo. "
                    "En caso de avería por mal uso del equipo o herramienta asignado, asumo las responsabilidades por el costo del equipo menos la depreciación del mismo a la fecha. "
                    "En caso de hurto o robo, me comprometo a entregar a RRHH la denuncia a carabineros o PDI. Si esta no es presentada en un lapso de 3 días hábiles, "
                    "me hago responsable por el costo del equipo menos la depreciación. "
                    "En caso de hacer uso de licencia médica, el empleador podrá solicitar la devolución temporal o definitiva del equipo asignado."
                )
                pdf.multi_cell(0, 8, texto_compromiso)
                pdf.ln(10)

                # Firmas
                pdf.cell(0, 10, "NOMBRE Y FIRMA RRHH: __________________________________", ln=True)
                pdf.cell(0, 10, "NOMBRE Y FIRMA BODEGA SOMYL: ___________________________", ln=True)
                pdf.cell(0, 10, "NOMBRE, FIRMA Y RUT DEL TRABAJADOR: ____________________", ln=True)

                # Descargar PDF
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"cargos_{nombre_seleccionado.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("Ingrese parte del nombre para mostrar coincidencias.")

    except Exception as e:
        st.error(f"⚠️ Error al procesar los datos:\n{e}")
