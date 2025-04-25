import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
import locale
import math

# Configuración de página completa
st.set_page_config(layout="wide")

# CSS personalizado
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

            # Vista previa mejorada (se mantiene para la interfaz web)
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

            # Exportar a PDF (formato columnar sin bordes)
            if st.button("📄 Exportar a PDF", type="primary"):
                pdf = FPDF()
                pdf.add_page()

                # Logo (si existe)
                logo_path = "logo somyl.png"
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=10, y=8, w=30)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "INFORME DE CARGOS ASIGNADOS POR SOMYL", ln=True, align="C")
                pdf.ln(15)

                # Información del trabajador
                pdf.set_font("Arial", "", 11)
                if not df_filtrado.empty and 'NOMBRE' in df_filtrado.columns:
                    pdf.cell(0, 10, f"NOMBRE DE TRABAJADOR: {nombre_seleccionado}", ln=True)
                else:
                     pdf.cell(0, 10, "NOMBRE DE TRABAJADOR: No disponible", ln=True)


                # Fecha de entrega
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

                pdf.ln(10) # Espacio antes del contenido

                # Definir anchos de columnas y posiciones X de inicio
                col_widths = [70, 15, 25, 25, 30] # Anchos ajustados
                col_x = [pdf.get_x()] # Posición X de la primera columna
                for i in range(1, len(col_widths)):
                    col_x.append(col_x[i-1] + col_widths[i-1])

                row_height = 7 # Altura base de la línea para celdas individuales
                
                # Encabezados (sin bordes)
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
                pdf.ln(2) # Pequeño espacio después de los encabezados


                # Contenido en formato columnar sin bordes
                pdf.set_font("Arial", "", 9)
                for index, row in df_filtrado.iterrows():
                    herramienta = str(row['HERRAMIENTA'])
                    cantidad = str(int(row['CANTIDAD ENTREGADO']))
                    fecha = str(row['FECHA ASIGNACION'])
                    costo = str(row['COSTO'])
                    total = str(row['COSTO TOTAL'])

                    # Guardar la posición Y inicial de la "fila" lógica
                    y_start_logical_row = pdf.get_y()

                    # Dibujar la primera columna con multi_cell (puede ocupar varias líneas)
                    pdf.set_x(col_x[0]) # Asegurar posición X correcta
                    pdf.multi_cell(col_widths[0], row_height * 0.8, herramienta, border=0, align="L")

                    # Obtener la posición Y después del multi_cell (inicio de la línea siguiente)
                    y_after_multicell = pdf.get_y()

                    # Determinar la altura real que ocupó el multi_cell
                    # multi_cell_height = y_after_multicell - y_start_logical_row # No necesitamos esta altura para este enfoque

                    # Dibujar las celdas restantes en la línea inmediatamente después del multi_cell
                    pdf.set_y(y_start_logical_row) # Regresar a la altura donde empezó la fila lógica
                    
                    # Posicionar y dibujar las celdas restantes en sus columnas respectivas
                    pdf.set_x(col_x[1])
                    pdf.cell(col_widths[1], y_after_multicell - y_start_logical_row, cantidad, border=0, align="C", ln=0) # Usar la altura que ocupó el multicell para alinear
                    pdf.set_x(col_x[2])
                    pdf.cell(col_widths[2], y_after_multicell - y_start_logical_row, fecha, border=0, align="C", ln=0)
                    pdf.set_x(col_x[3])
                    pdf.cell(col_widths[3], y_after_multicell - y_start_logical_row, costo, border=0, align="R", ln=0)
                    pdf.set_x(col_x[4])
                    pdf.cell(col_widths[4], y_after_multicell - y_start_logical_row, total, border=0, align="R", ln=1) # ln=1 para avanzar a la siguiente fila

                    # Asegurar que la próxima fila comience en la posición Y correcta (justo después del multi_cell más alto)
                    pdf.set_y(y_after_multicell) # Mover el cursor a la línea después del multicell

                    # pdf.ln(2) # Espacio opcional entre "filas" lógicas si se desea más separación

                # Texto compromiso
                pdf.ln(10)
                pdf.set_font("Arial", "", 10)
                texto_compromiso = (
                    "Las herramientas y cargos que aparecen en este informe, representan a aquellas informadas y registradas "
                    "previamente por SOMYL S.A., ante cualquier desconocimiento o diferencia, favor informar a su jefe "
                    "directo o RR.HH SOMYL S.A."
                )
                pdf.multi_cell(0, 8, texto_compromiso)

                # Descargar PDF
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="📥 Descargar PDF listo",
                    data=pdf_bytes,
                    file_name=f"cargos_{nombre_seleccionado.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("Seleccione un trabajador de la lista para mostrar información.")

    except Exception as e:
        st.error(f"⚠️ Error al procesar los datos:\n{str(e)}")