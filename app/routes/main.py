from flask import Blueprint, render_template, request, redirect, flash, jsonify
from app.database import conectar_db
from app.utils import somar_minutos, horario_livre
from app.utils import gerar_planilha
from app.utils import enviar_email

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
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

@main_bp.route("/agendar", methods=["POST"])
def agendar():
    cliente = request.form["cliente"]
    servico_id = int(request.form["servico"])
    data = request.form["data"]
    hora_inicio = request.form["hora"]
    email = request.form.get("emailCliente")
    telefone = request.form.get("telefoneCliente")

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
        
    cursor.execute("SELECT nome FROM servicos WHERE id = ?", (servico_id,))
    nome_servico = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    gerar_planilha()
    
    # depois de gerar_planilha()
    try:
        enviar_email(cliente, email, nome_servico, data, hora_inicio)
    except Exception as e:
        print("Erro ao enviar email:", e)

    flash("✅ Agendamento confirmado com sucesso!", "sucesso")
    return redirect("/")


@main_bp.route("/cancelar/<int:id>")
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


@main_bp.route("/horarios/<data>/<int:servico_id>")
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

@main_bp.route("/remover-servico/<int:id>")
def remover_servico(id):
    conn = conectar_db()
    cursor = conn.cursor()

    # Remove o serviço
    cursor.execute("DELETE FROM servicos WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    flash("Serviço removido com sucesso.", "admin")
    return redirect("/admin")

@main_bp.route("/servico/<int:id>", methods=["DELETE"])
def excluir_servico(id):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM servicos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify(sucesso=True)