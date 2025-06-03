from flask import Blueprint, request, jsonify, url_for
from src.models.Persona import Persona
from src.models.Beneficiaria import Beneficiaria
from src.models.TipoBeneficiaria import TipoBeneficiaria
from src.database.db import db
from utils.paginador import paginar_query 
from functionJWT import validate_token 


beneficiarias = Blueprint('beneficiarias', __name__)

# Solo los autenticados pueden acceder
@beneficiarias.before_request
def verificar_token():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token, output=False)

# ruta para obtener todas las beneficiarias
@beneficiarias.route('/api/beneficiarias', methods=['GET'])
def get_beneficiarias():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        query = db.session.query(Beneficiaria).join(Beneficiaria.persona).join(Beneficiaria.tipo_beneficiaria)

        paginated_data = query.paginate(page=page, per_page=per_page, error_out=False)

        beneficiarias_data = []
        for beneficiaria in paginated_data.items:
            beneficiaria_dict = {
                'id_beneficiaria': beneficiaria.id_beneficiaria,
                'estado': beneficiaria.estado,
                'cantidad_hijos': beneficiaria.cantidad_hijos,
                'codigo_SISFOH': beneficiaria.codigo_SISFOH,
                'fecha_registro': beneficiaria.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if beneficiaria.fecha_registro else None,
                'persona': {
                    'id_persona': beneficiaria.persona.id_persona,
                    'DNI': beneficiaria.persona.DNI,
                    'nombres': beneficiaria.persona.nombres,
                    'apellido_paterno': beneficiaria.persona.apellido_paterno,
                    'apellido_materno': beneficiaria.persona.apellido_materno,
                    'direccion': beneficiaria.persona.direccion,
                    'nombre_completo': f"{beneficiaria.persona.nombres} {beneficiaria.persona.apellido_paterno} {beneficiaria.persona.apellido_materno}"
                },
                'tipo_beneficiaria': {
                    'id_tipo_beneficiaria': beneficiaria.tipo_beneficiaria.id_tipo_beneficiaria,
                    'tipo': beneficiaria.tipo_beneficiaria.tipo,
                    'cantidad_raciones': beneficiaria.tipo_beneficiaria.cantidad_raciones
                }
            }
            beneficiarias_data.append(beneficiaria_dict)

        next_page_url = url_for('beneficiarias.get_beneficiarias', page=page + 1, per_page=per_page, _external=True) if paginated_data.has_next else None
        prev_page_url = url_for('beneficiarias.get_beneficiarias', page=page - 1, per_page=per_page, _external=True) if paginated_data.has_prev else None

        return jsonify({
            'success': True,
            'data': beneficiarias_data,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': query.count(),
                'total_pages': (query.count() + per_page - 1) // per_page,
                'next_page_url': next_page_url,
                'prev_page_url': prev_page_url
            },
            'message': 'Beneficiarias obtenidas exitosamente'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
# ruta para obtener a todas las beneficiarias activas sin paginador
@beneficiarias.route('/api/beneficiarias/activas', methods=['GET'])
def get_beneficiarias_activas():
    try:
        beneficiarias = db.session.query(Beneficiaria)\
            .join(Persona, Beneficiaria.fk_persona == Persona.id_persona)\
            .join(TipoBeneficiaria, Beneficiaria.fk_tipo_beneficiaria == TipoBeneficiaria.id_tipo_beneficiaria)\
            .filter(Beneficiaria.estado == True)\
            .all()
        
        beneficiarias_data = []
        for beneficiaria in beneficiarias:
            beneficiarias_data.append({
                'id_beneficiaria': beneficiaria.id_beneficiaria,
                'estado': beneficiaria.estado,
                'cantidad_hijos': beneficiaria.cantidad_hijos,
                'codigo_SISFOH': beneficiaria.codigo_SISFOH,
                'fecha_registro': beneficiaria.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if beneficiaria.fecha_registro else None,
                'persona': {
                    'id_persona': beneficiaria.persona.id_persona,
                    'DNI': beneficiaria.persona.DNI,
                    'nombres': beneficiaria.persona.nombres,
                    'apellido_paterno': beneficiaria.persona.apellido_paterno,
                    'apellido_materno': beneficiaria.persona.apellido_materno,
                    'direccion': beneficiaria.persona.direccion,
                    'nombre_completo': f"{beneficiaria.persona.nombres} {beneficiaria.persona.apellido_paterno} {beneficiaria.persona.apellido_materno}"
                },
                'tipo_beneficiaria': {
                    'id_tipo_beneficiaria': beneficiaria.tipo_beneficiaria.id_tipo_beneficiaria,
                    'tipo': beneficiaria.tipo_beneficiaria.tipo,
                    'cantidad_raciones': beneficiaria.tipo_beneficiaria.cantidad_raciones
                }
            })
        
        return jsonify({
            'success': True,
            'data': beneficiarias_data,
            'message': 'Beneficiarias activas obtenidas exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ruta para insertar una nueva beneficiaria
@beneficiarias.route('/api/beneficiarias/create', methods=['POST'])
def create_beneficiaria():
    try:
        data = request.get_json()
        
        # Validamos que los datos requeridos estén presentes
        required_fields = ['DNI', 'nombres', 'apellido_paterno', 'apellido_materno', 'direccion', 'fk_tipo_beneficiaria']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }), 400
        
        # Verificamos que no exista una persona con el mismo DNI
        persona_existente = Persona.query.filter_by(DNI=data['DNI']).first()
        if persona_existente:
            return jsonify({
                'success': False,
                'message': 'Ya existe una persona con este DNI'
            }), 400
                
        # Creamos la nueva persona
        nueva_persona = Persona(
            DNI=data['DNI'],
            nombres=data['nombres'],
            apellido_paterno=data['apellido_paterno'],
            apellido_materno=data['apellido_materno'],
            direccion=data['direccion']
        )
        
        db.session.add(nueva_persona)
        db.session.flush()  # Para obtener el ID de la persona
        
        # Creamos la nueva beneficiaria
        nueva_beneficiaria = Beneficiaria(
            fk_tipo_beneficiaria=data['fk_tipo_beneficiaria'],
            fk_persona=nueva_persona.id_persona,
            estado=data.get('estado', True),
            cantidad_hijos=data.get('cantidad_hijos', 0),
            codigo_SISFOH=data.get('codigo_SISFOH')
        )
        
        db.session.add(nueva_beneficiaria)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Beneficiaria creada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al crear la beneficiaria'
        }), 500
        
