import json

apostila_paginas = json.load(open("./static/apostila_paginas.json", encoding='utf-8'))
quiz_perguntas = json.load(open("./static/quiz_perguntas.json", encoding='utf-8'))
perguntas_prova = json.load(open("./static/perguntas_prova.json", encoding='utf-8'))
erros_prova = json.load(open("./static/erros_prova.json", encoding='utf-8'))
erro_assunto = json.load(open("./static/erro_assunto.json", encoding='utf-8'))