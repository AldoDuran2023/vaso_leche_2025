from src.database.db import db
from sqlalchemy.orm import relationship
from src.models.Entrega import Entrega
from src.models.DetalleViverEntregado import DetalleViveresEntregados

class DetalleEntrega(db.Model):
    __tablename__ = 'Detalle_Entregas'
    
    id_detalle_entregas = db.Column(db.Integer, primary_key=True)
    fk_entrega = db.Column(db.Integer, db.ForeignKey('Entregas.id_racion'), nullable=False)
    fk_beneficiaria = db.Column(db.Integer, db.ForeignKey('Beneficiarias.id_beneficiaria'), nullable=False)
    cantidad_raciones = db.Column(db.Integer, nullable=False)
    
    # Relaciones
    entrega = relationship('Entrega', back_populates='detalle_entregas')
    beneficiaria = relationship('Beneficiaria', back_populates='detalle_entregas')
    entrega = relationship(Entrega, back_populates='detalle_entregas')
    detalles_viveres = relationship('DetalleViveresEntregados', back_populates='detalle_entrega')
    
    def __init__(self, fk_entrega, fk_beneficiaria, cantidad_raciones):
        self.fk_entrega = fk_entrega
        self.fk_beneficiaria = fk_beneficiaria
        self.cantidad_raciones = cantidad_raciones