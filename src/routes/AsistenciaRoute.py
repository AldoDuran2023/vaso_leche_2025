from flask import Blueprint, request, jsonify
from src.models.Reunion import Reunion
from src.models.Asistencia import Asistencia
from src.models.Multa import Multa 
from src.models.TipoMulta import TipoMulta
from src.models.Beneficiaria import Beneficiaria
from src.models.Persona import Persona
from src.database.db import db
from datetime import date

asistencias = Blueprint('asistencias', __name__)

# Ruta para editar la asistencia de una beneficiaria
@asistencias.route('/api/asistencia/<int:id_asistencia>', methods=['PUT'])
def actualizar_asistencia(id_asistencia):
    try:
        data = request.json
        asistencia = Asistencia.query.get_or_404(id_asistencia)

        asistencia.presente = bool(data.get('presente', asistencia.presente))
        asistencia.justificacion_tardanza = data.get('justificacion_tardanza') or None

        # Verifica si debe crear multa basada en la asistencia
        crear_multa = False
        motivo = ""
        fk_tipo_multa = None
        monto_multa = 0.00

        if asistencia.presente is False:
            crear_multa = True
            motivo = "Inasistencia"
            fk_tipo_multa = 1  # ID del tipo de multa por inasistencia
            
        elif asistencia.presente is True and asistencia.justificacion_tardanza:
            crear_multa = True
            motivo = "Tardanza Justificada"
            fk_tipo_multa = 3  # ID del tipo de multa por tardanza

        if crear_multa and fk_tipo_multa:
            # Verificar que no exista ya una multa para esta asistencia
            multa_existente = Multa.query.filter(
                Multa.fk_beneficiaria == asistencia.fk_beneficiaria,
                Multa.observaciones.contains(f"Asistencia ID: {id_asistencia}")
            ).first()

            
            if not multa_existente:
                # Obtener el monto del tipo de multa
                tipo_multa = TipoMulta.query.get(fk_tipo_multa)
                if tipo_multa:
                    monto_multa = tipo_multa.monto
                else:
                    monto_multa = 10.00  # Monto por defecto si no se encuentra el tipo

                # Crear la nueva multa
                multa = Multa(
                    fk_beneficiaria=asistencia.fk_beneficiaria,
                    fk_tipo_multa=fk_tipo_multa,
                    monto=monto_multa,
                    fecha_multa=date.today(),
                    pagado=0,  # No pagada
                    fecha_pago=None,
                    observaciones=f"Generada por {motivo.lower()} - Asistencia ID: {id_asistencia} - {date.today().isoformat()}"
                )
                db.session.add(multa)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Asistencia actualizada correctamente",
            "multa_creada": crear_multa,
            "motivo": motivo if crear_multa else None
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error al actualizar la asistencia"
        }), 500


# Ruta para obtener todas las beneficiarias de una reunión específica
@asistencias.route('/api/reuniones/<int:id_reunion>', methods=['GET'])
def obtener_beneficiarias_por_reunion(id_reunion):
    try:
        # Verificar que la reunión existe
        reunion = Reunion.query.get(id_reunion)
        if not reunion:
            return jsonify({
                'success': False,
                'message': 'Reunión no encontrada'
            }), 404

        # Obtener asistencias de la reunión
        asistencias_reunion = db.session.query(Asistencia)\
            .join(Reunion, Asistencia.fk_reunion == Reunion.id_reunion)\
            .filter(Reunion.id_reunion == id_reunion)\
            .all()

        if not asistencias_reunion:
            return jsonify({
                'success': False,
                'message': 'No se encontraron beneficiarias para esta reunión'
            }), 404

        beneficiarias_data = []
        for asistencia in asistencias_reunion:
            beneficiaria = Beneficiaria.query.get(asistencia.fk_beneficiaria)
            persona = Persona.query.get(beneficiaria.fk_persona)
            
            # Verificar si tiene multas relacionadas con esta asistencia
            multas_asistencia = Multa.query.filter(
                Multa.fk_beneficiaria == beneficiaria.id_beneficiaria,
                Multa.observaciones.contains(f"Asistencia ID: {asistencia.id_asistencia}")
            ).all()

            beneficiarias_data.append({
                'id_asistencia': asistencia.id_asistencia,
                'id_beneficiaria': beneficiaria.id_beneficiaria,
                'nombre_completo': f"{persona.nombres} {persona.apellido_paterno} {persona.apellido_materno}",
                'presente': bool(asistencia.presente),
                'justificacion_tardanza': asistencia.justificacion_tardanza,
                'tiene_multas': len(multas_asistencia) > 0,
                'cantidad_multas': len(multas_asistencia),
                'monto_total_multas': sum(float(multa.monto) for multa in multas_asistencia if not multa.pagado)
            })

        return jsonify({
            'success': True,
            'data': beneficiarias_data,
            'reunion_info': {
                'id_reunion': reunion.id_reunion,
                'fecha': reunion.fecha.isoformat() if reunion.fecha else None,
                'lugar': reunion.lugar,
                'motivo': reunion.motivo
            },
            'total_beneficiarias': len(beneficiarias_data),
            'message': 'Lista de beneficiarias obtenida exitosamente'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener beneficiarias de la reunión'
        }), 500
