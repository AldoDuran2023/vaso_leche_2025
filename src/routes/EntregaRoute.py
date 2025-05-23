from flask import Blueprint, request, jsonify
from utils.paginador import paginar_query
from src.models.Entrega import Entrega
from src.models.Beneficiaria import Beneficiaria
from src.models.DetalleEntrega import DetalleEntrega
from src.models.DetalleViverEntregado import DetalleViveresEntregados
from src.models.Inventario import Inventario
from src.database.db import db
from datetime import datetime

entregas = Blueprint('entregas', __name__)

# Ruta para obtener todos los registros de entregas
@entregas.route('/api/entregas', methods=['GET'])
def obetenr_entregas():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = Entrega.query.order_by(Entrega.fecha_entrega.desc()) 

        # Campos a devolver por cada gasto (ajusta según lo que necesites mostrar)
        fields = ['id_racion', 'fk_representante', 'fecha_entrega', 'estado']

        resultado = paginar_query(query, page, per_page, 'entregas.obetenr_entregas', fields)

        # Formatear fechas y montos si deseas mejor presentación
        for item in resultado['data']:
            item['fecha_entrega'] = item['fecha_entrega'].isoformat()

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'message': 'Error al listar los gastos'}), 500
        
# Ruta para insertar un nuevo registro de entrega
@entregas.route('/api/entregas/create', methods=['POST'])
def crear_entrega():
    try:
        data = request.get_json()
        fk_representante = data.get('fk_representante')
        fecha_entrega = data.get('fecha_entrega')
        estado = data.get('estado', 'Pendiente')

        nueva_entrega = Entrega(fk_representante, fecha_entrega, estado)
        db.session.add(nueva_entrega)
        db.session.commit()  # Necesario para tener el id_racion

        beneficiarias_activas = Beneficiaria.query.filter_by(estado=True).all()

        for beneficiaria in beneficiarias_activas:
            detalle = DetalleEntrega(
                fk_entrega=nueva_entrega.id_racion,
                fk_beneficiaria=beneficiaria.id_beneficiaria,
                cantidad_raciones=beneficiaria.cantidad_hijos,
                estado=False
            )
            db.session.add(detalle)
            db.session.flush()  # Para obtener el ID del detalle sin hacer commit

            # Determinar raciones según tipo
            tipo = beneficiaria.fk_tipo_beneficiaria
            raciones = beneficiaria.cantidad_hijos * (1 if tipo == 1 else 2 if tipo == 2 else 0)

            if raciones > 0:
                # ID de los víveres. Asegúrate que estos IDs estén bien
                ID_AVENA = 1
                ID_LECHE = 2

                # Crear los viveres por ración
                detalle_avena = DetalleViveresEntregados(
                    fk_detalle_entrega=detalle.id_detalle_entregas,
                    fk_tipo_viver=ID_AVENA,
                    cantidad=raciones * 1
                )
                detalle_leche = DetalleViveresEntregados(
                    fk_detalle_entrega=detalle.id_detalle_entregas,
                    fk_tipo_viver=ID_LECHE,
                    cantidad=raciones * 3
                )

                db.session.add_all([detalle_avena, detalle_leche])

        db.session.commit()

        return jsonify({'success': True, 'message': 'Entrega y víveres registrados correctamente'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

        
# Ruta Entrega de los viveres
@entregas.route('/api/detalle_entrega/<int:id>', methods=['PUT'])
def marcar_detalle_como_entregado(id):
    try:
        detalle = DetalleEntrega.query.get(id)
        if not detalle:
            return jsonify({'success': False, 'message': 'Detalle no encontrado'}), 404
        
        if detalle.estado:
            return jsonify({'success': False, 'message': 'Ya fue entregado'}), 400

        # Verificamos si hay stock suficiente antes de continuar
        for item in detalle.detalles_viveres:
            inventario = Inventario.query.filter_by(fk_tipo_viver=item.fk_tipo_viver).first()
            if not inventario or inventario.cantidad_total < item.cantidad:
                return jsonify({
                    'success': False,
                    'message': f'Sin stock suficiente de {item.tipo_viver.viver}. Stock disponible: {inventario.cantidad_total if inventario else 0}'
                }), 400

        # Si todo está OK, marcamos como entregado
        detalle.estado = True

        # Descontamos del inventario
        for item in detalle.detalles_viveres:
            inventario = Inventario.query.filter_by(fk_tipo_viver=item.fk_tipo_viver).first()
            inventario.cantidad_total -= item.cantidad
            inventario.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({'success': True, 'message': 'Entrega confirmada y stock actualizado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500



        