from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import database

# Classe de Usuário
class User(UserMixin):
    def __init__(self, cpf):
        self.id = cpf

    def get_id(self):
        return self.id


def user_signup():
    if request.method == 'POST':
        cpf = request.form['cpf']
        nome = request.form['nome']
        password = request.form['password']
        if database.signup(cpf, nome, password):
            return "usuario criado com sucesso"
        else:
            return "usuario já existe"
    return render_template('signup.html')


def user_login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        password = request.form['password']
        if database.login(cpf, password):
            user = User(cpf, )
            user.id = cpf
            login_user(user)
            if request.args.get('next'):
                return redirect (request.args.get('next'))
            else:
                return redirect("/")
        else:
            return "não encontrado"
    return render_template('login.html')