# ruta para actualizar los datos de una beneficiaria
@beneficiarias.route('/api/beneficiarias/<int:id_beneficiaria>', methods=['PUT'])
def update_beneficiaria(id_beneficiaria):
    try:
        data = request.get_json()
        
        # Validamos que los datos requeridos estén presentes
        required_fields = ['DNI', 'nombres', 'apellido_paterno', 'apellido_materno', 'direccion', 'fk_tipo_beneficiaria']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }), 400
        
        # Buscamos la beneficiaria por ID
        beneficiaria = Beneficiaria.query.filter_by(id_beneficiaria=id_beneficiaria).first()
        if not beneficiaria:
            return jsonify({
                'success': False,
                'message': 'Beneficiaria no encontrada'
            }), 404
        
        # Buscamos la persona asociada a la beneficiaria
        persona = Persona.query.filter_by(id_persona=beneficiaria.fk_persona).first()
        
        # Actualizamos los datos de la persona
        persona.DNI = data['DNI']
        persona.nombres = data['nombres']
        persona.apellido_paterno = data['apellido_paterno']
        persona.apellido_materno = data['apellido_materno']
        persona.direccion = data['direccion']
        
        # Actualizamos los datos de la beneficiaria
        beneficiaria.fk_tipo_beneficiaria = data['fk_tipo_beneficiaria']
        beneficiaria.estado = data.get('estado', True)
        beneficiaria.cantidad_hijos = data.get('cantidad_hijos', 0)
        beneficiaria.codigo_SISFOH = data.get('codigo_SISFOH')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Beneficiaria actualizada exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al actualizar la beneficiaria'
        }), 500
       
# ruta para obtener una beneficiaria por el id 
@beneficiarias.route('/api/beneficiarias/<int:id_beneficiaria>', methods=['GET'])
def get_beneficiaria_by_id(id_beneficiaria):
    try:
        beneficiaria = db.session.query(Beneficiaria)\
            .join(Persona, Beneficiaria.fk_persona == Persona.id_persona)\
            .join(TipoBeneficiaria, Beneficiaria.fk_tipo_beneficiaria == TipoBeneficiaria.id_tipo_beneficiaria)\
            .filter(Beneficiaria.id_beneficiaria == id_beneficiaria)\
            .first()
        
        if not beneficiaria:
            return jsonify({
                'success': False,
                'message': 'Beneficiaria no encontrada'
            }), 404
        
        beneficiaria_data = {
            'id_beneficiaria': beneficiaria.id_beneficiaria,
            'estado': beneficiaria.estado,
            'estado_texto': 'Activa' if beneficiaria.estado else 'Inactiva',
            'cantidad_hijos': beneficiaria.cantidad_hijos,
            'codigo_SISFOH': beneficiaria.codigo_SISFOH,
            'fecha_registro': beneficiaria.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if beneficiaria.fecha_registro else None,
            'persona': {
                'id_persona': beneficiaria.persona.id_persona,
                'DNI': beneficiaria.persona.DNI,
                'nombres': beneficiaria.persona.nombres,
                'apellido_paterno': beneficiaria.persona.apellido_paterno,
                'apellido_materno': beneficiaria.persona.apellido_materno,
                'direccion': beneficiaria.persona.direccion,
                'nombre_completo': f"{beneficiaria.persona.nombres} {beneficiaria.persona.apellido_paterno} {beneficiaria.persona.apellido_materno}"
            },
            'tipo_beneficiaria': {
                'id_tipo_beneficiaria': beneficiaria.tipo_beneficiaria.id_tipo_beneficiaria,
                'tipo': beneficiaria.tipo_beneficiaria.tipo,
                'cantidad_raciones': beneficiaria.tipo_beneficiaria.cantidad_raciones
            }
        }
        
        return jsonify({
            'success': True,
            'data': beneficiaria_data,
            'message': 'Beneficiaria obtenida exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener la beneficiaria'
        }), 500