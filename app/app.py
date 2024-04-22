from flask import Flask, render_template, redirect, request, session
import json
import arquivos

app = Flask(__name__)

app.secret_key = "chave_secreta"

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
    perguntas = arquivos.quiz_perguntas
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
    if proxima_pagina in ["quiz_assunto7", "assunto7"]: proxima_pagina = "resultado"


    return render_template(f"/quiz/{page}.html", questao = questao, num_quest=num_quest, proxima = proxima_pagina, anterior = pagina_anterior, verificar = num_quest)



#rota para salvar as respostas do usuário
@app.route("/salvar_respostas/<verificar>", methods=["POST", "GET"])
def salvar_respostas(verificar):
    # perguntas = arquivos.quiz_perguntas

    # respostas = {}
    # acertos = 0

    try:
        session[f"resposta{verificar}"] = request.form[f"resposta{verificar}"]
    except KeyError:
        session[f"resposta{verificar}"] = ""
    
    # if perguntas[f"quiz_assunto{verificar}"][5] == session[f"resposta{verificar}"]:
    #     acertos += 1


    # if verificar == "resultado_final":
    #     resposta1 = session.get("resposta1", "")
    #     resposta2 = session.get("resposta2", "")
    #     erros = len(perguntas) - acertos
    #     porcentagem = f"{(acertos/len(perguntas) * 100):.2f}%"
    #     return render_template("/quiz/resultado.html", resposta1=resposta1, resposta2=resposta2)

    return redirect (f"/quiz/assunto{int(verificar) + 1}")


#rota para verificação dos resultados do quiz e visualização da página de resultados
@app.route("/quiz/resultado")
def resultado():
    perguntas = arquivos.quiz_perguntas
    acertos = 0
    resposta1 = session.get("resposta1", "")
    resposta2 = session.get("resposta2", "")
    resposta3 = session.get("resposta3", "")

    respostas = [resposta1, resposta2, resposta3]

    for i in range(1, len(respostas)+1):
        if perguntas[f"quiz_assunto{i}"][5] == session[f"resposta{i}"]:
            acertos += 1

    erros = len(perguntas) - acertos
    porcentagem = f"{(acertos/len(perguntas) * 100):.2f}%"


    return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem)


if __name__ == "__main__":
    app.run(debug=True)