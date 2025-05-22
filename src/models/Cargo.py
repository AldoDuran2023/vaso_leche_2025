from src.database.db import db
from sqlalchemy.orm import relationship

class Cargo(db.Model):
    __tablename__ = 'Cargos'
    
    id_cargo = db.Column(db.Integer, primary_key=True)
    cargo = db.Column(db.String(45), nullable=False)
    deberes = db.Column(db.String(50))
    
    # Relaciones
    representantes = relationship('Representante', back_populates='cargo')
    
    def __init__(self, cargo, deberes=None):
        self.cargo = cargo
        self.deberes = deberes