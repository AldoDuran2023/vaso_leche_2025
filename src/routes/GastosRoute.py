# insertar_gasto.py
from flask import Blueprint, request, jsonify
from src.models.Gasto import Gasto
from src.models.Representante import Representante
from src.models.Beneficiaria import Beneficiaria
from src.models.Persona import Persona 
from src.database.db import db
from src.models.Usuario import Usuario
from functionJWT import validate_token
from datetime import datetime

gastos = Blueprint('gastos', __name__)

# Ruta para obtener todos los gastos
@gastos.route('/api/gastos', methods=['GET'])
def obtener_gastos():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        gastos_query = Gasto.query \
            .join(Gasto.representante) \
            .join(Representante.beneficiaria) \
            .join(Beneficiaria.persona) \
            .add_entity(Representante) \
            .add_entity(Beneficiaria) \
            .add_entity(Persona) \
            .order_by(Gasto.fecha_gasto.desc())

        paginated = gastos_query.paginate(page=page, per_page=per_page, error_out=False)

        resultados = []
        for gasto, representante, beneficiaria, persona in paginated.items:
            resultados.append({
                'id_gastos': gasto.idGastos,
                'motivo': gasto.motivo,
                'fecha_gasto': gasto.fecha_gasto.strftime('%Y-%m-%d %H:%M:%S'),
                'monto': float(gasto.monto),
                'representante': {
                    'id_representante': representante.id_representante,
                    'datos_personales': persona.nombres + ' ' + persona.apellido_paterno + ' ' + persona.apellido_materno,
                }
            })

        return jsonify({
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'gastos': resultados
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Ruta para insertar un nuevo gasto
@gastos.route('/api/gastos/create', methods=['POST'])
def insertar_gasto():
    data = request.get_json()

    try:
        # 🔐 Obtener y validar el token
        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({"message": "Token requerido"}), 403
        
        token = token_header.split(" ")[1]
        user_data = validate_token(token, output=True)
        id_usuario = user_data.get("id_usuario")

        # 🔎 Obtener el representante del usuario
        usuario = Usuario.query.get(id_usuario)
        if not usuario or not usuario.representante:
            return jsonify({"message": "Usuario o representante no válido"}), 400

        representante = usuario.representante
        
        motivo = data['motivo']
        fecha_gasto = datetime.today().isoformat()
        monto = data['monto']
        fk_representante = representante.id_representante

        nuevo_gasto = Gasto(
            motivo=motivo,
            fecha_gasto=fecha_gasto,
            monto=monto,
            fk_representante=fk_representante
        )

        db.session.add(nuevo_gasto)
        db.session.commit()

        return jsonify({"message": "Gasto registrado exitosamente"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
