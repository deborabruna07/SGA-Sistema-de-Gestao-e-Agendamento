from app import create_app
from app.database import criar_tabelas

# Inicializa o sistema através da Factory
app = create_app()

if __name__ == "__main__":
    # Garante que o banco e as tabelas existam antes de iniciar
    with app.app_context():
        criar_tabelas()
    
    # Roda o servidor
    app.run(host="0.0.0.0", port=5000, debug=True)