from src.database.db import db
from sqlalchemy.orm import relationship

class ArchivacionBeneficiaria(db.Model):
    __tablename__ = 'Archivacion_Beneficiarias'
    
    idArchivacion_Beneficiarias = db.Column(db.Integer, primary_key=True)
    fecha_archivacion = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(45), nullable=False)
    fk_beneficiaria = db.Column(db.Integer, db.ForeignKey('Beneficiarias.id_beneficiaria'), nullable=False)
    
    # Relaciones
    beneficiaria = relationship('Beneficiaria', back_populates='archivaciones')
    
    def __init__(self, fecha_archivacion, motivo, fk_beneficiaria):
        self.fecha_archivacion = fecha_archivacion
        self.motivo = motivo
        self.fk_beneficiaria = fk_beneficiaria