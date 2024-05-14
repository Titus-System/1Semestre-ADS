from flask import Flask, render_template, redirect, request, session
import json
import arquivos
import database


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

    # cpf = session[cpf]
    nota_quiz = acertos
    posicao = numero_pagina
    # database.save_quiz_state(cpf: str, nota_quiz: int, posicao: int)

    return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas, questoes_erradas = questoes_erradas, correcao = correcao, perguntas=perguntas)