from flask import Blueprint, request, jsonify
from src.database.db import db
from datetime import datetime, date
from src.models.Movimiento import Movimiento
from src.models.Multa import Multa
from utils.paginador import paginar_query

movimiento = Blueprint('movimientos', __name__)

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

# Ruta para registrar un nuevo movimiento
@movimiento.route('/api/movimientos', methods=['POST'])
def registrar_movimiento():
    try:
        data = request.json

        monto = data.get('monto')
        fecha_movimiento = data.get('fecha_movimiento')
        fk_representante = data.get('fk_representante')
        fk_multa = data.get('fk_multa')  # opcional
        tipo_movimiento = data.get('tipo_movimiento', 'Ingreso')
        descripcion = data.get('descripcion', '')

        if not all([monto, fecha_movimiento, fk_representante]):
            return jsonify({
                'success': False,
                'message': 'Faltan campos obligatorios (monto, fecha_movimiento, fk_representante)'
            }), 400

        fecha_movimiento = datetime.strptime(fecha_movimiento, '%Y-%m-%d').date()

        nuevo_mov = Movimiento(
            monto=monto,
            fecha_movimiento=fecha_movimiento,
            fk_representante=fk_representante,
            fk_multa=fk_multa
        )
        nuevo_mov.tipo_movimiento = tipo_movimiento
        nuevo_mov.descripcion = descripcion

        db.session.add(nuevo_mov)

        # Si tiene multa, marcarla como pagada
        if fk_multa:
            multa = Multa.query.get(fk_multa)
            if multa:
                multa.pagado = 1
                multa.fecha_pago = fecha_movimiento
                if multa.observaciones:
                    multa.observaciones += f" | Pago automático por movimiento"
                else:
                    multa.observaciones = "Pago automático por movimiento"

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Movimiento registrado correctamente',
            'movimiento': {
                'idMovimientos': nuevo_mov.idMovimientos,
                'monto': float(nuevo_mov.monto),
                'fecha_movimiento': nuevo_mov.fecha_movimiento.isoformat(),
                'fk_representante': nuevo_mov.fk_representante,
                'fk_multa': nuevo_mov.fk_multa,
                'tipo_movimiento': nuevo_mov.tipo_movimiento,
                'descripcion': nuevo_mov.descripcion
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al registrar el movimiento'
        }), 500