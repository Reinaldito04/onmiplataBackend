import requests

# URL de tu endpoint FastAPI
url = 'http://localhost:8000/addImagen'

# Ruta completa de la imagen que deseas subir
file_path = 'imagenestest/test.png'

# Datos que quieres enviar junto con la imagen
data = {
    'inmueble_id': '1',               # Reemplaza con el ID adecuado del inmueble
    'descripcion': 'Descripción de la imagen' , # Descripción opcional de la imagen
    'image': '123'
}

try:
    with open(file_path, 'rb') as file:
        # Asegúrate de ajustar el tipo de archivo según tu imagen
        files = {'file': (file_path, file, 'image/jpeg')}

        # Realiza la solicitud POST con la imagen y los datos
        response = requests.post(url, files=files, data=data)

        # Imprime el código de estado de la respuesta y la respuesta JSON
        print('Status Code:', response.status_code)
        print('Response:', response.json())

except FileNotFoundError:
    print(f'Archivo no encontrado en la ruta especificada: {file_path}')
except Exception as e:
    print('Error:', e)
