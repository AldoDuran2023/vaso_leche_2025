from src.database.db import db
from sqlalchemy.orm import relationship

class Hijo(db.Model):
    __tablename__ = 'Hijos'

    id_hijo = db.Column(db.Integer, primary_key=True)
    fk_beneficiaria = db.Column(db.Integer, db.ForeignKey('Beneficiarias.id_beneficiaria'), nullable=False)
    fk_persona = db.Column(db.Integer, db.ForeignKey('Personas.id_persona'), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    estado = db.Column(db.Enum('Activo', 'Inactivo', name='estado_hijo'), default='Activo')
    numero_partida = db.Column(db.String(20))
    
    beneficiaria = relationship('Beneficiaria', back_populates='hijos')
    persona = relationship('Persona', back_populates='hijos')
    
    def __init__(self, fk_beneficiaria, fk_persona, fecha_nacimiento, estado='Activo', numero_partida=None):
        self.fk_beneficiaria = fk_beneficiaria
        self.fk_persona = fk_persona
        self.fecha_nacimiento = fecha_nacimiento
        self.estado = estado
        self.numero_partida = numero_partida