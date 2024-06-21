from docxtpl import DocxTemplate
import datetime
import os

def generar_reporte(template_path, output_base_path, variables, tipo):
    # Cargar el documento de plantilla
    doc = DocxTemplate(template_path)

    try:
        # Renderizar el documento con las variables
        doc.render(variables)

        # Crear un nombre de archivo único basado en la fecha
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"{output_base_path}/{tipo}_{fecha_actual}.docx"

        # Crear el directorio de salida si no existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Guardar el documento resultante
        doc.save(nombre_archivo)

        return nombre_archivo

    except Exception as e:
        # Manejar cualquier error que ocurra durante la generación del reporte
        raise RuntimeError(f"Error al generar el reporte: {str(e)}")

# Ejemplo de uso
template_path = 'reports/documents/plantillanotificacion.docx'
output_base_path = 'reports/output'
variables = {
    'fecha_inicio': '26 de junio 2023',
    'inquilinos': [
        {'nombre': 'LUIS MARTIN ALBILLO', 'cedula': 'V-11.902.268'},
        {'nombre': 'JUAN CARLOS ALBILLO', 'cedula': 'V-14.123.221'},
        {'nombre': 'CARLOS ALBILLO', 'cedula': 'V-14.123.221'},
        {'nombre': 'CARLOS Perez', 'cedula': 'V-12.123.221'}
    ],
    'inmueble': 'apartamento nº 2-B12',
    'items': [
        'Permitir el acceso al conjunto residencial y agregar la información de los vehículos que ocuparán el estacionamiento de la misma.',
        'Ingresar los números telefónicos de los inquilinos al grupo de WhatsApp del conjunto residencial y de esa manera estén al día con la información que por allí se facilita a todos los habitantes.'
    ],
    'vehiculos': [
        {'modelo': 'FORD KA', 'placa': 'AE984EV', 'color': 'GRIS'},
        {'modelo': 'JEEP CHEROKE', 'placa': 'BAK89R', 'color': 'MARRON'},
        {'modelo': 'FORD Fiesta', 'placa': 'AE984EV', 'color': 'GRIS'}
    ],
    'telefonos': ['0414-8207252', '0414-81278874'],
    'empresa': 'Corporación Plata, C.A.',
    'telefono_empresa': '0424-8083394 / 0414-8180523',
    'email_empresa': 'corporacionplata@gmail.com'
}
tipo = 'notificacion'

nombre_archivo = generar_reporte(template_path, output_base_path, variables, tipo)
print(f'Reporte generado: {nombre_archivo}')
