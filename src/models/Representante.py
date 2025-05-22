from src.database.db import db
from sqlalchemy.orm import relationship

class Representante(db.Model):
    __tablename__ = 'Representantes'
    
    id_representante = db.Column(db.Integer, primary_key=True)
    fk_cargo = db.Column(db.Integer, db.ForeignKey('Cargos.id_cargo'), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    fk_beneficiaria = db.Column(db.Integer, db.ForeignKey('Beneficiarias.id_beneficiaria'), nullable=False)
    fk_junta_directiva = db.Column(db.Integer, db.ForeignKey('Juntas_Directivas.idJuntas_Directivas'), nullable=False)
    
    # Relaciones
    cargo = relationship('Cargo', back_populates='representantes')
    beneficiaria = relationship('Beneficiaria', back_populates='representantes')
    junta_directiva = relationship('JuntaDirectiva', back_populates='representantes')
    movimientos = relationship('Movimiento', back_populates='representante')
    gastos = relationship('Gasto', back_populates='representante')
    entregas = relationship('Entrega', back_populates='representante')
    
    def __init__(self, fk_cargo, fecha_registro, fk_beneficiaria, fk_junta_directiva, estado=True, fecha_fin=None):
        self.fk_cargo = fk_cargo
        self.estado = estado
        self.fecha_registro = fecha_registro
        self.fecha_fin = fecha_fin
        self.fk_beneficiaria = fk_beneficiaria
        self.fk_junta_directiva = fk_junta_directiva