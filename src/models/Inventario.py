from src.database.db import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Inventario(db.Model):
    __tablename__ = 'Inventarios'
    
    id_inventario = db.Column(db.Integer, primary_key=True)
    fk_tipo_viver = db.Column(db.Integer, db.ForeignKey('Tipo_Viveres.id_viver'), nullable=False)
    cantidad_total = db.Column(db.Integer, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    tipo_viver = relationship('TipoViveres', back_populates='inventarios')
    
    def __init__(self, fk_tipo_viver, cantidad_total):
        self.fk_tipo_viver = fk_tipo_viver
        self.cantidad_total = cantidad_total