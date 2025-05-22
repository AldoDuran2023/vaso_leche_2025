from src.database.db import db
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.Movimiento import Movimiento

class Multa(db.Model):
    __tablename__ = 'multas'
    
    id_multa = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_beneficiaria = db.Column(db.Integer, db.ForeignKey('Beneficiarias.id_beneficiaria'), nullable=False)
    fk_tipo_multa = db.Column(db.Integer, db.ForeignKey('tipo_multa.id_tipo_multa'), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_multa = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    pagado = db.Column(db.SmallInteger, default=0)  # 0 = No pagado, 1 = Pagado
    fecha_pago = db.Column(db.Date)
    observaciones = db.Column(db.String(100))
    
    # Relaciones
    movimientos = relationship('Movimiento', back_populates='multa_rel', lazy=True, cascade='all, delete-orphan')
    beneficiaria = relationship('Beneficiaria', back_populates='multas')
    
    def __init__(self, fk_beneficiaria, fk_tipo_multa, monto, fecha_multa=None, pagado=0, fecha_pago=None, observaciones=None):
        self.fk_beneficiaria = fk_beneficiaria
        self.fk_tipo_multa = fk_tipo_multa
        self.monto = monto
        self.fecha_multa = fecha_multa or datetime.utcnow().date()
        self.pagado = pagado
        self.fecha_pago = fecha_pago
        self.observaciones = observaciones
        
        if pagado == 1 and not self.fecha_pago:
            self.fecha_pago = datetime.utcnow().date()

        
    def marcar_como_pagada(self, fecha_pago=None):
        """Marca la multa como pagada"""
        self.pagado = 1
        self.fecha_pago = fecha_pago or datetime.utcnow().date()
        db.session.commit()
    
    def get_total_pagado(self):
        """Calcula el total pagado de esta multa a través de movimientos"""
        total = db.session.query(db.func.sum(Movimiento.monto)).filter_by(
            fk_multa=self.id_multa,
            tipo_movimiento='Ingreso'
        ).scalar()
        return float(total) if total else 0.0