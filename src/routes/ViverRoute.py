from flask import Blueprint, request, jsonify
from src.models.TipoViver import TipoViveres
from src.models.Inventario import Inventario
from utils.paginador import paginar_query
from src.database.db import db

tipo_viveres = Blueprint('tipo_viveres', __name__)

# Ruta para obtener todos los tipos de víveres
@tipo_viveres.route('/api/tipo_viveres', methods=['GET'])
def listar_tipo_viveres():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = TipoViveres.query.order_by(TipoViveres.viver.asc())

        # Campos a devolver por cada tipo de víver
        fields = ['id_viver', 'viver', 'tipo_unidad', 'descripcion']

        resultado = paginar_query(query, page, per_page, 'tipo_viveres.listar_tipo_viveres', fields)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'message': 'Error al listar los tipos de víveres'}), 500

    
# Ruta para obtener un tipo de víveres por su ID
@tipo_viveres.route('/api/tipo_viveres/<int:id_viver>', methods=['GET'])
def obtener_tipo_viveres(id_viver):
    try:
        tipo = db.session.query(TipoViveres).filter_by(id_viver=id_viver).first()

        if not tipo:
            return jsonify({
                'success': False,
                'message': 'Tipo de víver no encontrado'
            }), 404

        tipo_viver_data = {
            'id_viver': tipo.id_viver,
            'viver': tipo.viver,
            'tipo_unidad': tipo.tipo_unidad,
            'descripcion': tipo.descripcion
        }

        return jsonify({
            'success': True,
            'data': tipo_viver_data,
            'message': 'Tipo de víver obtenido exitosamente'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener el tipo de víver'
        }), 500

    
# Crear un nuevo tipo de víveres
@tipo_viveres.route('/api/tipo_viveres', methods=['POST'])
def crear_tipo_viveres():
    data = request.json
    viver = data.get('viver')
    tipo_unidad = data.get('tipo_unidad')
    descripcion = data.get('descripcion')

    if not viver or not tipo_unidad:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        nuevo_tipo = TipoViveres(viver=viver, tipo_unidad=tipo_unidad, descripcion=descripcion)
        db.session.add(nuevo_tipo)
        db.session.commit()
        return jsonify({"message": "Tipo de víver creado correctamente", "id": nuevo_tipo.id_viver}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear el tipo de víver: {str(e)}"}), 500

# Actualizar un tipo de víveres
@tipo_viveres.route('/api/tipo_viveres/update/<int:id_viver>', methods=['PUT'])
def actualizar_tipo_viveres(id_viver):
    try:
        tipo = db.session.get(TipoViveres, id_viver)
        if not tipo:
            return jsonify({"error": "Tipo de víver no encontrado"}), 404

        data = request.json
        tipo.viver = data.get('viver', tipo.viver)
        tipo.tipo_unidad = data.get('tipo_unidad', tipo.tipo_unidad)
        tipo.descripcion = data.get('descripcion', tipo.descripcion)

        db.session.commit()
        return jsonify({"message": "Tipo de víver actualizado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar el tipo de víver: {str(e)}"}), 500

# Eliminar solo si no tiene inventario
@tipo_viveres.route('/api/tipo_viveres/delete/<int:id_viver>', methods=['DELETE'])
def eliminar_tipo_viveres(id_viver):
    try:
        tipo = db.session.get(TipoViveres, id_viver)
        if not tipo:
            return jsonify({"error": "Tipo de víver no encontrado"}), 404

        # Buscar el inventario asociado
        inventario = Inventario.query.filter_by(fk_tipo_viver=id_viver).first()

        if inventario and inventario.cantidad_total > 0:
            return jsonify({"error": "No se puede eliminar: tiene inventario mayor a 0"}), 400

        db.session.delete(tipo)
        db.session.commit()
        return jsonify({"message": "Tipo de víver eliminado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar el tipo de víver: {str(e)}"}), 500