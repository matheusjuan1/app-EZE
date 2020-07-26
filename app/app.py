import os

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import json

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


# _________________________________ Rotas Organizador _________________________________________________


@app.route("/login_organizador", methods=["GET", "POST"])
def login_organizador():
    if request.method == "POST":
        db = sqlite3.connect("eze.db")
        db.row_factory = sqlite3.Row
        eze = db.cursor()
        email = request.form.get("email")
        eze.execute("SELECT * FROM organizador WHERE email = ?", [email])
        rows = eze.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0]["senha"], request.form.get("senha")):
            flash("E-mail e/ou senha inválidos!")
            return redirect("/login_organizador")
        usuarioAT.append(request.form.get("email"))

        session["user_id"] = rows[0]["id"]

        return redirect("/organizador")

    else:
        return render_template("loginorg.html")


@app.route("/organizador", methods=["GET", "POST"])
@login_required
def organizador():
    if request.method == "GET":
        db = sqlite3.connect("eze.db")
        db.row_factory = sqlite3.Row
        eze = db.cursor()
        eze.execute("SELECT * FROM organizador WHERE id = ?",
                    [session["user_id"]])
        organizador = eze.fetchall()
        eze.execute("SELECT * FROM lista where lote = 1")
        lista1 = eze.fetchall()
        eze.execute("SELECT * FROM lista where lote = 2")
        lista2 = eze.fetchall()
        eze.execute("SELECT * FROM lista where lote = 3")
        lista3 = eze.fetchall()
        eze.execute("SELECT Count(idLista) as count FROM lista")
        contagem = eze.fetchall()
        tamanho2 = len(lista2)
        tamanho3 = len(lista3)
        return render_template("organizador.html", lista1=lista1, lista2=lista2, tamanho2=tamanho2, tamanho3=tamanho3, lista3=lista3, organizador=organizador, contagem=contagem)
    else:
        if 'editar' in request.form:
            nome = request.form["nome"]
            sexo = request.form["sexo"]
            idcli = request.form["editar"]
            db = sqlite3.connect("eze.db")
            db.row_factory = sqlite3.Row
            eze = db.cursor()
            eze.execute(
                f"UPDATE lista SET nomeCliente = '{nome}', sexo = '{sexo}' WHERE idLista = '{idcli}'")
            db.commit()
            eze.close()
            flash("Nome alterado com sucesso!")
            return redirect("/organizador")
        elif 'excluir' in request.form:
            idcli = request.form["excluir"]
            db = sqlite3.connect("eze.db")
            db.row_factory = sqlite3.Row
            eze = db.cursor()
            eze.execute(f"DELETE FROM lista WHERE idLista = '{idcli}'")
            db.commit()
            eze.close()
            flash("Excluido com sucesso!")
            return redirect("/organizador")
        elif 'adicionar' in request.form:
            nome = request.form["nome"]
            sexo = request.form["sexo"]
            lote = request.form["lote"]
            data = request.form["data"]

            with sqlite3.connect("eze.db") as db:
                eze = db.cursor()
                eze.execute(
                    f"INSERT INTO lista (nomeCliente, sexo, Lote, dataCompra, fk_promoter) VALUES (?,?,?,?, '1')", (nome, sexo, lote, data))
                db.commit()
                return redirect("/organizador")

        else:
            return redirect("/organizador")


@app.route("/organizador/promoters", methods=["GET", "POST"])
@login_required
def orgpromoters():
    if request.method == "GET":
        db = sqlite3.connect("eze.db")
        db.row_factory = sqlite3.Row
        eze = db.cursor()
        eze.execute("SELECT * FROM organizador WHERE id = ?",
                    [session["user_id"]])
        organizador = eze.fetchall()
        eze.execute(
            "SELECT promoters.*, count(fk_promoter) as count FROM promoters LEFT JOIN lista ON lista.fk_promoter = id GROUP BY id ORDER BY nome")
        promoters = eze.fetchall()
        return render_template("orgpromoters.html", organizador=organizador, promoters=promoters)
    else:
        if 'adicionar' in request.form:
            nome = request.form["nome"]
            email = request.form["email"]
            senha = '12345'
            hashS = generate_password_hash(senha)
            with sqlite3.connect("eze.db") as db:
                eze = db.cursor()
                eze.execute(
                    "INSERT INTO promoters (nome, senha, email) VALUES (?,?,?)", (nome, hashS, email))
                db.commit()
            flash("Promoter adicionado com sucesso")
            return redirect("/organizador/promoters")
        elif 'excluir' in request.form:
            idp = request.form["excluir"]
            db = sqlite3.connect("eze.db")
            db.row_factory = sqlite3.Row
            eze = db.cursor()
            eze.execute("SELECT * FROM lista WHERE fk_promoter = ?", (idp))
            nomes = eze.fetchall()
            if len(nomes) != 0:
                eze = db.cursor()
                eze.execute(
                    f"UPDATE lista SET fk_promoter ='1' WHERE fk_promoter = '{idp}'")
                db.commit()
            eze.execute(f"DELETE FROM promoters WHERE id = '{idp}'")
            db.commit()
            eze.close()
            flash("Promoter excluído com sucesso")
            return redirect("/organizador/promoters")
        return redirect("/organizador/promoters")


