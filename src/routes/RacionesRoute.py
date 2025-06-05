from flask import Blueprint, request, jsonify
from src.models.Entrega import Entrega
from src.models.Beneficiaria import Beneficiaria
from src.models.DetalleEntrega import DetalleEntrega
from src.models.DetalleViverEntregado import DetalleViveresEntregados
from src.models.Persona import Persona
from src.models.TipoViver import TipoViveres
from src.models.Inventario import Inventario
from sqlalchemy.sql import func, case
from src.database.db import db

detalle_entregas = Blueprint('detalle_entregas', __name__)

@detalle_entregas.route('/api/detalle_entregas/<int:id_entrega>', methods=['GET'])
def obtener_detalle_entrega(id_entrega):
    results = db.session.query(
        DetalleEntrega.fk_entrega,
        Persona.DNI,
        func.concat(Persona.apellido_paterno, ' ', Persona.apellido_materno, ' ', Persona.nombres).label('nombres'),
        DetalleEntrega.cantidad_raciones,
        case((DetalleEntrega.estado == True, 'Entregado'), else_='Pendiente').label('estado'),
        func.group_concat(
            func.concat(TipoViveres.viver, ' (', DetalleViveresEntregados.cantidad, ')')
        ).label('descripcion')
    ).join(
        DetalleEntrega.beneficiaria
    ).join(
        Persona, Beneficiaria.persona
    ).join(
        DetalleEntrega.detalles_viveres
    ).join(
        TipoViveres, DetalleViveresEntregados.tipo_viver
    ).filter(
        DetalleEntrega.fk_entrega == id_entrega
    ).group_by(
        DetalleEntrega.fk_entrega,
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
            "fk_entrega": row.fk_entrega,
            "dni": row.DNI,
            "nombres": row.nombres,
            "raciones": row.cantidad_raciones,
            "estado": row.estado,
            "descripcion": row.descripcion
        })

    return jsonify({
        "message": 'Datos obtenidos exitosamente',
        "data": formatted_results
    })

# Ruta para actualizar el estado de una detalle entrega y actualizar el stock del tipo de viveres
@detalle_entregas.route('/api/detalle_entregas/<int:id_detalle>', methods=['PUT'])
def actualizar_detalle_entrega(id_detalle):
    data = request.get_json()
    estado = data.get('estado')

    if estado not in [True, False]:
        return jsonify({"message": "Estado inválido. Debe ser True o False"}), 400

    detalle_entrega = DetalleEntrega.query.get(id_detalle)
    if not detalle_entrega:
        return jsonify({"message": f"No se encontró el detalle de entrega con ID {id_detalle}"}), 404

    # Si ya fue actualizado previamente como entregado, no restar el stock nuevamente
    if detalle_entrega.estado == True and estado == True:
        return jsonify({"message": "La entrega ya fue registrada como entregada"}), 400

    # Actualizar estado
    detalle_entrega.estado = estado
    db.session.add(detalle_entrega)

    # Si se está marcando como entregado, descontar del inventario
    if estado:
        detalles_viveres = DetalleViveresEntregados.query.filter_by(fk_detalle_entrega=id_detalle).all()
        for detalle in detalles_viveres:
            inventario = Inventario.query.filter_by(fk_tipo_viver=detalle.fk_tipo_viver).first()
            if inventario:
                if inventario.cantidad_total < detalle.cantidad:
                    return jsonify({"message": f"Stock insuficiente para {detalle.fk_tipo_viver}"}), 400
                inventario.cantidad_total -= detalle.cantidad
                db.session.add(inventario)

    db.session.commit()

    return jsonify({"message": "Estado de entrega actualizado y stock ajustado correctamente"})
