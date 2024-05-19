from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import arquivos
import database
import quiz_functions, login_functions


app = Flask(__name__)

app.secret_key = "chave_secreta"

database.initialize_database() #Inicia o banco de dados

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Classe de Usuário
class User(UserMixin):
    def __init__(self, username):
        self.id = username

    def get_id(self):
        return self.id


# Carrega o usuário
# Função para carregar usuário
@login_manager.user_loader
def load_user(username):
    user = User(username)
    user.id = username
    return user


@app.route("/", methods=["POST", "GET"])
def home():
    try:
        user_logged_in = current_user.is_authenticated
        print(user_logged_in)
    except AttributeError:
        user_logged_in = False

    try:
        posicao = quiz_functions.continue_quiz()
    except AttributeError: posicao = "iniciar"

    if login_functions.is_admin(current_user.id):
        is_admin = True
    else: is_Admin = False

    return render_template ("index.html", user_logged_in = user_logged_in, is_admin=is_admin, continuar = posicao)


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
    return render_template(f"/apostila/{name}.html", paginas = arquivos.apostila_paginas)


@app.route("/quiz/")
@login_required
def iniciar():
    return redirect("/quiz/iniciar")

#routes to find the quiz pages (concepts and questions)
#user must be logged in to access
@app.route("/quiz/<name>", methods=["POST", "GET"])
@login_required
def quiz_page(name=str):
    if name == "final":
        return redirect("/quiz/quiz_resultado")
    return quiz_functions.quiz_page(name)


@app.route("/quiz/quiz_resultado_parcial/<numero_pagina>")
def quiz_resultado_parcial(numero_pagina):
    return quiz_functions.quiz_resultado_parcial(numero_pagina)


@app.route("/quiz/quiz_resultado")
def quiz_resultado():
    return quiz_functions.quiz_resultado_final()


# route to the test; user must be logged in to access
@app.route("/avaliacao", methods=["POST", "GET"])
@login_required
def avaliacao():
    apostila_paginas = arquivos.apostila_paginas
    perguntas = arquivos.quiz_perguntas
    correcao = arquivos.erro_assunto
    questoes_erradas = {}

    if login_functions.verify_login():
        continuar = quiz_functions.continue_quiz()

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

        username = login_functions.current_user.id
        print(username, acertos)
        database.insert_grade(username, acertos)

        return render_template("/avaliacao/resultado_avaliacao.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas_prova, questoes_erradas = questoes_erradas, correcao = correcao, paginas = apostila_paginas, perguntas = perguntas, continunar = continuar)

    return render_template("/avaliacao/avaliacao.html", perguntas = perguntas, paginas = apostila_paginas, continuar = continuar)


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


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return login_functions.user_signup()



@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_functions.user_login()


@app.route('/logout', methods=["POST", "GET"])
# @login_required
def logout():
    logout_user()
    session.clear()
    return redirect("/")


@app.route("/admin")
@login_required
def admin():
    if login_functions.is_admin(login_functions.current_user.id):
        return render_template("admin.html", is_admin=True)
    flash("É necessário ser administrador para acessar essa página!")
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)