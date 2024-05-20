from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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


