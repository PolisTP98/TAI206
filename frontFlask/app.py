# -----------------
# | IMPORTACIONES |
# -----------------

from flask import Flask, render_template, request, redirect, url_for
import requests


# ----------------------
# | INICIALIZAR LA APP |
# ----------------------

app = Flask(__name__, template_folder = '.', static_folder = '.')

# DEFINIR LA RUTA BASE DE LA API
API_BASE_URL = "http://localhost:5000/v1/users"


# -------------
# | ENDPOINTS |
# -------------

# ENDPOINT "inicio" (GET)
@app.route("/")
def home():
    try:
        response = requests.get(API_BASE_URL)
        if response.status_code == 200:
            data = response.json()
            users = data.get("data", [])
        else:
            users = []
    except:
        users = []
    return render_template("index.html", users = users)

# ENDPOINT "agregar_usuario" (POST)
@app.route("/add_user", methods = ["POST"])
def add_user():
    try:
        new_user = {
            "id": int(request.form["id"]), 
            "name": request.form["name"], 
            "age": int(request.form["age"]), 
            "aka": request.form["aka"]
        }
        requests.post(API_BASE_URL, json = new_user)
    except:
        pass
    return redirect(url_for("home"))

# ENDPOINT "vista_para_actualizar" (GET)
@app.route("/update_view/<int:id>")
def update_view(id):
    user = None
    try:
        response = requests.get(f"http://localhost:5000/v1/user_optional/?id={id}")
        if response.status_code == 200:
            data = response.json()
            if "user" in data:
                user = data["user"]
    except:
        pass
    return render_template("update_user.html", user = user)

# ENDPOINT "actualizar_usuario" (PUT)
@app.route("/update_user", methods = ["POST"])
def update_user():
    try:
        id = int(request.form["id"])
        updated_user = {
            "name": request.form["name"],
            "age": int(request.form["age"]),
            "aka": request.form["aka"]
        }
        requests.put(f"{API_BASE_URL}/{id}", json = updated_user)
    except:
        pass
    return redirect(url_for("home"))

# ENDPOINT "borrar_usuario" (DELETE)
@app.route("/delete_user/<int:id>")
def delete_user(id):
    try:
        requests.delete(f"{API_BASE_URL}/{id}")
    except:
        pass
    return redirect(url_for("home"))

# EJECUTAR LA APP
if __name__ == "__main__":
    app.run(debug = True, port = 8000)