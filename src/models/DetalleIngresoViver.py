from src.database.db import db
from sqlalchemy.orm import relationship

class DetalleIngresoViveres(db.Model):
    __tablename__ = 'Detalle_Ingreso_Viveres'
    
    id_detalle_ingreso = db.Column(db.Integer, primary_key=True)
    fk_ingreso_viver = db.Column(db.Integer, db.ForeignKey('Ingreso_Viveres.idIngreso_Viveres'), nullable=False)
    fk_tipo_viver = db.Column(db.Integer, db.ForeignKey('Tipo_Viveres.id_viver'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    
    # Relaciones
    ingreso_viver = relationship('IngresoViveres', back_populates='detalle_ingresos')
    tipo_viver = relationship('TipoViveres', back_populates='detalle_ingresos')
    
    def __init__(self, fk_ingreso_viver, fk_tipo_viver, cantidad):
        self.fk_ingreso_viver = fk_ingreso_viver
        self.fk_tipo_viver = fk_tipo_viver
        self.cantidad = cantidad