from flask import Blueprint, request, jsonify
from src.models.Representante import Representante
from src.models.Persona import Persona
from src.models.Beneficiaria import Beneficiaria
from src.models.Cargo import Cargo
from src.models.JuntaDirectiva import JuntaDirectiva # Asegúrate de que este modelo esté correctamente definido y relacionado
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

# Ruta para obtener representantes activas con datos personales
@representantes.route('/api/representantes/activas', methods=['GET'])
def obtener_representantes_activas():
    try:
        representantes_activos = Representante.query.filter_by(estado=True).all()

        resultado = []
        for rep in representantes_activos:
            persona = rep.beneficiaria.persona
            cargo = rep.cargo
            # Asegúrate de que 'rep.junta_directiva' esté correctamente relacionado y tenga un atributo 'nombre'
            junta_directiva_nombre = rep.junta_directiva.anio if rep.junta_directiva else None
            resultado.append({
                'id': rep.id_representante,
                'fecha_registro': rep.fecha_registro.isoformat(),
                'cargo': cargo.cargo,
                'estado': rep.estado,
                'junta_directiva': junta_directiva_nombre, # <-- ¡Aquí ya se está añadiendo el nombre de la junta!
                'beneficiaria': {
                    'dni': persona.DNI,
                    'nombres': persona.nombres,
                    'apellido_paterno': persona.apellido_paterno,
                    'apellido_materno': persona.apellido_materno,
                    'direccion': persona.direccion,
                }
            })

        return jsonify({
            'success': True,
            'data': resultado
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener las representantes activas'
        }), 500

