from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime
import requests

app = Flask(__name__)
app.secret_key = "nutriaventura"  # Necesario para usar 'session'

# --- Página principal ---
@app.route('/')
def inicio():
    # Guarda un usuario ficticio en la sesión solo para pruebas
    session["usuario"] = {"nombre": "Juan", "puntos": 80}
    return render_template("index.html")

@app.route("/personalizar", methods=["POST"])
def personalizar():
    datos = request.get_json()

    edad = int(datos.get("edad", 0))
    actividad = datos.get("actividad", "")
    preferencia = datos.get("preferencia", "")

    # Determinar "aura saludable" según la información
    if actividad == "alta":
        aura = "Verde"
    elif actividad == "media":
        aura = "Amarillo"
    else:
        aura = "Rojo"

    mensaje = f"Tu estilo {preferencia} con actividad {actividad} es ideal para equilibrar tu bienestar. 🌱"

    progreso = {
        "nivel": 1,
        "puntos": 50
    }

    # Guardar los datos en la sesión
    session["usuario"] = {
        "edad": edad,
        "actividad": actividad,
        "preferencia": preferencia,
        "aura": aura,
        "puntos": progreso["puntos"]
    }

    return jsonify({
        "aura": aura,
        "mensaje": mensaje,
        "progreso": progreso
    })

    # Luego de guardar, redirige al chat o al progreso
    return redirect(url_for('chat'))

# --- Página de progreso ---
@app.route("/progreso")
def progreso():
    usuario = session.get("usuario", None)
    if not usuario:
        return redirect(url_for("inicio"))

    puntos = usuario.get("puntos", 0)
    historial = [
        {"fecha": "2025-11-01", "puntos": 10},
        {"fecha": "2025-11-05", "puntos": 35},
        {"fecha": "2025-11-08", "puntos": 55},
        {"fecha": "2025-11-11", "puntos": puntos}
    ]

    # Envía las variables al template
    return render_template("progreso.html", puntos=puntos, historial=historial)


# --- Página del chat ---
@app.route('/chat')
def chat():
    return render_template('chat.html')


# --- Ruta de respuesta inteligente ---
@app.route('/mensaje', methods=['POST'])
def mensaje():
    data = request.get_json()
    user_input = data.get("mensaje", "")

    api_url = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
    HF_TOKEN = os.getenv("HF_TOKEN")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    response = requests.post(api_url, headers=headers, json={"inputs": user_input})

    try:
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            bot_reply = data[0]["generated_text"]
        else:
            bot_reply = "Estoy aquí para ayudarte con tus hábitos saludables 😊"
    except:
        bot_reply = "Lo siento 😅, no logré procesar eso."

    return jsonify({'respuesta': bot_reply})


@app.route("/productos")
def productos():
    productos_saludables = [
        {
            "nombre": "Galletas Tosh Avena y Miel",
            "descripcion": "Galletas integrales ricas en fibra, bajas en azúcar y perfectas para un snack saludable."
        },
        {
            "nombre": "Snacks Monticello Mix",
            "descripcion": "Mezcla nutritiva de frutos secos y arándanos, ideal para energía rápida y natural."
        },
        {
            "nombre": "Cereal Zenú Fit",
            "descripcion": "Cereal alto en fibra, bajo en grasa y excelente para un desayuno balanceado."
        },
        {
            "nombre": "Barras Tosh de Cereal",
            "descripcion": "Barras ligeras con ingredientes naturales, perfectas para llevar a cualquier lugar."
        },
        {
            "nombre": "Bebida de Avena Crem Helado Fit",
            "descripcion": "Bebida vegetal nutritiva y baja en calorías, ideal para quienes buscan opciones saludables."
        }
    ]

    return render_template("productos.html", productos=productos_saludables)




if __name__ == '__main__':
    app.run(debug=True)
    app.run(host="0.0.0.0", port=8080)
