from flask import Flask, render_template, request, session, redirect, url_for
import google.generativeai as genai
import os, random, datetime

app = Flask(__name__)
app.secret_key = "nutresa_smartlife_secret_key"

# Configurar Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
modelo = genai.GenerativeModel("models/gemini-2.0-flash")

def calcular_nivel(puntos):
    if puntos < 20:
        return "Principiante 🌿", "🥦 NutriExplorador"
    elif puntos < 50:
        return "Avanzando 💪", "🥗 Hábito Saludable"
    else:
        return "Experto 🌟", "🍎 Embajador del Bienestar"

def generar_reto(estilo):
    hoy = datetime.date.today().isoformat()
    if "reto_fecha" in session and session["reto_fecha"] == hoy:
        return session["reto_actual"]
    prompt = f"Genera un reto saludable breve para alguien con estilo de vida {estilo}."
    try:
        reto = modelo.generate_content(prompt).text.strip()
    except:
        reto = random.choice([
            "Toma 8 vasos de agua hoy 💧",
            "Camina 20 minutos al aire libre 🚶‍♀️",
            "Incluye una fruta extra en tu almuerzo 🍎",
            "Haz una pausa activa de 10 minutos 🧘‍♂️"
        ])
    session["reto_actual"] = reto
    session["reto_fecha"] = hoy
    session["reto_completado"] = False
    return reto

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form["nombre"]
        estilo = request.form["estilo"]
        session["nombre"] = nombre
        session["estilo"] = estilo
        session["puntos"] = 0
        session["historial"] = []
        return redirect(url_for("chat"))
    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "nombre" not in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        mensaje = request.form["mensaje"]
        session["historial"].append({"role": "user", "text": mensaje})
        try:
            respuesta = modelo.generate_content(f"Eres NutresaBot, coach de bienestar. Responde con empatía: {mensaje}").text.strip()
        except Exception as e:
            respuesta = f"Error con IA: {e}"
        session["historial"].append({"role": "bot", "text": respuesta})
        session["puntos"] += random.randint(3, 10)

    estilo = session["estilo"]
    reto = generar_reto(estilo)
    nivel, insignia = calcular_nivel(session["puntos"])
    return render_template("chat.html",
                           nombre=session["nombre"],
                           historial=session["historial"],
                           puntos=session["puntos"],
                           nivel=nivel,
                           insignia=insignia,
                           reto=reto,
                           reto_completado=session.get("reto_completado", False))

@app.route("/completar_reto", methods=["POST"])
def completar_reto():
    if not session.get("reto_completado", False):
        session["reto_completado"] = True
        session["puntos"] += 15
    return redirect(url_for("chat"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
