from src.database.db import db
from sqlalchemy.orm import relationship

class Persona(db.Model):
    __tablename__ = 'Personas'
    
    id_persona = db.Column(db.Integer, primary_key=True)
    DNI = db.Column(db.String(8), unique=True, nullable=False)
    nombres = db.Column(db.String(55), nullable=False)
    apellido_paterno = db.Column(db.String(45), nullable=False)
    apellido_materno = db.Column(db.String(45), nullable=False)
    direccion = db.Column(db.String(45), nullable=False)
    
    beneficiarias = relationship('Beneficiaria', back_populates='persona')
    hijos = relationship('Hijo', back_populates='persona')
    
    def __init__(self, DNI, nombres, apellido_paterno, apellido_materno, direccion):
        self.DNI = DNI
        self.nombres = nombres
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.direccion = direccion