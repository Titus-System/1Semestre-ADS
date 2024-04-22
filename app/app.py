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
    perguntas = arquivos.quiz_capitulo1
    questao = ""
    num_quest = 0
    pagina_anterior = "#"
    proxima_pagina = "#"

    if name in perguntas:
        page = "quiz_capitulo"
        questao = perguntas[name]
        verificar = name
        print(questao)

    else: page = name
    
    for i in range(len(perguntas)):
        if name == f"quiz_assunto{i+1}":
            num_quest = i+1
            proxima_pagina = f"assunto{i+2}"
            pagina_anterior = f"assunto{i+1}"
    
    if pagina_anterior in ["quiz_assunto0", "assunto0"]: pagina_anterior = "assunto1"
    if proxima_pagina == "quiz_assunto7": proxima_pagina = "fim"


    return render_template(f"/quiz/{page}.html", questao = questao, num_quest=num_quest, proxima = proxima_pagina, anterior = pagina_anterior, verificar = num_quest)



#rota de verificação das respostas do quiz
#as respostas do quiz são avaliadas pela função verificar_respostas
@app.route("/verificar_respostas/<verificar>", methods=["POST", "GET"])
def verificar_respostas(verificar):
    perguntas = arquivos.quiz_capitulo1

    respostas = {}
    acertos = 0
    salvar_como = f"resposta{verificar}"

    try:
        respostas[f"resposta{verificar}"] = request.form[f"resposta{verificar}"]
    except KeyError:
        respostas[f"resposta{verificar}"] = ""
    
    if perguntas[f"quiz_assunto{verificar}"][5] == respostas[f"resposta{verificar}"]:
        acertos += 1


    if verificar == "resultado_final":
        erros = len(perguntas) - acertos
        porcentagem = f"{(acertos/len(perguntas) * 100):.2f}%"
        return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem)

    with open("salvar_resposta.txt", "a") as file:
        file.write("resposta" + verificar + "," + respostas[salvar_como]+ "\n")

    return redirect (f"/quiz/assunto{int(verificar) + 1}")




if __name__ == "__main__":
    app.run(debug=True)