@app.route("/organizador/geral", methods=["GET", "POST"])
@login_required
def geral():
    return render_template("geral.html")

    # _________________________________ Rotas Promoters _________________________________________________


@app.route("/login_promoter", methods=["GET", "POST"])
def login_promoter():
    if request.method == "POST":
        db = sqlite3.connect("eze.db")
        db.row_factory = sqlite3.Row
        eze = db.cursor()
        email = request.form.get("email")
        eze.execute("SELECT * FROM promoters WHERE email = ?", [email])
        rows = eze.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0]["senha"], request.form.get("senha")):
            flash("E-mail e/ou Senha inválidos!")
            return redirect("/login_promoter")
        usuarioAT.append(request.form.get("email"))

        session["user_id"] = rows[0]["id"]

        return redirect("/promoter")

    else:
        return render_template("loginprom.html")


@app.route("/promoter", methods=["GET", "POST"])
@login_required
def promoter():
    if request.method == "GET":
        db = sqlite3.connect("eze.db")
        db.row_factory = sqlite3.Row
        eze = db.cursor()
        eze.execute("SELECT * FROM promoters WHERE id = ?",
                    [session["user_id"]])
        linhas2 = eze.fetchall()
        eze.execute(
            "SELECT * FROM lista WHERE fk_promoter = ? ORDER BY idLista DESC", [session["user_id"]])
        linhas = eze.fetchall()
        total = len(linhas)
        return render_template("promoter.html", banco=linhas, promoter=linhas2, total=total)
    else:
        nome = request.form["nome"]
        sexo = request.form["sexo"]
        select = request.form["SC"]
        idPro = session["user_id"]
        image = request.form["img"]
        print(image)

        db = sqlite3.connect("eze.db")
        db.row_factory = sqlite3.Row
        eze = db.cursor()

        eze.execute(
            f"UPDATE lista SET nomeCliente = '{nome}', sexo = '{sexo}' WHERE idLista = '{select}'")
        linhas = eze.fetchall()
        db.commit()
        eze.close()
        return redirect("/promoter")


@app.route("/add_cliente", methods=["POST"])
@login_required
def add_cliente():
    nome = request.form["nome"]
    sexo = request.form["sexo"]
    lote = request.form["lote"]
    data = request.form["data"]
    idPro = session["user_id"]

    with sqlite3.connect("eze.db") as db:
        eze = db.cursor()
        eze.execute(
            f"INSERT INTO lista (nomeCliente, sexo, Lote, dataCompra, fk_promoter) VALUES (?,?,?,?, '{idPro}')", (nome, sexo, lote, data))
        db.commit()
        return redirect("/promoter")


@app.route("/perfil_promoter", methods=["GET"])
@login_required
def perfil_cliente():
    db = sqlite3.connect("eze.db")
    db.row_factory = sqlite3.Row
    eze = db.cursor()
    eze.execute("SELECT * FROM promoters WHERE id = ?",
                [session["user_id"]])
    linhas2 = eze.fetchall()
    eze.execute(
        "SELECT * FROM lista WHERE fk_promoter = ? ORDER BY idLista DESC", [session["user_id"]])
    linhas = eze.fetchall()
    total = len(linhas)
    eze.execute(
        "SELECT * FROM lista WHERE fk_promoter = ? AND sexo = 'M'", [session["user_id"]])
    masculino = eze.fetchall()
    masc = len(masculino)
    eze.execute(
        "SELECT * FROM lista WHERE fk_promoter = ? AND sexo = 'F'", [session["user_id"]])
    femi = eze.fetchall()
    fem = len(femi)

    eze.execute("SELECT dataCompra , COUNT(dataCompra) FROM lista WHERE fk_promoter = ? GROUP BY dataCompra", [
                session["user_id"]])
    datas = eze.fetchall()
    total_datas = len(datas)
    valores_datas = []
    ingressos = []
    for i in datas:
        valores_datas.append(i["dataCompra"])
        ingressos.append(i["COUNT(dataCompra)"])

    return render_template("perfilP.html", user=linhas2, quant=total, vendas=linhas, masc=masc, fem=fem, data=valores_datas, total_datas=total_datas, ingressos=ingressos)


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
#             insert = eze.execute("INSERT INTO organizador (nomeOrganizador, senha, urlIMG, email) VALUES (?,?,?,?)", (nome1, hashS, perfilP, email))
#             db.commit()
#             return render_template("registrar.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
