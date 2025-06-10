from flask import Blueprint, request, jsonify
from src.database.db import db
from datetime import datetime, date
from src.models.Movimiento import Movimiento
from src.models.Beneficiaria import Beneficiaria
from src.models.Representante import Representante
from src.models.JuntaDirectiva import JuntaDirectiva
from src.models.Gasto import Gasto
from src.models.Multa import Multa
from utils.paginador import paginar_query
from utils.export_tesoreria import export_to_excel_tesoreria, export_to_word_tesoreria, export_to_pdf_tesoreria
from src.models.Usuario import Usuario
from functionJWT import validate_token
from sqlalchemy import func

movimiento = Blueprint('movimientos', __name__)


def obtener_data_tesoreria_usuario(id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario or not usuario.representante:
        raise ValueError("Usuario no tiene representante asignado")

    representante = usuario.representante
    id_representante = representante.id_representante
    anio_junta = representante.junta_directiva.anio if representante.junta_directiva else '---'

    # 🔢 Ingresos (desde Movimiento)
    movimientos = Movimiento.query.filter_by(fk_representante=id_representante, tipo_movimiento='Ingreso').all()
    ingresos = [{
        'Descripción': m.descripcion or '---',
        'Monto': f"{m.monto:.2f}",
        'Fecha': m.fecha_movimiento.strftime('%d/%m/%Y')
    } for m in movimientos]
    total_ingresos = sum(m.monto for m in movimientos)

    # 💸 Gastos
    gastos = Gasto.query.filter_by(fk_representante=id_representante).all()
    gastos_list = [{
        'Motivo': g.motivo,
        'Monto': f"{g.monto:.2f}",
        'Fecha': g.fecha_gasto.strftime('%d/%m/%Y')
    } for g in gastos]
    total_gastos = sum(g.monto for g in gastos)

    return {
        'ingresos': ingresos,
        'gastos': gastos_list,
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'anio_junta': anio_junta
    }



# Rutas Para exportar datos de las movimiento
@movimiento.route('/api/movimiento/export/excel', methods=['GET'])
def export_tesoreria_excel():
    try:
        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({"message": "Token requerido"}), 403
        token = token_header.split(" ")[1]
        user_data = validate_token(token, output=True)

        data = obtener_data_tesoreria_usuario(user_data["id_usuario"])
        return export_to_excel_tesoreria(data)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@movimiento.route('/api/movimiento/export/word', methods=['GET'])
def export_tesoreria_word():
    try:
        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({"message": "Token requerido"}), 403
        token = token_header.split(" ")[1]
        user_data = validate_token(token, output=True)

        data = obtener_data_tesoreria_usuario(user_data["id_usuario"])
        return export_to_word_tesoreria(data)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@movimiento.route('/api/movimiento/export/pdf', methods=['GET'])
def export_tesoreria_pdf():
    try:
        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({"message": "Token requerido"}), 403
        token = token_header.split(" ")[1]
        user_data = validate_token(token, output=True)

        data = obtener_data_tesoreria_usuario(user_data["id_usuario"])
        return export_to_pdf_tesoreria(data)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Ruta para obtener todos los movimientos
@movimiento.route('/api/movimientos', methods=['GET'])
def obtener_movimientos():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = Movimiento.query.order_by(Movimiento.fecha_movimiento)
        fields = ['idMovimientos', 'monto', 'fecha_movimiento', 'fk_representante', 'fk_multa', 'tipo_movimiento', 'descripcion']

        resultado = paginar_query(query, page, per_page, 'movimientos.obtener_movimientos', fields)

        return jsonify({
            'success': True,
            'message': 'Movimientos obtenidos exitosamente',
            **resultado
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener los movimientos'
        }), 500

# Ruta para pagar multas
@movimiento.route('/api/multas/pagar-multiples/<int:fk_beneficiaria>', methods=['PUT'])
def pagar_multas_multiples(fk_beneficiaria):
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
        
        data = request.json
        ids_multas = data.get('ids_multas', [])
        fecha_pago = data.get('fecha_pago')  
        observacion_pago = data.get('observacion_pago', 'ninguna')
        fk_representante = representante.id_representante

        if not ids_multas:
            return jsonify({
                'success': False,
                'message': 'Debe proporcionar al menos una multa para pagar'
            }), 400

        if not fk_representante:
            return jsonify({
                'success': False,
                'message': 'Debe proporcionar el ID del representante que realiza el pago'
            }), 400

        multas = Multa.query.filter(
            Multa.id_multa.in_(ids_multas),
            Multa.fk_beneficiaria == fk_beneficiaria
        ).all()

        if len(multas) != len(ids_multas):
            return jsonify({
                'success': False,
                'message': 'Algunas multas no fueron encontradas o no pertenecen a la beneficiaria especificada'
            }), 404

        multas_ya_pagadas = [m for m in multas if m.pagado == 1]
        if multas_ya_pagadas:
            ids_pagadas = [str(m.id_multa) for m in multas_ya_pagadas]
            return jsonify({
                'success': False,
                'message': f'Las siguientes multas ya están pagadas: {", ".join(ids_pagadas)}'
            }), 400

        # Preparar fecha
        if fecha_pago:
            fecha_pago_obj = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
        else:
            fecha_pago_obj = date.today()

        multas_procesadas = []
        total_pagado = 0

        for multa in multas:
            multa.pagado = 1
            multa.fecha_pago = fecha_pago_obj

            if observacion_pago:
                if multa.observaciones:
                    multa.observaciones += f" | Pago múltiple: {observacion_pago}"
                else:
                    multa.observaciones = f"Pago múltiple: {observacion_pago}"

            # ✅ Registrar un movimiento por cada multa
            movimiento = Movimiento(
                monto=multa.monto,
                fecha_movimiento=fecha_pago_obj,
                fk_representante=fk_representante,
                fk_multa=multa.id_multa
            )
            
            movimiento.tipo_movimiento = 'Ingreso'  
            movimiento.descripcion = f'Pago de multa de benficiaria {fk_beneficiaria}'
            db.session.add(movimiento)

            total_pagado += float(multa.monto)
            multas_procesadas.append({
                'id_multa': multa.id_multa,
                'monto': float(multa.monto),
                'fecha_multa': multa.fecha_multa
            })

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Se pagaron exitosamente {len(multas)} multas para la beneficiaria {fk_beneficiaria}',
            'datos': {
                'beneficiaria_id': fk_beneficiaria,
                'multas_pagadas': len(multas),
                'total_pagado': total_pagado,
                'fecha_pago': fecha_pago_obj.isoformat(),
                'multas_procesadas': multas_procesadas
            }
        }), 200

    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Formato de fecha inválido. Use AAAA-MM-DD'
        }), 400
    except Exception as e:
        db.session.rollback()
        print('Error al procesar pago múltiple:', str(e))
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al procesar el pago de las multas'
        }), 500

@movimiento.route('/api/tesoreria/balance', methods=['GET'])
def obtener_balance_tesoreria():
    try:
        total_ingresos = db.session.query(func.sum(Movimiento.monto))\
            .filter(Movimiento.tipo_movimiento == 'Ingreso')\
            .scalar() or 0

        total_egresos = db.session.query(func.sum(Gasto.monto)).scalar() or 0

        balance = total_ingresos - total_egresos

        return jsonify({
            'success': True,
            'data': {
                'ingresos': float(total_ingresos),
                'egresos': float(total_egresos),
                'balance': float(balance)
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
