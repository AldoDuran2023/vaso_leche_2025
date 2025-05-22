from flask import Blueprint, request, jsonify
from src.models.JuntaDirectiva import JuntaDirectiva
from utils.paginador import paginar_query  
from src.database.db import db

juntas_directivas = Blueprint('juntas_directivas', __name__)

# Ruta para obtener todas las juntas directivas paginadas
@juntas_directivas.route('/api/juntas_directivas', methods=['GET'])
def get_juntas_directivas():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        # Llamada al paginador
        resultado = paginar_query(
            query=JuntaDirectiva.query.order_by(JuntaDirectiva.anio.desc()),
            page=page,
            per_page=per_page,
            route_name='juntas_directivas.get_juntas_directivas',  # Usa el nombre registrado de la ruta
            fields=['idJuntas_Directivas', 'anio', 'fecha_inicio', 'fecha_fin', 'estado']
        )

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ruta para insertar una nueva junta directiva
@juntas_directivas.route('/api/juntas_directivas', methods=['POST'])
def crear_junta_directiva():
    try:
        data = request.get_json()

        # Validación básica
        anio = data.get('anio')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin', None)  # Puede ser opcional
        estado = data.get('estado', 'Activa')    # Por defecto 'Activa'

        if not anio or not fecha_inicio:
            return jsonify({'error': 'Faltan campos obligatorios (anio, fecha_inicio).'}), 400

        nueva_junta = JuntaDirectiva(
            anio=anio,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=estado
        )

        db.session.add(nueva_junta)
        db.session.commit()

        return jsonify({
            'success': True,
            'mensaje': 'Junta directiva creada exitosamente.'
            }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500