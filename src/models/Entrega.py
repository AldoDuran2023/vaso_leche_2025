from src.database.db import db
from sqlalchemy.orm import relationship

class Entrega(db.Model):
    __tablename__ = 'Entregas'
    
    id_racion = db.Column(db.Integer, primary_key=True)
    fk_representante = db.Column(db.Integer, db.ForeignKey('Representantes.id_representante'), nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    estado = db.Column(db.Enum('Realizada', 'Pendiente', name='estado_entrega'), default='Pendiente')
    
    # Relaciones
    representante = relationship('Representante', back_populates='entregas')
    detalle_entregas = relationship('DetalleEntrega', back_populates='entrega')
    
    def __init__(self, fk_representante, fecha_entrega, estado='Pendiente'):
        self.fk_representante = fk_representante
        self.fecha_entrega = fecha_entrega
        self.estado = estado