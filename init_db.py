from __init__ import create_app
from models import db

app = create_app()

with app.app_context():
    db.create_all()

print("Banco de dados inicializado com sucesso!")
