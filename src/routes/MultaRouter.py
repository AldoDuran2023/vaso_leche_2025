from flask import Blueprint, jsonify, request
from src.models.Multa import Multa
from src.models.Beneficiaria import Beneficiaria
from utils.paginador import paginar_query
from datetime import date
from src.database.db import db
from sqlalchemy.orm import joinedload

multas = Blueprint('multas', __name__)

# Ruta para obtener todas las multas
@multas.route('/api/multas', methods=['GET'])
def obtener_todas_multas():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        query = db.session.query(Multa).options(joinedload(Multa.beneficiaria).joinedload(Beneficiaria.persona)).filter(Multa.pagado == 0).order_by(Multa.fecha_multa.desc())

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        multas_list = []
        for multa in paginated.items:
            persona = multa.beneficiaria.persona

            multas_list.append({
                'id_multa': multa.id_multa,
                'fk_beneficiaria': multa.fk_beneficiaria,
                'monto': float(multa.monto),
                'fecha_multa': multa.fecha_multa.isoformat(),
                'pagado': multa.pagado,
                'fecha_pago': multa.fecha_pago.isoformat() if multa.fecha_pago else None,
                'observaciones': multa.observaciones,
                'nombre_completo': f"{persona.nombres} {persona.apellido_paterno} {persona.apellido_materno}"
            })

        return jsonify({
            'success': True,
            'total': paginated.total,
            'page': paginated.page,
            'pages': paginated.pages,
            'per_page': paginated.per_page,
            'data': multas_list,
            'message': 'Multas obtenidas correctamente con datos personales.'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener las multas'
        }), 500

# Ruta para obtener una multa por su id_multa
@multas.route('/api/multa/<int:id_multa>', methods=['GET'])
def obtener_multa_por_id(id_multa):
    try:
        multa = Multa.query.get(id_multa)
        if not multa:
            return jsonify({
                'success': False,
                'message': 'Multa no encontrada'
            }), 404

        data = {
            'id_multa': multa.id_multa,
            'fk_beneficiaria': multa.fk_beneficiaria,
            'fk_tipo_multa': multa.fk_tipo_multa,
            'monto': float(multa.monto),
            'fecha_multa': multa.fecha_multa.isoformat() if multa.fecha_multa else None,
            'pagado': multa.pagado,
            'fecha_pago': multa.fecha_pago.isoformat() if multa.fecha_pago else None,
            'observaciones': multa.observaciones
        }

        return jsonify({
            'success': True,
            'data': data,
            'message': 'Multa obtenida exitosamente'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener la multa'
        }), 500


# Ruta para obtener multas de una beneficiaria específica
@multas.route('/api/multas/beneficiaria/<int:id_beneficiaria>', methods=['GET'])
def obtener_multas_beneficiaria(id_beneficiaria):
    try:
        solo_pendientes = request.args.get('pendientes', 'false').lower() == 'true'
        
        query = Multa.query.filter_by(fk_beneficiaria=id_beneficiaria, pagado=0) 
        if solo_pendientes:
            query = query.filter_by(pagado=0)
        
        multas = query.order_by(Multa.fecha_multa.desc()).all()

        total_pendiente = 0
        multas_pagadas = 0
        multas_pendientes = 0

        data = []

        for multa in multas:
            if not multa.pagado:
                total_pendiente += float(multa.monto)
                multas_pendientes += 1
            else:
                multas_pagadas += 1

            data.append({
                'id_multa': multa.id_multa,
                'fk_beneficiaria': multa.fk_beneficiaria,
                'fk_tipo_multa': multa.fk_tipo_multa,
                'monto': float(multa.monto),
                'fecha_multa': multa.fecha_multa.isoformat() if multa.fecha_multa else None,
                'pagado': multa.pagado,
                'fecha_pago': multa.fecha_pago.isoformat() if multa.fecha_pago else None,
                'observaciones': multa.observaciones
            })

        return jsonify({
            'success': True,
            'data': data,
            'resumen': {
                'total_multas': len(multas),
                'total_pendiente': total_pendiente,
                'multas_pagadas': multas_pagadas,
                'multas_pendientes': multas_pendientes
            },
            'message': 'Multas obtenidas exitosamente'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener las multas'
        }), 500

# Ruta para actualizar el estado de una multa (marcar como pagada)
@multas.route('/api/multa/<int:id_multa>', methods=['PUT'])
def pagar_multa(id_multa):
    try:
        data = request.json
        multa = Multa.query.get_or_404(id_multa)
        
        if multa.pagado:
            return jsonify({
                'success': False,
                'message': 'Esta multa ya está pagada'
            }), 400
        
        # Marcar como pagada
        fecha_pago = data.get('fecha_pago')
        if fecha_pago:
            from datetime import datetime
            multa.fecha_pago = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
        else:
            from datetime import date
            multa.fecha_pago = date.today()
            
        multa.pagado = 1
        
        # Actualizar observaciones si se proporciona
        observacion_pago = data.get('observacion_pago')
        if observacion_pago:
            multa.observaciones = (multa.observaciones or '') + f" | Pago: {observacion_pago}"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Multa marcada como pagada exitosamente',
            'multa': {
                'id': multa.id_multa,
                'monto': multa.monto,
                'fecha_pago': str(multa.fecha_pago) if multa.fecha_pago else None,
                'pagado': bool(multa.pagado),
                'observaciones': multa.observaciones
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al procesar el pago de la multa'
        }), 500

        
