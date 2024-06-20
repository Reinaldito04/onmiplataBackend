from docxtpl import DocxTemplate
import datetime

def generar_reporte(template_path, output_base_path, variables, tipo):
    # Cargar el documento de plantilla
    doc = DocxTemplate(template_path)

    try:
        # Renderizar el documento con las variables
        doc.render(variables)

        # Crear un nombre de archivo único basado en el nombre y la fecha
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        nombre = variables['nombre'].replace(" ", "_")
        nombre_archivo = f"{output_base_path}/{tipo}_{nombre}_{fecha_actual}.docx"

        # Guardar el documento resultante
        doc.save(nombre_archivo)

        return nombre_archivo

    except Exception as e:
        # Manejar cualquier error que ocurra durante la generación del reporte
        raise RuntimeError(f"Error al generar el reporte: {str(e)}")

