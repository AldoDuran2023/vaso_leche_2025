from src.database.db import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Reunion(db.Model):
    __tablename__ = 'Reuniones'
    
    id_reunion = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.DateTime, nullable=False)
    lugar = db.Column(db.String(45), nullable=False)
    motivo = db.Column(db.String(45), nullable=False)
    fk_junta_directiva = db.Column(db.Integer, db.ForeignKey('Juntas_Directivas.idJuntas_Directivas'), nullable=False)
    estado_reunion = db.Column(db.Boolean, default=False)
    
    # Relaciones
    junta_directiva = relationship('JuntaDirectiva', back_populates='reuniones')
    asistencias = relationship('Asistencia', back_populates='reunion')
    
    def __init__(self, fecha, hora, lugar, motivo, fk_junta_directiva):
        self.fecha = fecha
        self.hora = hora
        self.lugar = lugar
        self.motivo = motivo
        self.fk_junta_directiva = fk_junta_directiva