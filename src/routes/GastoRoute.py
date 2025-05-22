from flask import Blueprint, request, jsonify
from src.models.Gasto import Gasto
from src.database.db import db
from datetime import datetime
from utils.paginador import paginar_query

gastos = Blueprint('gastos', __name__)

# Ruta para obetenr todos los gastos
@gastos.route('/api/gastos', methods=['GET'])
def listar_gastos():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = Gasto.query.order_by(Gasto.fecha_gasto.desc()) 

        # Campos a devolver por cada gasto (ajusta según lo que necesites mostrar)
        fields = ['idGastos', 'motivo', 'fecha_gasto', 'monto', 'fk_representante']

        resultado = paginar_query(query, page, per_page, 'gastos.listar_gastos', fields)

        # Formatear fechas y montos si deseas mejor presentación
        for item in resultado['data']:
            item['fecha_gasto'] = item['fecha_gasto'].isoformat()
            item['monto'] = float(item['monto'])

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'message': 'Error al listar los gastos'}), 500
    
# Ruta para Registrar un nuevo gasto
@gastos.route('/api/gastos', methods=['POST'])
def registrar_gasto():
    try:
        data = request.get_json()
        motivo = data.get('motivo')
        fecha_gasto = data.get('fecha_gasto')
        monto = data.get('monto')
        fk_representante = data.get('fk_representante')

        if not (motivo and fecha_gasto and monto and fk_representante):
            return jsonify({'success': False, 'message': 'Faltan campos obligatorios'}), 400

        nuevo_gasto = Gasto(
            motivo=motivo,
            fecha_gasto=datetime.fromisoformat(fecha_gasto),
            monto=monto,
            fk_representante=fk_representante
        )

        db.session.add(nuevo_gasto)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Gasto registrado correctamente'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'error': str(e), 
            'message': 'Error al registrar gasto'
            }), 500


# Ruta para Actualizar un gasto existente
@gastos.route('/api/gastos/<int:id>', methods=['PUT'])
def actualizar_gasto(id):
    try:
        gasto = Gasto.query.get_or_404(id)
        data = request.get_json()

        gasto.motivo = data.get('motivo', gasto.motivo)
        gasto.fecha_gasto = datetime.fromisoformat(data.get('fecha_gasto')) if data.get('fecha_gasto') else gasto.fecha_gasto
        gasto.monto = data.get('monto', gasto.monto)
        gasto.fk_representante = data.get('fk_representante', gasto.fk_representante)

        db.session.commit()

        return jsonify({
            'success': True, 
            'message': 'Gasto actualizado correctamente'
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'error': str(e), 
            'message': 'Error al actualizar gasto'
            }), 500


# Ruta para Obtener detalle de gasto por ID
@gastos.route('/api/gastos/<int:id>', methods=['GET'])
def obtener_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    return jsonify({
        'idGastos': gasto.idGastos,
        'motivo': gasto.motivo,
        'fecha_gasto': gasto.fecha_gasto.isoformat(),
        'monto': float(gasto.monto),
        'fk_representante': gasto.fk_representante
    }), 200
