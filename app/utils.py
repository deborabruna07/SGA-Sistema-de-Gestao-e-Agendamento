from datetime import datetime, timedelta
from app.database import conectar_db
import csv
import os


import sib_api_v3_sdk
from sib_api_v3_sdk.api.transactional_emails_api import TransactionalEmailsApi
from sib_api_v3_sdk.models.send_smtp_email import SendSmtpEmail

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


def enviar_email(nome, email, servico, data, hora):
    if not email:
        return

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = os.getenv("BREVO_API_KEY")

    api_instance = TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email_data = SendSmtpEmail(
        to=[{"email": email, "name": nome}],
        sender={
            "email": "bethsalao.agendamentos@gmail.com",
            "name": "Beth Salão & Cosmetics"
        },
        subject="Agendamento confirmado ✔",
        html_content=f"""
            <h3>Olá, {nome}! 💕</h3>
            <h4>\nSeu agendamento foi confirmado com sucesso. 😉\n</h4>
            <p><b> 💁‍♀️ Serviço:</b> {servico}</p>
            <p><b>🗓️ Data:</b> {data}</p>
            <p><b>\n🕑 Horário:</b> {hora}\n</p>
            <h5><b>⚠️ Em caso de cancelamento, avisar com 2 dias de antecedência.<b></p>
        """
    )

    try:
        api_instance.send_transac_email(email_data)
        print("📩 Email enviado com sucesso")
    except Exception as e:
        print("❌ Erro ao enviar email:", e)