from flask import Flask, render_template, redirect, request, session, send_file
from flask_login import LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import date
import arquivos
import database
import quiz_functions, login_functions
import certificate_functions

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

app.secret_key = "chave_secreta"

database.initialize_database() #Inicia o banco de dados

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor, faça login para acessar essa página!"

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


@app.route("/home")
@app.route("/", methods=["POST", "GET"])
def home():
    is_admin = False
    continuar = "iniciar"

    try:
        user_logged_in = current_user.is_authenticated
        try:
            user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email
        except TypeError:
            logout_user()
            session.clear()
            return redirect("/")
        continuar = quiz_functions.continue_quiz(current_user.id)

        if login_functions.is_admin(current_user.id):
            is_admin = True
    except AttributeError:
        user_logged_in = False
        user_data = []

    return render_template ("index.html", user_logged_in = user_logged_in, is_admin=is_admin, user_data=user_data, continuar = continuar)


@app.route("/<name>")
def get_page(name):
    if name == "apostila":
        return redirect("/apostila/introducao")
    if name == "quiz":
        return redirect ("quiz/iniciar")
    if name == "ferramentas":
        return redirect("/ferramentas/ferramentas")
    if name == "avaliacao" or name=="avaliação":
        return redirect("/avaliacao")
    return render_template(f"{name}.html")


@app.route("/ferramentas/<name>")
def ferramentas(name):
    try:
        is_admin = login_functions.is_admin(login_functions.current_user.id)
    except AttributeError:
        is_admin = False
    
    if login_functions.verify_login():
        continuar = quiz_functions.continue_quiz(current_user.id)
        user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email
    else:
        continuar = "iniciar"
        user_data = []
    
    return render_template(f"/ferramentas/{name}.html", is_admin = is_admin, continuar=continuar, user_data = user_data)


@app.route("/apostila/<name>")
def find_apostila(name):
    try:
        is_admin = login_functions.is_admin(login_functions.current_user.id)
    except AttributeError:
        is_admin = False
    
    if login_functions.verify_login():
        continuar = quiz_functions.continue_quiz(current_user.id)
        user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email
    else:
        continuar = "iniciar"
        user_data = []

    return render_template(f"/apostila/{name}.html", paginas = arquivos.apostila_paginas, is_admin=is_admin, continuar = continuar, user_data=user_data)


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

@app.route("/quiz/salvar_quiz/<numero_pagina>")
@login_required
def save_quiz_answers(numero_pagina):
    return quiz_functions.save_quiz(numero_pagina)


@app.route("/quiz/resultado_parcial")
@login_required
def partial_result():
    return quiz_functions.resultado_parcial(current_user.id)


@app.route("/quiz/quiz_resultado")
@login_required
def quiz_resultado():
    return quiz_functions.quiz_resultado_final()


# route to the test; user must be logged in to access
@app.route("/avaliacao", methods=["POST", "GET"])
@login_required
def avaliacao():
    apostila_paginas = arquivos.apostila_paginas
    perguntas = arquivos.perguntas_prova
    correcao = arquivos.erros_prova
    questoes_erradas = {}

    is_admin = login_functions.is_admin(login_functions.current_user.id)
    user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email

    if login_functions.verify_login():
        continuar = quiz_functions.continue_quiz(current_user.id)

    if request.method == "POST":
        respostas_prova = {}
        acertos = 0

        for key, value in perguntas.items():
            if key == "result": break
            respostas_prova[key] = request.form.get(f"resposta{key}")
        
        for key,value in respostas_prova.items():
            if value == perguntas[key][5]:
                acertos += 1
            else: questoes_erradas[perguntas[key][0]] = correcao[f"erro_{perguntas[key][0]}"]
        
        erros = len(perguntas) - acertos
        porcentagem = f"{(acertos/(len(perguntas)) * 100):.2f}%"

        username = login_functions.current_user.id
        print(username, acertos)
        database.insert_grade(username, acertos)

        return render_template("/avaliacao/resultado_avaliacao.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas_prova, questoes_erradas = questoes_erradas, correcao = correcao, paginas = apostila_paginas, perguntas = perguntas, continuar = continuar, is_admin=is_admin, user_data=user_data)

    return render_template("/avaliacao/avaliacao.html", perguntas = perguntas, paginas = apostila_paginas, continuar = continuar, is_admin=is_admin, user_data=user_data)


#rota para o PACER
@app.route("/pacer", methods = ["POST", "GET"])
def pacer_page():
    try:
        is_admin = login_functions.is_admin(login_functions.current_user.id)
    except AttributeError:
        is_admin = False
    
    if login_functions.verify_login():
        continuar = quiz_functions.continue_quiz(current_user.id)
        user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email
    else:
        continuar = "iniciar"
        user_data = []

    qtd_funcionarios = 0

    if request.method == "POST":
        qtd_funcionarios = int(request.form.get("qtd_funcionarios"))
        return redirect (f"pacer/{qtd_funcionarios}")

    return render_template("/pacer/pacer.html", qtd_funcionarios=qtd_funcionarios, is_admin=is_admin, continuar = continuar, user_data=user_data)

#recarrega a pagina com um questionario para cada membro da equipe
@app.route("/pacer/<name>", methods=["POST", "GET"])
def get_pacer(name):
    try:
        is_admin = login_functions.is_admin(login_functions.current_user.id)
    except AttributeError:
        is_admin = False
    if login_functions.verify_login():
        continuar = quiz_functions.continue_quiz(current_user.id)
        user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email
    else:
        continuar = "iniciar"
        user_data = []
    return render_template ("/pacer/pacer.html", qtd_funcionarios = int(name), is_admin=is_admin, continuar = continuar, user_data=user_data)


#retorno do PACER para o usuário
@app.route("/pacer/ver/<name>", methods=["POST", "GET"])
def pacer_res(name):
    try:
        is_admin = login_functions.is_admin(login_functions.current_user.id)
    except AttributeError:
        is_admin = False
        
    if login_functions.verify_login():
        continuar = quiz_functions.continue_quiz(current_user.id)
        user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email
    else:
        continuar = "iniciar"
        user_data=[]

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

    return render_template("/pacer/pacer_res.html", pacer = pacer_funcionarios, soma = soma_pacer, is_admin=is_admin, continuar = continuar, user_data=user_data)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return login_functions.user_signup()


@app.route("/update_user_info", methods=["POST", "GET"])
@login_required
def update():
    return login_functions.update_user_info()


@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_functions.user_login()


@app.route('/logout', methods=["POST", "GET"])
# @login_required
def logout():
    logout_user()
    session.clear()
    return redirect("/")


@app.route("/user")
@login_required
def user_page():
    return login_functions.user_page(current_user.id)


@app.route("/admin")
@login_required
def admin():
    return login_functions.admin_page()


@app.route('/feedback', methods=["POST", "GET"])
@login_required
def feedback():
    if login_functions.verify_login():
        continuar = quiz_functions.continue_quiz(current_user.id)
        user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email
    else:
        continuar = "iniciar"
        user_data=[]
    if request.method == "POST":
        feedback = request.form.get('star')
        comment = request.form.get('suggestion')
        database.insert_feedback(current_user.id, feedback, comment)
        return redirect("/user")
    return render_template ("/feedback/feedback.html", continuar=continuar, user_data=user_data)

#Rota para gerar o certificado

@app.route('/certificado')
@login_required
def gerar_pdf():
    
    certificate_functions.create_certificate(database.retrieve_data('registro', 'nome', current_user.id))
    
    return send_file('certificado.pdf', mimetype='application/pdf',)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)