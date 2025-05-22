from src.database.db import db
from sqlalchemy.orm import relationship

class DetalleViveresEntregados(db.Model):
    __tablename__ = 'Detalle_Viveres_Entregados'
    
    id_detalle_viver_entregado = db.Column(db.Integer, primary_key=True)
    fk_detalle_entrega = db.Column(db.Integer, db.ForeignKey('Detalle_Entregas.id_detalle_entregas'), nullable=False)
    fk_tipo_viver = db.Column(db.Integer, db.ForeignKey('Tipo_Viveres.id_viver'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    
    # Relaciones
    detalle_entrega = relationship('DetalleEntrega', back_populates='detalles_viveres')
    tipo_viver = relationship('TipoViveres', back_populates='detalle_viveres_entregados')
    
    def __init__(self, fk_detalle_entrega, fk_tipo_viver, cantidad):
        self.fk_detalle_entrega = fk_detalle_entrega
        self.fk_tipo_viver = fk_tipo_viver
        self.cantidad = cantidad