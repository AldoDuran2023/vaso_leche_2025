from flask import Blueprint, jsonify
from src.database.db import db
from src.models.Cargo import Cargo  

cargos_bp = Blueprint('cargos', __name__)

@cargos_bp.route('/api/cargos', methods=['GET'])
def get_cargos():
    try:
        cargos = Cargo.query.all()
        cargos_data = [
            {
                'id_cargo': cargo.id_cargo,
                'cargo': cargo.cargo,
                'deberes': cargo.deberes
            }
            for cargo in cargos
        ]
        return jsonify({
            'success': True,
            'data': cargos_data,
            'total': len(cargos_data),
            'message': 'Cargos obtenidos exitosamente'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
