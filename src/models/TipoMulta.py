from src.database.db import db
from sqlalchemy.orm import relationship

class TipoMulta(db.Model):
    __tablename__ = 'tipo_multa'
    
    id_tipo_multa = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_multa = db.Column(db.String(45), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relación con Multas
    multas = db.relationship('Multa', backref='tipo_multa_rel', lazy=True)

    def __init__(self, tipo_multa, monto):
        self.tipo_multa = tipo_multa
        self.monto = monto
