from fastapi import APIRouter, HTTPException
from models.Rentals import Rentals, ContractDetails,ReportData,notificacionInquilino,ReporteNotificacion,CrearInquilinoReporte,EntregaInmueble,ContratoInquilino
import os
from reports.Contrato import generar_reporte
from pydantic import ValidationError
from typing import List
from datetime import datetime,timedelta
from db.db import create_connection
from reports.Notificacionvehicular import generar_reporte as generarNotificacionVehicular
from reports.PagosContrato import ContratoInquilinoExcel
from datetime import datetime
import calendar
import locale

router = APIRouter()



locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Ajusta según tu sistema operativo

def month_year(date):
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')  # Convertir la cadena a fecha si es necesario
    month = calendar.month_name[date.month]
    year = date.year
    return f"{month.uppercase()}/{year}"

@router.post("/report-pays/{id}")
def generarReport(id: int):
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos del contrato
        cursor.execute("""
            SELECT 
                c.FechaInicio, c.FechaFin, c.Monto, c.Comision, c.FechaPrimerPago, c.DuracionMeses,
                cl.Nombre, cl.Apellido, cl.Telefono, cl.Email,
                i.Direccion AS DireccionInmueble, 
                i.Tipo AS TipoInmueble, 
                i.Descripcion AS DescripcionInmueble, 
                i.Municipio AS MunicipioInmueble
            FROM 
                Contratos c
                JOIN Clientes cl ON c.ClienteID = cl.ID
                JOIN Inmuebles i ON c.InmuebleID = i.ID
            WHERE 
                c.ID = ?
        """, (id,))
        contrato_data = cursor.fetchone()
        
        if contrato_data is None:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        
        # Obtener pagos del contrato
        cursor.execute("""
            SELECT FechaPago, Monto
            FROM Pagos
            WHERE ContratoID = ? AND TipoPago = 'Arrendamiento'
        """, (id,))
        pagos_data = cursor.fetchall()
        cursor.execute("""
                       SELECT FechaPago,Monto FROM
                       Pagos WHERE ContratoID =? AND TipoPago = 'Deposito De Garantia'
                       """,(id,))
        garantiaDeposito = cursor.fetchall()
        GarantiaSum = sum(garantia[1] for garantia in garantiaDeposito)

        # Crear una lista con los montos de los pagos formateados
        canones_mensuales = [
    {"CANON MES": f"{datetime.strptime(pago[0], '%Y-%m-%d').strftime('%B').upper()}/{datetime.strptime(pago[0], '%Y-%m-%d').strftime('%Y')}", "Cantidad": f"{pago[1]:,.2f}"}
    for pago in pagos_data
]
        
        # Crear una lista con los depósitos efectuados formateados
        depositos_efectuados = [
            {"Fecha": pago[0], "MODALIDAD": "EFECTIVO", "Cantidad": f"USD {pago[1]:,.2f}"}
            for pago in pagos_data
        ]

        # Calcular los totales
        total_contrato = f"USD {sum(pago[1] for pago in pagos_data):,.2f}"
        total_depositado = f"USD {sum(pago[1] for pago in pagos_data):,.2f}"
        fechaContrato = f"{contrato_data[0]} AL {contrato_data[1]}"
        # Mapear datos del contrato a ContratoInquilino
        contrato = ContratoInquilino(
            INQUILINO=f"{contrato_data[6]} {contrato_data[7]}",
            N_CONTACTO=contrato_data[8],
            CORREO=contrato_data[9],
            INMUEBLE=str(contrato_data[10]),  # Ajusta esto según tu tabla de inmuebles
            FECHA_CONTRATO=fechaContrato,
            CANON=str(contrato_data[2]),
            DEPOSITO_EN_GARANTIA=str(GarantiaSum),  # Ajusta esto según tu lógica
            CANONES_MENSUALES=canones_mensuales,
            TOTAL_CONTRATO=total_contrato,
            DEPOSITOS_EFECTUADOS=depositos_efectuados,
            TOTAL_DEPOSITADO=total_depositado
        )
        
        # Llamar a la función generarExcel con el contrato
        response = generarExcel(contrato)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {str(e)}")
    finally:
        if conn:
            conn.close()
