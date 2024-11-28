from flask import Flask, request, jsonify, redirect, url_for, render_template
import redis
import json

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración de Redis
client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('basehtml.html')

# Ruta para agregar una receta desde el formulario web
@app.route('/agregar', methods=['GET', 'POST'])
def agregar_receta():
    if request.method == 'POST':
        data = request.form
        nombre = data.get('nombre')

        # Validar que el nombre de la receta esté presente
        if not nombre:
            return jsonify({"error": "El nombre de la receta es requerido"}), 400

        # Recoger los datos de ingredientes y pasos como listas
        ingredientes = request.form.getlist('ingredientes')
        pasos = request.form.getlist('pasos')

        # Crear la receta con los datos recibidos
        receta = {
            "nombre": nombre,
            "ingredientes": ingredientes,  # Lista de ingredientes
            "pasos": pasos  # Lista de pasos
        }

        # Guardar la receta en Redis
        client.set(nombre, json.dumps(receta))
        return redirect(url_for('ver_recetas'))

    return render_template('recetas_html.html')  # El formulario para agregar receta

# Ruta para ver todas las recetas almacenadas
@app.route('/recetas', methods=['GET'])
def ver_recetas():
    recetas_keys = client.keys()
    recetas = []

    for key in recetas_keys:
        if client.type(key) == 'string':  # Verificar que el valor almacenado sea un string
            receta_json = client.get(key)
            if receta_json:
                try:
                    receta = json.loads(receta_json)
                    recetas.append(receta)
                except json.JSONDecodeError:
                    print(f"Advertencia: La receta con clave {key} contiene datos no válidos.")
            else:
                print(f"Advertencia: La clave {key} tiene un valor vacío o nulo.")
        else:
            print(f"Advertencia: La clave {key} no es del tipo string.")

    return render_template('ver_recetas.html', recetas=recetas)  # Mostrar todas las recetas

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
