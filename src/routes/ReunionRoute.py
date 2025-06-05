from flask import Blueprint, request, jsonify
from src.models.Reunion import Reunion
from src.models.Beneficiaria import Beneficiaria
from src.models.Asistencia import Asistencia
from utils.paginador import paginar_query
from datetime import datetime
from src.database.db import db

reuniones = Blueprint('reuniones', __name__)

# ruta para devolver todas las reuniones 
@reuniones.route('/api/reuniones', methods=['GET'])
def get_reuniones():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        # Llamada al paginador
        resultado = paginar_query(
            query=Reunion.query.order_by(Reunion.fecha.desc()),
            page=page,
            per_page=per_page,
            route_name='reuniones.get_reuniones', 
            fields=['id_reunion', 'fecha', 'hora', 'lugar', 'motivo', 'estado_reunion']
        )

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ruta para insertar una nueva reunion
@reuniones.route('/api/reuniones/create', methods=['POST'])
def crear_reunion():
    data = request.json
    fecha = data.get('fecha')
    hora = data.get('hora')
    lugar = data.get('lugar')
    motivo = data.get('motivo')
    junta_id = data.get('fk_junta_directiva')

    # Crear la reunión
    nueva_reunion = Reunion(
        fecha=datetime.strptime(fecha, '%Y-%m-%d'),
        hora=datetime.strptime(hora, '%H:%M:%S'),
        lugar=lugar,
        motivo=motivo,
        fk_junta_directiva=junta_id
    )
    db.session.add(nueva_reunion)
    db.session.flush() 

    # Obtener todos los beneficiarios
    beneficiarios = Beneficiaria.query.filter(Beneficiaria.estado == 1).all();
    if not beneficiarios:
        return jsonify({
            "message": "No hay beneficiarias activas para generar la reunión"
        })

    # Crear asistencia para cada beneficiario
    for b in beneficiarios:
        asistencia = Asistencia(
            fk_beneficiaria=b.id_beneficiaria,
            fk_reunion=nueva_reunion.id_reunion,
            presente=True
        )
        db.session.add(asistencia)

    db.session.commit()
    return jsonify({"message": "Reunión y asistencias creadas correctamente"})

# Ruta para eliminar reuniones siempre y cuando no haya pasado la fecha
@reuniones.route('/api/reuniones/delete/<int:id_reunion>', methods=['DELETE'])
def eliminar_reunion(id_reunion):
    try:
        reunion = Reunion.query.get_or_404(id_reunion)

        # Verificar si la reunión ya ha pasado
        if reunion.fecha < datetime.now():
            return jsonify({
                'success': False,
                'message': 'No se puede eliminar una reunión que ya ha pasado'
            }), 400

        db.session.delete(reunion)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Reunión eliminada exitosamente'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al eliminar la reunión'
        }), 500
        
@reuniones.route('/api/reuniones/actualizar_estado/<int:id_reunion>', methods=['PUT'])
def actualizar_estado_reunion(id_reunion):
    try:
        reunion = Reunion.query.get_or_404(id_reunion)

        reunion.estado_reunion = 1 
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Estado de la reunión actualizado correctamente.'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error al actualizar el estado de la reunión.',
            'error': str(e)
        }), 500