def generarExcel(contrato: ContratoInquilino):
    try:
        # Crear instancia de la clase de Excel
        contrato_excel = ContratoInquilinoExcel("contrato_inquilino.xlsx")
        
        # Configurar datos del contrato desde el body de la solicitud
        contrato_excel.set_datos_inquilino({
            "INQUILINO": contrato.INQUILINO,
            "N° CONTACTO": contrato.N_CONTACTO,
            "CORREO": contrato.CORREO,
            "INMUEBLE": contrato.INMUEBLE,
            "FECHA DE CONTRATO": contrato.FECHA_CONTRATO,
            "CANON": contrato.CANON,
            "DEPOSITO EN GARANTIA": contrato.DEPOSITO_EN_GARANTIA
        })
        contrato_excel.set_canones_mensuales(contrato.CANONES_MENSUALES)
        contrato_excel.set_total_contrato(contrato.TOTAL_CONTRATO)
        contrato_excel.set_depositos_efectuados(contrato.DEPOSITOS_EFECTUADOS)
        contrato_excel.set_total_depositado(contrato.TOTAL_DEPOSITADO)
        
        # Ruta base para guardar los reportes
        output_base_path = 'reports/output'
        
        # Generar el nombre del archivo basado en la fecha y hora actual 
        # Generar el archivo Excel en la ruta especificada
        nombre_archivo_output_path = contrato_excel.write_to_excel(output_path=output_base_path)
        nombre_archivo = nombre_archivo_output_path["nombre_archivo"]
        output_path = nombre_archivo_output_path["output_path"]
                
        # Devolver un mensaje de éxito con el nombre del archivo creado
        return {"message": f"Archivo '{nombre_archivo}', creado  '{output_path}'",
                "file_path": output_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")

@router.post("/inmueble-entrega")
def entrega_inmueble(inmueble : EntregaInmueble):
    try:
        template_path = 'reports/documents/EntregaInmueble.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generarNotificacionVehicular(template_path=template_path, output_base_path=output_base_path, variables=inmueble.model_dump(),tipo="Entrega Inmueble")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)
@router.post("/generate-inquilinoreporte")
def generate_inquilino(inquilino : CrearInquilinoReporte):
    try:
        template_path = 'reports/documents/DatosInquilinos.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generarNotificacionVehicular(template_path=template_path, output_base_path=output_base_path, variables=inquilino.model_dump(),tipo="Registro de Inquilino")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)

@router.post("/generate-notificacionVehicular")
def generate_vehicular(vehicular : ReporteNotificacion):
    try:
        # Validar los datos recibidos antes de continuar
        

        template_path = 'reports/documents/plantillanotificacion.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generarNotificacionVehicular(template_path=template_path, output_base_path=output_base_path, variables=vehicular.model_dump(),tipo="Notificacion Vehicular")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)
@router.post("/generate-notificacionInquilino")
def generate_inquilino(notificacion: notificacionInquilino):
    try:
        # Validar los datos recibidos antes de continuar
        

        template_path = 'reports/documents/plantillaInquilino.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generar_reporte(template_path=template_path, output_base_path=output_base_path, variables=notificacion.model_dump(),tipo="Notificacion")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except ValidationError as validation_error:
        # Capturar errores de validación de Pydantic (por ejemplo, campos faltantes o incorrectos)
        raise HTTPException(status_code=422, detail=f"Error de validación de datos: {str(validation_error)}")
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/generate-contratReport")
def generate_report(report_data: ReportData):
    try:
        # Validar los datos recibidos antes de continuar
        validate_report_data(report_data)

        template_path = 'reports/documents/contratoplantilla.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generar_reporte(template_path, output_base_path, report_data.model_dump(),"reporte")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except ValidationError as validation_error:
        # Capturar errores de validación de Pydantic (por ejemplo, campos faltantes o incorrectos)
        raise HTTPException(status_code=422, detail=f"Error de validación de datos: {str(validation_error)}")
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)

def validate_report_data(report_data: ReportData):
    # Validar que todos los campos obligatorios estén presentes y en el formato correcto
    if not report_data.fecha:
        raise HTTPException(status_code=422, detail="Falta la fecha en los datos del reporte")
    
    if not report_data.nombre:
        raise HTTPException(status_code=422, detail="Falta el nombre en los datos del reporte")
    
    if not report_data.inmueble:
        raise HTTPException(status_code=422, detail="Falta el inmueble en los datos del reporte")
    
    if not report_data.municipio:
        raise HTTPException(status_code=422, detail="Falta el municipio en los datos del reporte")
    
    if not report_data.motivo:
        raise HTTPException(status_code=422, detail="Falta el motivo en los datos del reporte")
    
    if not report_data.fechaInicio:
        raise HTTPException(status_code=422, detail="Falta la fecha de inicio en los datos del reporte")
    else:
        try:
            # Validar que la fecha de inicio esté en el formato correcto (YYYY-MM-DD)
            datetime.strptime(report_data.fechaInicio, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato incorrecto para la fecha de inicio. Debe ser YYYY-MM-DD")
    
    if not report_data.fechaFin:
        raise HTTPException(status_code=422, detail="Falta la fecha de fin en los datos del reporte")
    else:
        try:
            # Validar que la fecha de fin esté en el formato correcto (YYYY-MM-DD)
            datetime.strptime(report_data.fechaFin, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato incorrecto para la fecha de fin. Debe ser YYYY-MM-DD")
    
    if not report_data.duracionMeses:
        raise HTTPException(status_code=422, detail="Falta la duración en meses en los datos del reporte")
    else:
        try:
            # Validar que la duración en meses sea un número entero positivo
            duracion_meses = int(report_data.duracionMeses)
            if duracion_meses <= 0:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=422, detail="La duración en meses debe ser un número entero positivo")
    
    if not report_data.monto:
        raise HTTPException(status_code=422, detail="Falta el monto en los datos del reporte")
    else:
        try:
            # Validar que el monto sea un número decimal positivo
            monto = float(report_data.monto)
            if monto <= 0:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=422, detail="El monto debe ser un número decimal positivo")
        