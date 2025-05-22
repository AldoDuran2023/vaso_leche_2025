from src.database.db import db
from sqlalchemy.orm import relationship

class TipoBeneficiaria(db.Model):
    __tablename__ = 'Tipo_Beneficiaria'
    
    id_tipo_beneficiaria = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(45), nullable=False)
    cantidad_raciones = db.Column(db.Integer, nullable=False)
    
    # Relaciones
    beneficiarias = relationship('Beneficiaria', back_populates='tipo_beneficiaria')
    
    def __init__(self, tipo, cantidad_raciones):
        self.tipo = tipo
        self.cantidad_raciones = cantidad_raciones