from src.database.db import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Movimiento(db.Model):
    __tablename__ = 'Movimientos'

    idMovimientos = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Numeric(5, 2), nullable=False)
    fecha_movimiento = db.Column(db.Date, nullable=False)
    fk_representante = db.Column(db.Integer, db.ForeignKey('Representantes.id_representante'), nullable=False)
    fk_multa = db.Column(db.Integer, db.ForeignKey('multas.id_multa'), nullable=False)
    tipo_movimiento = db.Column(db.Enum('Ingreso', 'Egreso', name='tipo_movimiento_enum'), default='Ingreso')
    descripcion = db.Column(db.String(100))

    representante = relationship('Representante', back_populates='movimientos')
    multa_rel = relationship('Multa', back_populates='movimientos')

    def __init__(self, monto, fecha_movimiento, fk_representante, fk_multa):
        self.monto = monto
        self.fecha_movimiento = fecha_movimiento
        self.fk_representante = fk_representante
        self.fk_multa = fk_multa
