import os

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


usuarioAT = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/edicoes")
def edicoes():
    return render_template("edicoes.html")

@app.route("/comprar")
def comprar():
    return render_template("comprar.html")    

@app.route("/organizador", methods=["GET", "POST"])
def login_organizador():
    if request.method == "POST":
        db = sqlite3.connect("eze.db")
        db.row_factory = sqlite3.Row
        eze = db.cursor()
        eze.execute("SELECT * FROM organizador WHERE email = :email",
                          email=request.form.get("email"))
        rows = eze.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0]["senha"], request.form.get("senha")):
            return apology("invalid email and/or password", 403)
        usuarioAT.append(request.form.get("email"))

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("loginorg.html") 


@app.route("/promoter")
def login_prom():
    return render_template("loginprom.html")     


# @app.route("/registerOrg", methods=["GET", "POST"])
# def registrar():
#     if request.method == "GET":
#         return render_template("registrar.html")
#     else:
#         nome1 = request.form["nomeP"]
#         senha = request.form["senhaP"]
#         email = request.form["emailP"]
#         perfilP = request.form["urlP"]
#         hashS = generate_password_hash(senha)
#         with sqlite3.connect("eze.db") as db:
#             eze = db.cursor()
#             insert = eze.execute("INSERT INTO organizador (nome, senha, urlIMG, email) VALUES (?,?,?,?)", (nome1, hashS, perfilP, email))
#             db.commit()
#             return render_template("registrar.html")
#             db.close()


# @app.route("/register", methods=["GET", "POST"])
# def registrar():
#     if request.method == "GET":
#         return render_template("registrar.html")
#     else:
#         nome1 = request.form["nomeP"]
#         senha = request.form["senhaP"]
#         email = request.form["emailP"]
#         perfilP = request.form["urlP"]
#         hashS = generate_password_hash(senha)
#         with sqlite3.connect("eze.db") as db:
#             eze = db.cursor()
#             insert = eze.execute("INSERT INTO promoters (nomePromoter, senha, urlIMG, emailPromoter) VALUES (?,?,?,?)", (nome1, hashS, perfilP, email))
#             db.commit()
#             return render_template("registrar.html")
#             db.close()
# 

@app.route("/promoterLogado", methods=["GET", "POST"])
def promoterLogado():
    if request.method == "GET":
        db = sqlite3.connect("eze.db")
        db.row_factory = sqlite3.Row
        eze = db.cursor()
        eze.execute("SELECT * FROM promoters WHERE nomePromoter = 'Vitória Gama'")
        linhas = eze.fetchall()
        return render_template("promoter.html", banco = linhas)


# @app.route("/login", methods=["GET", "POST"])
# def login():

#     # Forget any user_id
#     session.clear()

#     # User reached route via POST (as by submitting a form via POST)
#     if request.method == "POST":
#         # Query database for username
#         rows = db.execute("SELECT * FROM organizador WHERE username = :username",
#                           username=request.form.get("username"))

#         # Ensure username exists and password is correct
#         if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
#             return apology("invalid username and/or password", 403)
#         usuarioAT.append(request.form.get("username"))

#         # Remember which user has logged in
#         session["user_id"] = rows[0]["id"]

#         # Redirect user to home page
#         return redirect("/")

#     # User reached route via GET (as by clicking a link or via redirect)
#     else:
#         return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    app.run(debug=True,port=8080)