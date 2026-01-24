import sqlite3

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