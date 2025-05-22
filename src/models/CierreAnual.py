from src.database.db import db
from sqlalchemy.orm import relationship

class CierreAnual(db.Model):
    __tablename__ = 'Cierres_Anuales'
    
    id_cierre_anual = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    saldo_inicial = db.Column(db.Numeric(10, 2), nullable=False)
    saldo_final = db.Column(db.Numeric(10, 2), nullable=False)
    total_ingresos = db.Column(db.Numeric(10, 2), nullable=False)
    total_gastos = db.Column(db.Numeric(10, 2), nullable=False)
    observaciones = db.Column(db.String(100))
    fk_junta_directiva = db.Column(db.Integer, db.ForeignKey('Juntas_Directivas.idJuntas_Directivas'), nullable=False)
    
    # Relaciones
    junta_directiva = relationship('JuntaDirectiva', back_populates='cierres_anuales')
    
    def __init__(self, fecha, saldo_inicial, saldo_final, total_ingresos, total_gastos, fk_junta_directiva, observaciones=None):
        self.fecha = fecha
        self.saldo_inicial = saldo_inicial
        self.saldo_final = saldo_final
        self.total_ingresos = total_ingresos
        self.total_gastos = total_gastos
        self.observaciones = observaciones
        self.fk_junta_directiva = fk_junta_directiva