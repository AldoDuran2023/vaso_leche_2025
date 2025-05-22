from src.database.db import db  # <- Asegúrate que esta importación está bien
from sqlalchemy.orm import relationship
from datetime import datetime

class Gasto(db.Model):
    __tablename__ = 'Gastos'

    idGastos = db.Column(db.Integer, primary_key=True)
    motivo = db.Column(db.String(100), nullable=False)
    fecha_gasto = db.Column(db.DateTime, default=datetime.utcnow)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fk_representante = db.Column(db.Integer, db.ForeignKey('Representantes.id_representante'), nullable=False)

    representante = relationship('Representante', back_populates='gastos')

    
    def __init__(self, motivo, fecha_gasto, monto, fk_representante):
        self.motivo = motivo
        self.fecha_gasto = fecha_gasto
        self.monto = monto
        self.fk_representante = fk_representante