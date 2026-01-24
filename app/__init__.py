from flask import Flask
import os

def create_app():
    # Inicializa o Flask
    app = Flask(__name__)
    
    # Configurações básicas
    app.secret_key = os.getenv("SECRET_KEY", "chave-secreta-padrao")

    # Importa os Blueprints (importação dentro da função evita erros de ciclo)
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp

    # REGISTRO dos Blueprints
    # Aqui o Flask "aprende" as rotas que você criou nos outros arquivos
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app