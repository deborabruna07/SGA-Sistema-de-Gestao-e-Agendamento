from flask import Flask, render_template, request, redirect, flash
from flask import jsonify

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

def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tempo_ativo_1 INTEGER NOT NULL,
            tempo_espera INTEGER NOT NULL,
            tempo_ativo_2 INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            servico_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (servico_id) REFERENCES servicos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bloqueios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

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

    # Serviços (para o formulário)
    cursor.execute("SELECT id, nome FROM servicos")
    servicos = cursor.fetchall()

    # Agendamentos (para a tabela)
    cursor.execute("""
        SELECT 
            a.id,
            a.cliente,
            s.nome,
            a.data,
            a.hora_inicio,
            a.hora_fim,
            a.status
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        ORDER BY a.data, a.hora_inicio
    """)
    agendamentos = cursor.fetchall()
    conn.close()

    # ⬇⬇⬇ render_template vem SÓ NO FINAL
    return render_template(
        "index.html",
        servicos=servicos,
        agendamentos=agendamentos,
    )
    
@app.route("/admin")
def admin():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome FROM servicos")
    servicos = cursor.fetchall()

    cursor.execute("""
        SELECT 
            a.id,
            a.cliente,
            s.nome,
            a.data,
            a.hora_inicio,
            a.hora_fim,
            a.status
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        ORDER BY a.data, a.hora_inicio
    """)
    agendamentos = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        servicos=servicos,
        agendamentos=agendamentos
    )


@app.route("/servico", methods=["POST"])
def cadastrar_servico():
    nome = request.form.get("nome")

    ativo1 = request.form.get("ativo1") or 0
    espera = request.form.get("espera") or 0
    ativo2 = request.form.get("ativo2") or 0

    ativo1 = int(ativo1)
    espera = int(espera)
    ativo2 = int(ativo2)

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO servicos (nome, tempo_ativo_1, tempo_espera, tempo_ativo_2)
        VALUES (?, ?, ?, ?)
    """, (nome, ativo1, espera, ativo2))
    conn.commit()
    conn.close()

    return jsonify(sucesso=True)

@app.route("/servico", methods=["GET"])
def listar_servicos():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome FROM servicos")
    rows = cursor.fetchall()
    conn.close()

    servicos = []
    for r in rows:
        servicos.append({
            "id": r[0],
            "nome": r[1]
        })

    return jsonify(servicos)


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
        flash("❌ Conflito de horário. Não é possível agendar!", "erro")
        return redirect("/")


    if ativo2 > 0 and not horario_livre(data, inicio_ativo2, fim_ativo2):
        flash("❌ Conflito de horário. Não é possível agendar!", "erro")
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

@app.route("/cancelar/<int:id>")
def cancelar(id):
    conn = conectar_db()
    cursor = conn.cursor()

    # Buscar dados do agendamento
    cursor.execute("""
        SELECT data, hora_inicio, hora_fim 
        FROM agendamentos 
        WHERE id = ?
    """, (id,))
    agendamento = cursor.fetchone()

    if not agendamento:
        conn.close()
        flash("❌ Agendamento não encontrado.", "erro")
        return redirect("/")

    data, inicio, fim = agendamento

    # Atualizar status
    cursor.execute("""
        UPDATE agendamentos
        SET status = 'Cancelado'
        WHERE id = ?
    """, (id,))

    # Remover bloqueios do horário
    cursor.execute("""
        DELETE FROM bloqueios
        WHERE data = ?
        AND hora_inicio >= ?
        AND hora_fim <= ?
    """, (data, inicio, fim))

    conn.commit()
    conn.close()

    flash("✅ Agendamento cancelado com sucesso.", "sucesso")
    return redirect("/")

@app.route("/horarios/<data>/<int:servico_id>")
def horarios_disponiveis(data, servico_id):
    horarios_base = [
        "08:00","08:30","09:00","09:30","10:00","10:30",
        "11:00","11:30","13:00","13:30","14:00","14:30",
        "15:00","15:30","16:00","16:30", "17:00"
    ]

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT hora_inicio, hora_fim
        FROM bloqueios
        WHERE data = ?
    """, (data,))
    bloqueios = cursor.fetchall()
    conn.close()

    disponiveis = []

    for h in horarios_base:
        ocupado = False
        for b in bloqueios:
            if b[0] <= h < b[1]:
                ocupado = True
        if not ocupado:
            disponiveis.append(h)

    return jsonify(disponiveis)

@app.route("/limpar-antigos")
def limpar_antigos():
    hoje = datetime.now().strftime("%Y-%m-%d")

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM agendamentos WHERE data < ?", (hoje,))
    cursor.execute("DELETE FROM bloqueios WHERE data < ?", (hoje,))

    conn.commit()
    conn.close()

    flash("🧹 Agendamentos antigos removidos!", "sucesso")
    return redirect("/admin")

@app.route("/limpar-tudo")
def limpar_tudo():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM agendamentos")
    cursor.execute("DELETE FROM bloqueios")

    conn.commit()
    conn.close()

    flash("🧹 Todos os agendamentos foram apagados com sucesso.", "admin")
    return redirect("/admin")

@app.route("/remover-servico/<int:id>")
def remover_servico(id):
    conn = conectar_db()
    cursor = conn.cursor()

    # Remove o serviço
    cursor.execute("DELETE FROM servicos WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    flash("Serviço removido com sucesso.", "admin")
    return redirect("/admin")

@app.route("/servico/<int:id>", methods=["DELETE"])
def excluir_servico(id):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM servicos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify(sucesso=True)


# -----------------------
# EXECUÇÃO
# -----------------------
if __name__ == "__main__":
    criar_tabelas()
    app.run(debug=True)

