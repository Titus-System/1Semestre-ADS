from flask import Flask, render_template, redirect
import json

app = Flask(__name__)

@app.route("/")
def home():
    return render_template ("index.html")


@app.route("/<name>")
def get_page(name):
    if name == "apostila":
        return redirect("/apostila/introducao")
    if name == "quiz":
        return redirect ("quiz/iniciar")
    return render_template(f"{name}.html")


@app.route("/apostila/<name>")
def find_apostila(name):
    #arquivo json para guardar as páginas e ser usado para a construção do indice
    apostila_paginas = json.load(open("./static/apostila_paginas.json", encoding='utf-8'))
    return render_template(f"{name}.html", paginas = apostila_paginas)


@app.route("/quiz/<name>")
def quiz_page(name):
    return render_template(f"{name}.html")





if __name__ == "__main__":
    app.run(debug=True)