from flask import Blueprint, request, jsonify
from src.models.Entrega import Entrega
from src.models.Beneficiaria import Beneficiaria
from src.models.DetalleEntrega import DetalleEntrega
from src.models.DetalleViverEntregado import DetalleViveresEntregados
from src.models.Persona import Persona
from src.models.TipoViver import TipoViveres
from src.models.Inventario import Inventario
from src.models.Multa import Multa
from sqlalchemy.sql import func, case
from src.database.db import db

detalle_entregas = Blueprint('detalle_entregas', __name__)

# Ruta para obtener los detalles de una entrega especifica
@detalle_entregas.route('/api/detalle_entregas/<int:id_entrega>', methods=['GET'])
def obtener_detalle_entrega(id_entrega):

    results = db.session.query(
        DetalleEntrega.id_detalle_entregas,
        DetalleEntrega.fk_entrega,
        Beneficiaria.id_beneficiaria,
        Persona.DNI,
        func.concat(Persona.apellido_paterno, ' ', Persona.apellido_materno, ' ', Persona.nombres).label('nombres'),
        DetalleEntrega.cantidad_raciones,
        case((DetalleEntrega.estado == True, 'Entregado'), else_='Pendiente').label('estado'),
        func.group_concat(
            func.concat(TipoViveres.viver, ' (', DetalleViveresEntregados.cantidad, ')')
        ).label('descripcion'),
        # Solo contar multas no pagadas (asumiendo que el campo se llama 'pagado' o 'estado')
        func.count(case((Multa.pagado == False, Multa.id_multa), else_=None)).label('cantidad_multas_pendientes')
    ).join(
        DetalleEntrega.beneficiaria
    ).join(
        Persona, Beneficiaria.persona
    ).join(
        DetalleEntrega.detalles_viveres
    ).join(
        TipoViveres, DetalleViveresEntregados.tipo_viver
    ).outerjoin(
        Multa, Multa.fk_beneficiaria == Beneficiaria.id_beneficiaria
    ).filter(
        DetalleEntrega.fk_entrega == id_entrega
    ).group_by(
        DetalleEntrega.id_detalle_entregas,
        DetalleEntrega.fk_entrega,
        Beneficiaria.id_beneficiaria,
        Persona.DNI,
        Persona.apellido_paterno,
        Persona.apellido_materno,
        Persona.nombres,
        DetalleEntrega.cantidad_raciones,
        DetalleEntrega.estado
    ).all()

    if not results:
        return jsonify({"message": f"No se encontraron detalles para la entrega con ID {id_entrega}"}), 404

    formatted_results = []
    for row in results:
        formatted_results.append({
            "id_detalle_entregas": row.id_detalle_entregas,
            "fk_entrega": row.fk_entrega,
            "id_beneficiaria": row.id_beneficiaria,
            "dni": row.DNI,
            "nombres": row.nombres,
            "raciones": row.cantidad_raciones,
            "estado": row.estado,
            "descripcion": row.descripcion,
            "cantidad_multas_pendientes": row.cantidad_multas_pendientes
        })

    return jsonify({
        "message": 'Datos obtenidos exitosamente',
        "data": formatted_results
    })


@detalle_entregas.route('/api/detalle_entregas/<int:id_detalle>', methods=['PUT'])
def actualizar_detalle_entrega(id_detalle):
    try:
        data = request.get_json()
        estado = data.get('estado')

        if estado not in [True, False]:
            return jsonify({"message": "Estado inválido. Debe ser True o False"}), 400

        detalle_entrega = DetalleEntrega.query.get(id_detalle)
        if not detalle_entrega:
            return jsonify({"message": f"No se encontró el detalle de entrega con ID {id_detalle}"}), 404

        # Si ya fue entregado y se intenta volver a entregar
        if detalle_entrega.estado and estado:
            return jsonify({"message": "Esta entrega ya fue registrada como entregada"}), 400

        # Si se está entregando por primera vez, actualizar stock
        if estado and not detalle_entrega.estado:
            detalles_viveres = DetalleViveresEntregados.query.filter_by(fk_detalle_entrega=id_detalle).all()
            for detalle in detalles_viveres:
                inventario = Inventario.query.filter_by(fk_tipo_viver=detalle.fk_tipo_viver).first()
                if not inventario:
                    return jsonify({"message": f"No hay inventario para el tipo de víveres ID {detalle.fk_tipo_viver}"}), 404

                if inventario.cantidad_total < detalle.cantidad:
                    return jsonify({"message": f"Stock insuficiente para el tipo de víveres ID {detalle.fk_tipo_viver}"}), 400

                inventario.cantidad_total -= detalle.cantidad
                db.session.add(inventario)

        # Actualizar estado del detalle
        detalle_entrega.estado = estado
        db.session.add(detalle_entrega)
        db.session.commit()

        return jsonify({"message": "Estado de entrega actualizado y stock ajustado correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error interno del servidor", "error": str(e)}), 500

