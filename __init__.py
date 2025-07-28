import os
from flask import Flask
from dotenv import load_dotenv
from models import db
from auth import login_manager, auth_bp
from routes import main_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'uma_chave_secreta_muito_segura')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
