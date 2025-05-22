from src.database.db import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Asistencia(db.Model):
    __tablename__ = 'Asistencias'
    
    id_asistencia = db.Column(db.Integer, primary_key=True)
    presente = db.Column(db.Boolean, default=False)
    justificacion_tardanza = db.Column(db.String(45))
    fk_reunion = db.Column(db.Integer, db.ForeignKey('Reuniones.id_reunion'), nullable=False)
    fk_beneficiaria = db.Column(db.Integer, db.ForeignKey('Beneficiarias.id_beneficiaria'), nullable=False)
    
    # Relaciones
    reunion = relationship('Reunion', back_populates='asistencias')
    beneficiaria = relationship('Beneficiaria', back_populates='asistencias')
    
    def __init__(self, fk_reunion, fk_beneficiaria, presente=False, justificcion_tardanza=None):
        self.presente = presente
        self.justificcion_tardanza = justificcion_tardanza
        self.fk_reunion = fk_reunion
        self.fk_beneficiaria = fk_beneficiaria