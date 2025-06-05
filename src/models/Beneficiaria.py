from src.database.db import db
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.Hijo import Hijo
from src.models.DetalleEntrega import DetalleEntrega
from src.models.Representante import Representante
from src.models.Asistencia import Asistencia
from src.models.Multa import Multa

class Beneficiaria(db.Model):
    __tablename__ = 'Beneficiarias'
    
    id_beneficiaria = db.Column(db.Integer, primary_key=True)
    fk_tipo_beneficiaria = db.Column(db.Integer, db.ForeignKey('Tipo_Beneficiaria.id_tipo_beneficiaria'), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    cantidad_hijos = db.Column(db.Integer, default=0)
    codigo_SISFOH = db.Column(db.String(14))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fk_persona = db.Column(db.Integer, db.ForeignKey('Personas.id_persona'), nullable=False)
    
    # Relaciones
    tipo_beneficiaria = relationship('TipoBeneficiaria', back_populates='beneficiarias')
    persona = relationship('Persona', back_populates='beneficiarias')
    hijos = relationship(lambda: Hijo, back_populates='beneficiaria')
    representantes = relationship(lambda: Representante, back_populates='beneficiaria')
    asistencias = relationship(lambda: Asistencia, back_populates='beneficiaria')
    multas = relationship(lambda: Multa, back_populates='beneficiaria', cascade='all, delete-orphan', lazy=True)
    detalle_entregas = relationship(lambda: DetalleEntrega, back_populates='beneficiaria')
    
    def __init__(self, fk_tipo_beneficiaria, fk_persona, estado=True, cantidad_hijos=0, codigo_SISFOH=None):
        self.fk_tipo_beneficiaria = fk_tipo_beneficiaria
        self.fk_persona = fk_persona
        self.estado = estado
        self.cantidad_hijos = cantidad_hijos
        self.codigo_SISFOH = codigo_SISFOH
