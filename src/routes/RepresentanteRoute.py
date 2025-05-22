from flask import Blueprint, request, jsonify
from src.models import Representante
from src.database.db import db
from datetime import date

representantes = Blueprint('representantes', __name__)

# Ruta para registrar un nuevo representante
@representantes.route('/api/representantes', methods=['POST'])
def registrar_representante():
    try:
        data = request.get_json()

        fk_cargo = data.get('fk_cargo')
        fk_beneficiaria = data.get('fk_beneficiaria')
        fk_junta_directiva = data.get('fk_junta_directiva')
        fecha_registro = data.get('fecha_registro')

        if not (fk_cargo and fk_beneficiaria and fk_junta_directiva and fecha_registro):
            return jsonify({
                'success': False,
                'message': 'Todos los campos son obligatorios: fk_cargo, fk_beneficiaria, fk_junta_directiva, fecha_registro'
            }), 400

        # Validar que no haya otro representante activo con el mismo cargo en la misma junta
        cargo_existente = Representante.query.filter_by(
            fk_junta_directiva=fk_junta_directiva,
            fk_cargo=fk_cargo,
            estado=True
        ).first()

        if cargo_existente:
            return jsonify({
                'success': False,
                'message': 'Ya existe un representante con ese cargo en esta junta directiva'
            }), 409

        # Validar que la beneficiaria no tenga ya un cargo activo en la misma junta
        beneficiaria_existente = Representante.query.filter_by(
            fk_junta_directiva=fk_junta_directiva,
            fk_beneficiaria=fk_beneficiaria,
            estado=True
        ).first()

        if beneficiaria_existente:
            return jsonify({
                'success': False,
                'message': 'Esta beneficiaria ya tiene un cargo activo en esta junta directiva'
            }), 409

        # Crear nuevo representante
        nuevo_representante = Representante(
            fk_cargo=fk_cargo,
            fk_beneficiaria=fk_beneficiaria,
            fk_junta_directiva=fk_junta_directiva,
            fecha_registro=date.fromisoformat(fecha_registro)
        )

        db.session.add(nuevo_representante)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Representante registrado correctamente'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al registrar el representante'
        }), 500
