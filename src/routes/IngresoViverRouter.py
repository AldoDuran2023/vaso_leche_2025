from flask import Blueprint, request, jsonify
from src.database.db import db
from src.models.IngresoViver import IngresoViveres
from src.models.DetalleIngresoViver import DetalleIngresoViveres
from src.models.Inventario import Inventario
from src.models.TipoViver import TipoViveres
from datetime import datetime
from sqlalchemy import func, desc
from src.models.Usuario import Usuario
from functionJWT import validate_token

ingresos_viveres = Blueprint('ingresos_viveres', __name__)

# Ruta para ingresar nuevos viveres
@ingresos_viveres.route('/api/ingresos_viveres', methods=['POST'])
def registrar_ingreso_viveres():
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
        junta_id = representante.fk_junta_directiva
        
        data = request.json
        ingreso = IngresoViveres(
            fecha_ingreso=datetime.utcnow(),
            responsable=data['responsable'],
            fk_junta_directiva= junta_id
        )
        db.session.add(ingreso)
        db.session.flush()  

        for item in data['detalles']:
            cantidad = int(item['cantidad'])
            fk_tipo_viver = int(item['fk_tipo_viver'])

            detalle = DetalleIngresoViveres(
                fk_ingreso_viver=ingreso.idIngreso_Viveres,
                fk_tipo_viver=fk_tipo_viver,
                cantidad=cantidad
            )
            db.session.add(detalle)

            # Actualizar inventario
            inventario = Inventario.query.filter_by(fk_tipo_viver=fk_tipo_viver).first()
            if inventario:
                inventario.cantidad_total += cantidad
                inventario.fecha_actualizacion = datetime.utcnow()
            else:
                nuevo = Inventario(
                    fk_tipo_viver=fk_tipo_viver,
                    cantidad_total=cantidad
                )
                db.session.add(nuevo)

        db.session.commit()
        return jsonify({"success": True, "message": "Ingreso de víveres registrado correctamente."}), 201

    except Exception as e:
        db.session.rollback()
        print('Error al registrar ingreso:', str(e)) 
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

        subquery = db.session.query(
            IngresoViveres.idIngreso_Viveres.label('id'),
            IngresoViveres.fecha_ingreso.label('fecha'),
            IngresoViveres.responsable.label('responsable'),
            func.group_concat(
                func.concat(TipoViveres.viver, ' ', DetalleIngresoViveres.cantidad, ' unidades')
            ).label('detalles_de_entrega')
        ).join(DetalleIngresoViveres, IngresoViveres.idIngreso_Viveres == DetalleIngresoViveres.fk_ingreso_viver) \
         .join(TipoViveres, DetalleIngresoViveres.fk_tipo_viver == TipoViveres.id_viver) \
         .group_by(IngresoViveres.idIngreso_Viveres, IngresoViveres.fecha_ingreso, IngresoViveres.responsable) \
         .order_by(desc(IngresoViveres.fecha_ingreso)) \
         .subquery()

        total = db.session.query(func.count()).select_from(subquery).scalar()
        resultados = db.session.query(subquery).offset((page - 1) * per_page).limit(per_page).all()

        ingresos_list = []
        for row in resultados:
            ingresos_list.append({
                "id": row.id,
                "fecha": row.fecha.isoformat(),
                "responsable": row.responsable,
                "detalles_de_entrega": row.detalles_de_entrega
            })

        return jsonify({
            "success": True,
            "page": page,
            "per_page": per_page,
            "total": total,
            "data": ingresos_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error al obtener los ingresos de víveres"
        }), 500