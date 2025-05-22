from src.database.db import db
from sqlalchemy.orm import relationship
from src.models.CierreAnual import CierreAnual


class JuntaDirectiva(db.Model):
    __tablename__ = 'Juntas_Directivas'
    
    idJuntas_Directivas = db.Column(db.Integer, primary_key=True)
    anio = db.Column(db.String(4), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    estado = db.Column(db.Enum('Activa', 'Inactiva', name='estado_junta'), default='Activa')
    
    # Relaciones
    representantes = relationship('Representante', back_populates='junta_directiva')
    reuniones = relationship('Reunion', back_populates='junta_directiva')
    cierres_anuales = relationship(lambda: CierreAnual, back_populates='junta_directiva')
    ingreso_viveres = relationship('IngresoViveres', back_populates='junta_directiva')
    
    def __init__(self, anio, fecha_inicio, fecha_fin=None, estado='Activa'):
        self.anio = anio
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado