from flask import Flask, render_template, request, redirect
from flask import Flask, render_template, request, redirect, flash

import sqlite3
from datetime import datetime, timedelta
import csv

app = Flask(__name__)

app.secret_key = "chave-secreta"

# -----------------------
# BANCO DE DADOS
# -----------------------
def conectar_db():
    return sqlite3.connect("database.db")

# -----------------------
# FUNÇÕES DE HORÁRIO
# -----------------------
def somar_minutos(hora, minutos):
    h = datetime.strptime(hora, "%H:%M")
    return (h + timedelta(minutes=minutos)).strftime("%H:%M")

def horario_livre(data, inicio, fim):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM bloqueios
        WHERE data = ?
        AND NOT (hora_fim <= ? OR hora_inicio >= ?)
    """, (data, inicio, fim))
    livre = cursor.fetchone() is None
    conn.close()
    return livre

# -----------------------
# PLANILHA CSV
# -----------------------
def gerar_planilha():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.cliente, s.nome, a.data, a.hora_inicio, a.hora_fim, a.status
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
    """)
    dados = cursor.fetchall()
    conn.close()

    with open("agendamentos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Cliente", "Serviço", "Data", "Início", "Fim", "Status"])
        writer.writerows(dados)

# -----------------------
# ROTAS
# -----------------------
@app.route("/")
def index():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM servicos")
    servicos = cursor.fetchall()
    conn.close()
    return render_template("index.html", servicos=servicos)

@app.route("/servico", methods=["POST"])
def cadastrar_servico():
    nome = request.form["nome"]
    ativo1 = int(request.form["ativo1"])
    espera = int(request.form["espera"])
    ativo2 = int(request.form["ativo2"])

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO servicos (nome, tempo_ativo_1, tempo_espera, tempo_ativo_2)
        VALUES (?, ?, ?, ?)
    """, (nome, ativo1, espera, ativo2))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/agendar", methods=["POST"])
def agendar():
    cliente = request.form["cliente"]
    servico_id = int(request.form["servico"])
    data = request.form["data"]
    hora_inicio = request.form["hora"]

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tempo_ativo_1, tempo_espera, tempo_ativo_2
        FROM servicos WHERE id = ?
    """, (servico_id,))
    ativo1, espera, ativo2 = cursor.fetchone()

    fim_ativo1 = somar_minutos(hora_inicio, ativo1)
    inicio_ativo2 = somar_minutos(fim_ativo1, espera)
    fim_ativo2 = somar_minutos(inicio_ativo2, ativo2)

    if not horario_livre(data, hora_inicio, fim_ativo1):
        flash("❌ Conflito no tempo ativo inicial", "erro")
        return redirect("/")


    if ativo2 > 0 and not horario_livre(data, inicio_ativo2, fim_ativo2):
        flash("❌ Conflito no tempo ativo final", "erro")
        return redirect("/")

    cursor.execute("""
        INSERT INTO agendamentos
        (cliente, servico_id, data, hora_inicio, hora_fim, status)
        VALUES (?, ?, ?, ?, ?, 'Confirmado')
    """, (cliente, servico_id, data, hora_inicio, fim_ativo2))

    cursor.execute("""
        INSERT INTO bloqueios (data, hora_inicio, hora_fim)
        VALUES (?, ?, ?)
    """, (data, hora_inicio, fim_ativo1))

    if ativo2 > 0:
        cursor.execute("""
            INSERT INTO bloqueios (data, hora_inicio, hora_fim)
            VALUES (?, ?, ?)
        """, (data, inicio_ativo2, fim_ativo2))

    conn.commit()
    conn.close()

    gerar_planilha()
    flash("✅ Agendamento confirmado com sucesso!", "sucesso")
    return redirect("/")

# -----------------------
# EXECUÇÃO
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
