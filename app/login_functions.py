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
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Senhas não batem!", "Error")
            return redirect("/signup")
        
        if database.signup(cpf, nome, password):
            flash("registro realizado com sucesso!", "Success")
            return redirect("/login")
        else:
            flash("usuário já está cadastrado", "Error")
            return render_template("signup.html")
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
                flash("Você está logado!", "Success")
                return render_template("index.html", login_success = True)
        else:
            flash("Usuário não está cadastrado ou a senha está errada", "Error")
            return redirect ("/login")
    return render_template('login.html')