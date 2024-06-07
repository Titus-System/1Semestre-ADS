from flask import render_template, redirect, url_for, request, flash
from flask_login import UserMixin, login_user, current_user
import database
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
import numpy

# Classe de Usuário
class User(UserMixin):
    def __init__(self, username):
        self.id = username

    def get_id(self):
        return self.id


def user_signup():
    if request.method == 'POST':
        username = request.form['username']
        nome = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Senhas não batem!", "Error")
            return redirect("/login")
        
        if username == "egydio":
            is_admin = True
        else: is_admin = False

        if database.signup(username, nome, password, email, is_admin):
            flash("registro realizado com sucesso! Faça login para continuar...", "Success")
            return redirect("/login")
        else:
            flash("usuário já está cadastrado", "Error")
            return redirect("/login")
    return redirect("/")


def user_login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        if database.login(username, password): #verifica se o usuário existe no banco de dados
            user = User(username, )
            user.id = username
            login_user(user)
            if request.args.get('next'):
                return redirect (request.args.get('next'))
            else:
                flash("Você está logado!", "Success")
                return redirect("/")
        else:
            flash("Usuário não está cadastrado ou a senha está errada", "Error")
            return redirect ("/login")
    return render_template("login.html")


def verify_login():
    return current_user.is_authenticated


def is_admin(username):
    return database.retrieve_data("registro", "is_admin", username) == 1


def graph(eixo_x, eixo_y):
    # Criação dos eixos
    x = numpy.array(eixo_x)
    y = numpy.array(eixo_y)

    # Criação do gráfico
    fig, ax = plt.subplots()
    ax.bar(x, y)

    # Salvar o gráfico em um buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Fechar a figura para liberar a memória
    plt.close(fig)

    # Retorna a imagem codificada
    return image_base64


def admin_page():

    def media(column):
        soma = 0
        qtd = 0
        if len(column) < 1:
            return "Ainda não há registros"
        
        for i in column:
            if type(i) == int:
                soma += i
                qtd += 1
        return format(soma/qtd, ",.2f")

    if is_admin(current_user.id):
        try:
            user_data = database.retrieve_data("registro", ['nome', 'mail'], current_user.id)['nome'] #tupla com nome e email
            continuar = database.retrieve_data("academico", "posicao", current_user.id)
        except TypeError:
            user_data = []
            continuar = "iniciar"
        notas_prova = database.retrieve_column("academico", "nota_prova")
        notas_quiz = database.retrieve_column("academico", "nota_quiz")
        feedbacks = database.retrieve_column("opiniao", "feedback")

        media_prova = media(notas_prova)
        media_quiz = media(notas_quiz)
        media_feedback = media(feedbacks)

        feedback_distribution = []
        for i in range(1, 6):
            feedback_distribution.append(feedbacks.count(i))

        graphic = graph([1, 2, 3, 4, 5], feedback_distribution)

        users_results = database.get_user_info()

        return render_template("admin.html", is_admin=True,media_feedback=media_feedback, media_prova=media_prova, media_quiz=media_quiz, graph = graphic, user_data=user_data, users_results=users_results, continuar=continuar)
    
    flash("É necessário ser administrador para acessar essa página!")
    return redirect("/login")


def update_user_info():
    username = current_user.id
    update_nome = request.form.get("update_nome")
    update_mail = request.form.get("update_mail")
    update_password = request.form.get("update_password")
    update_password_confirm = request.form.get("update_password_confirm")

    if update_password != update_password_confirm:
        flash("senhas não batem!")
        return redirect("/login")
    
    for column, value in [("nome", update_nome), ('mail',update_mail), ('password', database.hashpw(update_password.encode("utf-8"), database.gensalt()))]:
        if value:
            database.update_user_info("registro", column, username, value)

    return redirect("/")


def user_page(username):
    personal_user_info = database.retrieve_data("registro", ['nome', 'mail'], username)['nome'] #tupla com nome e email
    admin = is_admin(username)
    try:
        academic_info = database.retrieve_data("academico", ["nota_quiz", "nota_prova", "posicao"], username)['nota_quiz']#retorna uma tupla (nota_quiz, nota_prova, posicao)
        continuar = academic_info[2]
    except TypeError:
        academic_info = database.retrieve_data("academico", ["nota_quiz", "nota_prova", "posicao"], username)
        continuar = "iniciar"
    user_feedback = database.retrieve_data("opiniao", "feedback", username)
    if user_feedback == None or user_feedback =="": user_feedback = "*" 
    return render_template("user.html", user_data = personal_user_info, is_admin = admin, academic_info = academic_info, continuar = continuar, user_feedback=user_feedback)