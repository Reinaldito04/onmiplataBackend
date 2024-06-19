from docxtpl import DocxTemplate
import datetime

def generar_reporte(template_path, output_base_path, variables):
    # Cargar el documento de plantilla
    doc = DocxTemplate(template_path)

    # Renderizar el documento con las variables
    doc.render(variables)

    # Crear un nombre de archivo único basado en el nombre y la fecha
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
    nombre = variables['nombre'].replace(" ", "_")
    nombre_archivo = f"{output_base_path}/reporte_{nombre}_{fecha_actual}.docx"

    # Guardar el documento resultante
    doc.save(nombre_archivo)
    return nombre_archivo

# Definir las variables específicas para el reporte
variables = {
    'fecha': '2024-06-18',
    'nombre': 'Juan Pérez', 
    'inmueble': 'casa numero 8',
}

# Generar el reporte
generar_reporte('reports/documents/contratoplantilla.docx', 'reports/output', variables)
