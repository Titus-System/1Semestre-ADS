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

    is_admin = login_functions.is_admin(login_functions.current_user.id)

    if continue_quiz() == None:
        print("sem quiz")
        posicao = "iniciar"
    else:
        posicao = continue_quiz()

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
    
    return render_template(f"/quiz/{page}.html", questao = questao, num_quest=num_quest, proxima = proxima_pagina, anterior = pagina_anterior, pagina_atual=pagina_atual, paginas=arquivos.apostila_paginas, perguntas=perguntas, continuar=posicao, is_admin =is_admin)


#função para salvar as respostas do usuário
def salvar_respostas(num_quest, proxima_pagina):
    is_admin = login_functions.is_admin(login_functions.current_user.id)
    try:
        session[f"resposta{num_quest}"] = request.form[f"resposta{num_quest}"]
    except KeyError:
        session[f"resposta{num_quest}"] = ""
        
    return render_template (f"/quiz/{proxima_pagina}.html", is_admin=is_admin)


def quiz_resultado_parcial(numero_pagina):
    perguntas = arquivos.quiz_perguntas
    acertos = 0
    questoes_erradas = {}
    correcao = arquivos.erro_assunto
    respostas = {}
    is_admin = login_functions.is_admin(login_functions.current_user.id)

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

    username = login_functions.current_user.id
    database.save_quiz_state(username, acertos, numero_pagina)
    database.save_quiz_answers(respostas, username)
    print(username)
    return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas, questoes_erradas = questoes_erradas, correcao = correcao, perguntas=perguntas, is_admin=is_admin)


def quiz_resultado_final():
    perguntas = arquivos.quiz_perguntas
    acertos = 0
    questoes_erradas = {}
    correcao = arquivos.erro_assunto
    
    username = login_functions.current_user.id
    is_admin = login_functions.is_admin(username)
    
    respostas_anteriores = database.retrieve_quiz_answers(username)
    respostas_sessao = dict(map(lambda key: (key, session[key]), filter(lambda key: key.startswith("resposta"), session)))
    
    if respostas_anteriores != None:
        respostas_anteriores.update(respostas_sessao)
        respostas = respostas_anteriores
    else:
        respostas = respostas_sessao

    database.save_quiz_answers(respostas, username)
    print(respostas)

    for i in perguntas:
        if i == "result": break
        try:
            if perguntas[i][6] == respostas[f"resposta_{perguntas[i][0]}"]:
                acertos += 1
            else: questoes_erradas[perguntas[i][0]] = correcao[f"erro_{perguntas[i][0]}"]

        except KeyError:
            respostas[f"resposta_{perguntas[i][0]}"] = ""
            questoes_erradas[perguntas[i][0]] = correcao[f"erro_{perguntas[i][0]}"]

    erros = len(perguntas)-1 - acertos
    porcentagem = f"{(acertos/(len(perguntas)-1) * 100):.2f}%"
    database.save_quiz_state(username, acertos, "final")

    return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas, questoes_erradas = questoes_erradas, correcao = correcao, perguntas=perguntas, is_admin=is_admin)


def continue_quiz():
    cpf = login_functions.current_user.id
    posicao = database.retrieve_data("academico", "posicao", cpf)
    print(posicao)
    return posicao