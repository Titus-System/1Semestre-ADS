from flask import Flask, render_template, redirect, request, session
import json
import arquivos
import database
import functions
app = Flask(__name__)

app.secret_key = "chave_secreta"

database.initialize_database() #Inicia o banco de dados

@app.route("/")
def home():
    return render_template ("index.html")

@app.route("/<name>")
def get_page(name):
    if name == "apostila":
        return redirect("/apostila/introducao")
    if name == "quiz":
        return redirect ("quiz/iniciar")
    if name == "ferramentas":
        return redirect("/ferramentas/ferramentas")
    if name == "avaliação":
        return redirect("/avaliacao")
    return render_template(f"{name}.html")

@app.route("/ferramentas/<name>")
def ferramentas(name):
    return render_template(f"/ferramentas/{name}.html")


@app.route("/apostila/<name>")
def find_apostila(name):
    #arquivo json para guardar as páginas e ser usado para a construção do indice
    apostila_paginas = json.load(open("./static/apostila_paginas.json", encoding='utf-8'))
    return render_template(f"/apostila/{name}.html", paginas = arquivos.apostila_paginas)


#contrução do quiz
#as perguntas são retiradas do arquivo json correspondente a cada capitulo
@app.route("/quiz/<name>", methods=["POST", "GET"])
def quiz_page(name=str):
    perguntas = arquivos.quiz_perguntas
    questao = ""
    num_quest = 0
    page = name
    pagina_atual = name
    proxima_pagina = "#"
    pagina_anterior = "#"


    if name in perguntas.keys():
        page = "pergunta"
        questao = perguntas[name]
        num_quest = questao[0]
        proxima_pagina = questao[8]
        pagina_anterior = f"{questao[0]}_{name}"
    
    if request.method == "POST":
        questao = perguntas[pagina_atual]
        num_quest = questao[0]

        pagina_anterior = f"{questao[0]}_{name}"
        proxima_pagina = questao[8]

        try:
            session[f"resposta_{num_quest}"] = request.form[f"resposta_{num_quest}"]
        except KeyError:
            session[f"resposta_{num_quest}"] = ""


        if proxima_pagina == "result":
            return redirect("/quiz/quiz_resultado")
        
        return redirect (f"/quiz/{proxima_pagina}")
    
    return render_template(f"/quiz/{page}.html", questao = questao, num_quest=num_quest, proxima = proxima_pagina, anterior = pagina_anterior, pagina_atual=pagina_atual, paginas=arquivos.apostila_paginas, perguntas=perguntas)


#função para salvar as respostas do usuário
def salvar_respostas(num_quest, proxima_pagina):
    try:
        session[f"resposta{num_quest}"] = request.form[f"resposta{num_quest}"]
    except KeyError:
        session[f"resposta{num_quest}"] = ""
        
    return render_template (f"/quiz/{proxima_pagina}.html")


@app.route("/quiz/quiz_resultado_parcial/<numero_pagina>")
def quiz_resultado_parcial(numero_pagina):
    return functions.quiz_resultado_parcial(numero_pagina)


#rota para verificação dos resultados do quiz e visualização da página de resultados
@app.route("/quiz/quiz_resultado")
def resultado():
    perguntas = arquivos.quiz_perguntas
    acertos = 0
    questoes_erradas = {}
    correcao = arquivos.erro_assunto
    respostas = dict(map(lambda key: (key.replace("_", " ").title(), session[key]), filter(lambda key: key.startswith("resposta"), session)))
    print(respostas)

    for i in perguntas:
        if i == "result": break
        try:
            if perguntas[i][6] == session[f"resposta_{perguntas[i][0]}"]:
                acertos += 1
            else: questoes_erradas[perguntas[i][0]] = correcao[f"erro_{perguntas[i][0]}"]

        except KeyError:
            respostas[f"resposta_{perguntas[i][0]}"] = ""
            questoes_erradas[perguntas[i][0]] = correcao[f"erro_{perguntas[i][0]}"]

    erros = len(perguntas)-1 - acertos
    porcentagem = f"{(acertos/(len(perguntas)-1) * 100):.2f}%"

    return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas, questoes_erradas = questoes_erradas, correcao = correcao, perguntas=perguntas)


# rota para avaliação e resultado da avaliação
@app.route("/avaliacao", methods=["POST", "GET"])
def avaliacao():
    apostila_paginas = arquivos.apostila_paginas
    perguntas = arquivos.quiz_perguntas
    correcao = arquivos.erro_assunto
    questoes_erradas = {}

    if request.method == "POST":
        respostas_prova = {}
        acertos = 0

        for key, value in perguntas.items():
            if key == "result": break
            respostas_prova[key] = request.form.get(f"resposta{key}")
            
        
        for key,value in respostas_prova.items():
            if value == perguntas[key][6]:
                acertos += 1
            else: questoes_erradas[perguntas[key][0]] = correcao[f"erro_{perguntas[key][0]}"]
        
        erros = len(perguntas) - 1 - acertos
        porcentagem = f"{(acertos/(len(perguntas)-1) * 100):.2f}%"

        return render_template("/avaliacao/resultado_avaliacao.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas_prova, questoes_erradas = questoes_erradas, correcao = correcao, paginas = apostila_paginas, perguntas = perguntas)

    return render_template("/avaliacao/avaliacao.html", perguntas = perguntas, paginas = apostila_paginas)


#rota para o PACER
@app.route("/pacer", methods = ["POST", "GET"])
def pacer_page():
    qtd_funcionarios = 0

    if request.method == "POST":
        qtd_funcionarios = int(request.form.get("qtd_funcionarios"))
        return redirect (f"pacer/{qtd_funcionarios}")

    return render_template("/pacer/pacer.html", qtd_funcionarios=qtd_funcionarios)


#recarrega a pagina com um questionario para cada membro da equipe
@app.route("/pacer/<name>", methods=["POST", "GET"])
def get_pacer(name):
    return render_template ("/pacer/pacer.html", qtd_funcionarios = int(name))


#retorno do PACER para o usuário
@app.route("/pacer/ver/<name>", methods=["POST", "GET"])
def pacer_res(name):

    pacer_funcionarios = {}
    soma_pacer = 0

    for i in range(int(name)):
        nome_funcionario = request.form.get(f"nome_funcionario{i}")
        productivity = int(request.form.get(f"productivity{i}"))
        autonomy = int(request.form.get(f"autonomy{i}"))
        collaboration = int(request.form.get(f"collaboration{i}"))
        results = int(request.form.get(f"results{i}"))

        calculo_final = productivity + autonomy + collaboration + results
        pacer_funcionarios[nome_funcionario] = [productivity, autonomy, collaboration, results, calculo_final]

    for i in pacer_funcionarios:
            soma_pacer += pacer_funcionarios[i][4]

    return render_template("/pacer/pacer_res.html", pacer = pacer_funcionarios, soma = soma_pacer)


if __name__ == "__main__":
    app.run(debug=True)