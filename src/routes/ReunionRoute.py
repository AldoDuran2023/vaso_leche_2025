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
            route_name='reuniones.get_reuniones',  # Usa el nombre registrado de la ruta
            fields=['idReunion', 'fecha', 'hora_inicio', 'hora_fin', 'estado']
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
    db.session.flush()  # Para obtener el ID de la reunión antes del commit

    # Obtener todos los beneficiarios
    beneficiarios = Beneficiaria.query.all()

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