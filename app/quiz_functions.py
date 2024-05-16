from flask import Flask, render_template, redirect, request, session
import json
import arquivos
import database
import login_functions

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


def quiz_resultado_parcial(numero_pagina):
    perguntas = arquivos.quiz_perguntas
    acertos = 0
    questoes_erradas = {}
    correcao = arquivos.erro_assunto
    respostas = {}

    respostas = dict(map(lambda key: (key, session[key]), filter(lambda key: key.startswith("resposta"), session)))
    print(session)
    print(respostas)
    
    for key in perguntas:
        if key == "result": break
        try:
            if perguntas[key][6] == session[f"resposta_{perguntas[key][0]}"]:
                acertos += 1
            else:
                questoes_erradas[perguntas[key][0]] = correcao[f"erro_{perguntas[key][0]}"]
        except KeyError: pass

    erros = len(respostas) - acertos
    porcentagem = f"{(acertos/(len(perguntas)-1) * 100):.2f}%"

    cpf = login_functions.current_user.id
    database.save_quiz_state(cpf, acertos, numero_pagina)
    print(cpf)
    return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas, questoes_erradas = questoes_erradas, correcao = correcao, perguntas=perguntas)


def quiz_resultado_final():
    perguntas = arquivos.quiz_perguntas
    acertos = 0
    questoes_erradas = {}
    correcao = arquivos.erro_assunto
    respostas = dict(map(lambda key: (key, session[key]), filter(lambda key: key.startswith("resposta"), session)))
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