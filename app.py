from flask import Flask
from config import DATABASE_CONECCTION_URI
from src.database.db import db
from dotenv import load_dotenv
from src.routes.AsistenciaRoute import asistencias
from src.routes.BeneficiariaRoute import beneficiarias
from src.routes.IngresoViverRouter import ingresos_viveres
from src.routes.JuntaDirectivaRoute import juntas_directivas
from src.routes.RepresentanteRoute import representantes
from src.routes.ReunionRoute import reuniones
from src.routes.ViverRoute import tipo_viveres
from src.routes.CargoRoute import cargos_bp
from src.routes.InventarioRoute import inventarios_bp
from src.routes.MultaRouter import multas
from src.routes.MovimientoRoute import movimiento
from src.routes.EntregaRoute import entregas
from src.routes.RacionesRoute import detalle_entregas
from src.routes.GastosRoute import gastos
from src.routes.auth import auth
from flask_cors import CORS
import os

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONECCTION_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa la base de datos con la app
db.init_app(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

app.register_blueprint(auth)
app.register_blueprint(asistencias)
app.register_blueprint(beneficiarias)
app.register_blueprint(gastos)
app.register_blueprint(ingresos_viveres)
app.register_blueprint(juntas_directivas)
app.register_blueprint(representantes)
app.register_blueprint(reuniones)
app.register_blueprint(tipo_viveres)
app.register_blueprint(cargos_bp)
app.register_blueprint(inventarios_bp)
app.register_blueprint(multas)
app.register_blueprint(movimiento)
app.register_blueprint(entregas)
app.register_blueprint(detalle_entregas)

# Ruta de prueba
@app.route('/')
def inicio():
    return "Hola"
