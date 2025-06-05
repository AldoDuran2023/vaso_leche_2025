from flask import Blueprint, request, jsonify
from src.database.db import db
from src.models.IngresoViver import IngresoViveres
from src.models.DetalleIngresoViver import DetalleIngresoViveres
from src.models.Inventario import Inventario
from datetime import datetime
from utils.paginador import paginar_query

ingresos_viveres = Blueprint('ingresos_viveres', __name__)

# Ruta para ingresar nuevos viveres
@ingresos_viveres.route('/api/ingresos_viveres', methods=['POST'])
def registrar_ingreso_viveres():
    try:
        data = request.json
        ingreso = IngresoViveres(
            fecha_ingreso=datetime.strptime(data['fecha_ingreso'], '%Y-%m-%d').date(),
            responsable=data['responsable'],
            fk_junta_directiva=data['fk_junta_directiva']
        )
        db.session.add(ingreso)
        db.session.flush()  # Necesario para obtener el idIngreso_Viveres

        for item in data['detalles']:
            detalle = DetalleIngresoViveres(
                fk_ingreso_viver=ingreso.idIngreso_Viveres,
                fk_tipo_viver=item['fk_tipo_viver'],
                cantidad=item['cantidad']
            )
            db.session.add(detalle)

            # Actualizar inventario
            inventario = Inventario.query.filter_by(fk_tipo_viver=item['fk_tipo_viver']).first()
            if inventario:
                inventario.cantidad_total += item['cantidad']
                inventario.fecha_actualizacion = datetime.utcnow()
            else:
                nuevo = Inventario(
                    fk_tipo_viver=item['fk_tipo_viver'],
                    cantidad_total=item['cantidad']
                )
                db.session.add(nuevo)

        db.session.commit()
        return jsonify({"success": True, "message": "Ingreso de víveres registrado correctamente."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e), "message": "Error al registrar ingreso de víveres"}), 500

# Ruta para obtener los detalles del ingreso de los viveres por id
@ingresos_viveres.route('/api/ingresos_viveres/<int:id>', methods=['GET'])
def obtener_ingreso_viveres(id):
    try:
        ingreso = IngresoViveres.query.get_or_404(id)

        detalles = [
            {
                "id_detalle_ingreso": d.id_detalle_ingreso,
                "cantidad": d.cantidad,
                "tipo_viver": {
                    "id": d.fk_tipo_viver,
                    "nombre": d.tipo_viver.viver,
                    "unidad": d.tipo_viver.tipo_unidad
                }
            }
            for d in ingreso.detalle_ingresos
        ]

        result = {
            "idIngreso_Viveres": ingreso.idIngreso_Viveres,
            "fecha_ingreso": ingreso.fecha_ingreso.isoformat(),
            "responsable": ingreso.responsable,
            "junta_directiva": {
                "id": ingreso.fk_junta_directiva,
                "anio": ingreso.junta_directiva.anio
            },
            "detalles": detalles
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "message": "Error al obtener ingreso de víveres"}), 500


# Ruta para ver todos los ingresos de viveres
@ingresos_viveres.route('/api/ingresos_viveres', methods=['GET'])
def obtener_ingresos_viveres():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        pagination = IngresoViveres.query \
            .join(IngresoViveres.junta_directiva) \
            .order_by(IngresoViveres.fecha_ingreso.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

        ingresos_list = []
        for ingreso in pagination.items:
            ingresos_list.append({
                "idIngreso_Viveres": ingreso.idIngreso_Viveres,
                "fecha_ingreso": ingreso.fecha_ingreso.isoformat(),
                "responsable": ingreso.responsable,
                "junta_directiva": {
                    "id": ingreso.fk_junta_directiva,
                    "anio": ingreso.junta_directiva.anio
                }
            })

        return jsonify({
            "success": True,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "ingresos": ingresos_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error al obtener los ingresos de víveres"
        }), 500