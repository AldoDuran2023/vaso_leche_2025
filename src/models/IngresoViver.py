from src.database.db import db
from sqlalchemy.orm import relationship

class IngresoViveres(db.Model):
    __tablename__ = 'Ingreso_Viveres'
    
    idIngreso_Viveres = db.Column(db.Integer, primary_key=True)
    fecha_ingreso = db.Column(db.Date, nullable=False)
    responsable = db.Column(db.String(30), nullable=False)
    fk_junta_directiva = db.Column(db.Integer, db.ForeignKey('Juntas_Directivas.idJuntas_Directivas'), nullable=False)
    
    # Relaciones
    junta_directiva = relationship('JuntaDirectiva', back_populates='ingreso_viveres')
    detalle_ingresos = relationship('DetalleIngresoViveres', back_populates='ingreso_viver')
    
    def __init__(self, fecha_ingreso, responsable, fk_junta_directiva):
        self.fecha_ingreso = fecha_ingreso
        self.responsable = responsable
        self.fk_junta_directiva = fk_junta_directiva