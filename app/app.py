from flask import Flask, render_template, redirect, request
import json
import arquivos

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
    return render_template(f"{name}.html", paginas = arquivos.apostila_paginas)


#contrução do quiz
#as perguntas são retiradas do arquivo json correspondente a cada capitulo
@app.route("/quiz/<name>")
def quiz_page(name):
    perguntas = ""
    capitulo = ""
    title = ""
    lista_quiz = arquivos.rotas_quiz
    todos_quiz = arquivos.todosquiz
    pagina_anterior = "#"
    proxima_pagina = "#"

    if name in lista_quiz:
        page = "quiz_capitulo"
        capitulo = lista_quiz[lista_quiz.index(name)]
    else: page = name

    for i in range(len(lista_quiz)):
        if name == f"quiz_capitulo{i+1}":
            perguntas = todos_quiz[i]
            title = f"Capítulo {i+1}"
            proxima_pagina = f"capitulo{i+2}"
            pagina_anterior = f"capitulo{i+1}"
    
    if pagina_anterior == "capitulo0": pagina_anterior = "capitulo1"
    if proxima_pagina == "capitulo7": proxima_pagina = "fim"


    return render_template(f"/quiz/{page}.html", perguntas = perguntas, capitulo = capitulo, title = title, proxima = proxima_pagina, anterior = pagina_anterior)



#rota de verificação das respostas do quiz
#as respostas do quiz são avaliadas pela função verificar_respostas
@app.route("/verificar_respostas/<capitulo>", methods=["POST", "GET"])
def verificar_respostas(capitulo):
    lista_quiz = arquivos.rotas_quiz
    todos_quiz = arquivos.todosquiz

    for i in range(len(lista_quiz)):
        if capitulo == f"quiz_capitulo{i+1}":
            perguntas = todos_quiz[i]

    respostas = {}
    acertos = 0


    for i in range(1, len(perguntas)+1):
        try:
            respostas[f"{capitulo}resposta{i}"] = request.form[f"resposta{i}"]
        except KeyError:
            respostas[f"{capitulo}resposta{i}"] = ""
    
    for i in range(1, len(perguntas)+1):
        if perguntas[str(i)][5] == respostas[f"{capitulo}resposta{i}"]:
            acertos += 1

    erros = len(perguntas) - acertos
    porcentagem = f"{(acertos/len(perguntas) * 100):.2f}%"


    return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem)


if __name__ == "__main__":
    app.run(debug=True)