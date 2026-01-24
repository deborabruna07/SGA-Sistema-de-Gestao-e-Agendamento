from flask import Blueprint, render_template, request, redirect, flash, jsonify
from datetime import datetime
# Importamos a conexão que você moveu para database.py
from app.database import conectar_db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/admin")
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


@admin_bp.route("/servico", methods=["POST"])
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

@admin_bp.route("/servico", methods=["GET"])
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

@admin_bp.route("/limpar-antigos")
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

@admin_bp.route("/limpar-tudo")
def limpar_tudo():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM agendamentos")
    cursor.execute("DELETE FROM bloqueios")

    conn.commit()
    conn.close()

    flash("🧹 Todos os agendamentos foram apagados com sucesso.", "admin")
    return redirect("/admin")

@admin_bp.route("/remover-servico/<int:id>")
def remover_servico(id):
    conn = conectar_db()
    cursor = conn.cursor()

    # Remove o serviço
    cursor.execute("DELETE FROM servicos WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    flash("Serviço removido com sucesso.", "admin")
    return redirect("/admin")

@admin_bp.route("/servico/<int:id>", methods=["DELETE"])
def excluir_servico(id):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM servicos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify(sucesso=True)