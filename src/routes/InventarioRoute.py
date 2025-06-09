from flask import Blueprint, request, jsonify
from src.models.Inventario import Inventario
from utils.paginador import paginar_query
from src.models.TipoViver import TipoViveres

inventarios_bp = Blueprint('inventarios', __name__)

@inventarios_bp.route('/api/inventarios', methods=['GET'])
def listar_inventarios():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = Inventario.query.order_by(Inventario.fecha_actualizacion.desc())

        # Campos que quieres devolver
        fields = ['id_inventario', 'fk_tipo_viver', 'cantidad_total', 'fecha_actualizacion']

        resultado = paginar_query(query, page, per_page, 'inventarios.listar_inventarios', fields)

        # Formatear fechas
        for item in resultado['data']:
            item['fecha_actualizacion'] = item['fecha_actualizacion'].isoformat()

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error al listar los inventarios"
        }), 500

# Ruta para obtener todos los tipos de viveres
@inventarios_bp.route('/api/tipo_viveres', methods=['GET']) # Added leading slash for consistency
def listar_tipo_viveres():
    try:
        tipo_viveres = TipoViveres.query.all() # Changed this line
        
        result = [
            {
                "id": tv.id_viver, # Changed to id_viver based on your model
                "nombre": tv.viver,
                "unidad": tv.tipo_unidad
            } for tv in tipo_viveres
        ]
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error al listar los tipos de víveres"
        }), 500