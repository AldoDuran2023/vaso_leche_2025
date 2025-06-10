from flask import Blueprint, request, jsonify
from src.models.Reunion import Reunion
from src.models.Beneficiaria import Beneficiaria
from src.models.Asistencia import Asistencia
from utils.paginador import paginar_query
from src.models.Usuario import Usuario
from functionJWT import validate_token
from datetime import datetime
from src.database.db import db
from utils.export_utils import export_to_excel, export_to_word, export_to_pdf

reuniones = Blueprint('reuniones', __name__)

def get_reuniones_data():
    reuniones = db.session.query(Reunion).all()
    
    data = []
    for idx, reunion in enumerate(reuniones, start=1):
        for asistencia in reunion.asistencias:
            persona = asistencia.beneficiaria.persona
            data.append({
                'N°': len(data) + 1,
                'Fecha de Reunión': reunion.fecha.strftime('%d/%m/%Y'),
                'Motivo': reunion.motivo,
                'Nombre Beneficiaria': f"{persona.nombres} {persona.apellido_paterno} {persona.apellido_materno}",
                'Presente': 'Sí' if asistencia.presente else 'No',
                'Justificación': asistencia.justificacion_tardanza or '---'
            })
    return data

# Rutas Para exportar datos de las reuniones
@reuniones.route('/api/reuniones/export/excel', methods=['GET'])
def export_excel():
    data = get_reuniones_data()
    return export_to_excel(data, "reuniones.xlsx")

@reuniones.route('/api/reuniones/export/word', methods=['GET'])
def export_word():
    data = get_reuniones_data()
    return export_to_word(data, "Reporte de reuniones", "reuniones.docx")

@reuniones.route('/api/reuniones/export/pdf', methods=['GET'])
def export_pdf():
    data = get_reuniones_data()
    return export_to_pdf(data, "Reporte de reuniones", "reuniones.pdf")

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

        # 📩 Datos del request
        data = request.get_json()
        fecha = data.get('fecha')
        hora = data.get('hora')
        lugar = data.get('lugar')
        motivo = data.get('motivo')

        # ✅ Crear reunión
        nueva_reunion = Reunion(
            fecha=datetime.strptime(fecha, '%Y-%m-%d'),
            hora=datetime.strptime(hora, '%H:%M:%S'),
            lugar=lugar,
            motivo=motivo,
            fk_junta_directiva=junta_id
        )
        db.session.add(nueva_reunion)
        db.session.flush()

        # 👥 Crear asistencias
        beneficiarios = Beneficiaria.query.filter_by(estado=1).all()
        for b in beneficiarios:
            asistencia = Asistencia(
                fk_beneficiaria=b.id_beneficiaria,
                fk_reunion=nueva_reunion.id_reunion,
                presente=True
            )
            db.session.add(asistencia)

        db.session.commit()
        return jsonify({"message": "Reunión y asistencias creadas correctamente"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

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
