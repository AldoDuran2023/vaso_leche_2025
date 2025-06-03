from src.database.db import db
from sqlalchemy.orm import relationship

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(55), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    fullname = db.Column(db.String(65), nullable=False)
    fk_representante = db.Column(db.Integer, db.ForeignKey('Representantes.id_representante'), nullable=False)
    
    representante = relationship('Representante', back_populates='usuario', uselist=False)

    def __init__(self, username, contrasena, fullname, fk_representante):
        self.username = username
        self.contrasena = contrasena
        self.fullname = fullname
        self.fk_representante = fk_representante

