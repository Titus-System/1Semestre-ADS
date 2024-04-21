import json

apostila_paginas = json.load(open("./static/apostila_paginas.json", encoding='utf-8'))

quiz_capitulo1 = json.load(open("./static/quiz_capitulo1.json", encoding='utf-8'))

quiz_capitulo2 = json.load(open("./static/quiz_capitulo2.json", encoding='utf-8'))

quiz_capitulo3 = json.load(open("./static/quiz_capitulo3.json", encoding='utf-8'))

rotas_quiz = ["quiz_capitulo1", "quiz_capitulo2", "quiz_capitulo3"]

todosquiz = [quiz_capitulo1, quiz_capitulo2, quiz_capitulo3]

resumos = ""