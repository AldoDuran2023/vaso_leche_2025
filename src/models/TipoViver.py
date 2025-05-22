from src.database.db import db
from sqlalchemy.orm import relationship

class TipoViveres(db.Model):
    __tablename__ = 'Tipo_Viveres'
    
    id_viver = db.Column(db.Integer, primary_key=True)
    viver = db.Column(db.String(45), nullable=False)
    tipo_unidad = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(45))
    
    # Relaciones
    inventarios = relationship('Inventario', back_populates='tipo_viver')
    detalle_ingresos = relationship('DetalleIngresoViveres', back_populates='tipo_viver')
    detalle_viveres_entregados = relationship('DetalleViveresEntregados', back_populates='tipo_viver')
    
    def __init__(self, viver, tipo_unidad, descripcion=None):
        self.viver = viver
        self.tipo_unidad = tipo_unidad
        self.descripcion = descripcion