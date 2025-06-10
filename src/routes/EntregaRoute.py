from flask import Blueprint, request, jsonify
from utils.paginador import paginar_query
from src.models.Entrega import Entrega
from src.models.Beneficiaria import Beneficiaria
from src.models.DetalleEntrega import DetalleEntrega
from src.models.DetalleViverEntregado import DetalleViveresEntregados
from src.models.Multa import Multa
from src.models.TipoMulta import TipoMulta
from src.models.Inventario import Inventario
from src.models.TipoViver import TipoViveres
from src.models.Representante import Representante
from src.models.JuntaDirectiva import JuntaDirectiva
from src.database.db import db
from datetime import datetime
from src.models.Usuario import Usuario
from functionJWT import validate_token
from sqlalchemy.orm import load_only
from utils.export_utils import export_to_excel, export_to_word, export_to_pdf


entregas = Blueprint('entregas', __name__)

def get_reparticiones_data():
    entregas = db.session.query(Entrega).join(Entrega.representante).join(Representante.beneficiaria).join(Beneficiaria.persona).all()
    data = []

    for e in entregas:
        for detalle in e.detalle_entregas: 
            persona = detalle.beneficiaria.persona
            data.append({
                'N°': len(data) + 1,
                'Fecha de Entrega': e.fecha_entrega.strftime('%d/%m/%Y'),
                'Representante': f"{e.representante.beneficiaria.persona.nombres} {e.representante.beneficiaria.persona.apellido_paterno} {e.representante.beneficiaria.persona.apellido_materno}",
                'Junta Directiva': e.representante.junta_directiva.anio,
                'Beneficiaria': f"{persona.nombres} {persona.apellido_paterno} {persona.apellido_materno}",
                'Cantidad Raciones': detalle.cantidad_raciones,
                'Estado': 'Recibido' if detalle.estado else 'Pendiente'
            })
    return data


# Rutas Para exportar datos de las entregas
@entregas.route('/api/entregas/export/excel', methods=['GET'])
def export_excel():
    data = get_reparticiones_data()
    return export_to_excel(data, "entregas.xlsx")

@entregas.route('/api/entregas/export/word', methods=['GET'])
def export_word():
    data = get_reparticiones_data()
    return export_to_word(data, "Reporte de entregas", "entregas.docx")

@entregas.route('/api/entregas/export/pdf', methods=['GET'])
def export_pdf():
    data = get_reparticiones_data()
    return export_to_pdf(data, "Reporte de entregas", "entregas.pdf")

# Ruta para obtener todas las entregas 
@entregas.route('/api/entregas', methods=['GET'])
def obetenr_entregas():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Realiza join con Representante y JuntaDirectiva
        query = db.session.query(
            Entrega.id_racion,
            Entrega.fecha_entrega,
            Entrega.estado,
            Representante.id_representante,
            JuntaDirectiva.anio.label("junta_anio")
        ).join(Representante, Entrega.fk_representante == Representante.id_representante) \
         .join(JuntaDirectiva, Representante.fk_junta_directiva == JuntaDirectiva.idJuntas_Directivas)

        # Paginar manualmente ya que usamos columnas específicas
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        data = []
        for row in paginated.items:
            data.append({
                'id_racion': row.id_racion,
                'fecha_entrega': row.fecha_entrega.isoformat(),
                'estado': row.estado,
                'id_representante': row.id_representante,
                'junta_anio': row.junta_anio
            })

        return jsonify({
            'success': True,
            'total': paginated.total,
            'pages': paginated.pages,
            'page': paginated.page,
            'per_page': paginated.per_page,
            'data': data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'message': 'Error al listar las entregas'}), 500

# Ruta para insertar un nuevo registro de entrega
@entregas.route('/api/entregas/create', methods=['POST'])
def crear_entrega():
    try:
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
        
        # 📩 Datos del request
        data = request.get_json()
        fk_representante = representante.id_representante
        fecha_entrega = data.get('fecha_entrega')
        estado = data.get('estado', 'Pendiente')

        nueva_entrega = Entrega(fk_representante, fecha_entrega, estado)
        db.session.add(nueva_entrega)
        db.session.commit() 

        entregas_activas = Beneficiaria.query.filter_by(estado=True).all()

        for beneficiaria in entregas_activas:
            detalle = DetalleEntrega(
                fk_entrega=nueva_entrega.id_racion,
                fk_beneficiaria=beneficiaria.id_beneficiaria,
                cantidad_raciones=beneficiaria.cantidad_hijos,
                estado=False
            )
            db.session.add(detalle)
            db.session.flush()  # Para obtener el ID del detalle sin hacer commit

            # Determinar raciones según tipo
            tipo = beneficiaria.fk_tipo_beneficiaria
            raciones = beneficiaria.cantidad_hijos * (1 if tipo == 1 else 2 if tipo == 2 else 1)

            if raciones > 0:
                ID_AVENA = TipoViveres.query.filter_by(viver = 'Avena en bolsa').first().id_viver
                ID_LECHE = TipoViveres.query.filter_by(viver = 'Leche en lata').first().id_viver

                # Crear los viveres por ración
                detalle_avena = DetalleViveresEntregados(
                    fk_detalle_entrega=detalle.id_detalle_entregas,
                    fk_tipo_viver=ID_AVENA,
                    cantidad=raciones * 1
                )
                detalle_leche = DetalleViveresEntregados(
                    fk_detalle_entrega=detalle.id_detalle_entregas,
                    fk_tipo_viver=ID_LECHE,
                    cantidad=raciones * 6
                )

                db.session.add_all([detalle_avena, detalle_leche])
            
            # Obtener el tipo de multa y su monto
            tipo_multa = TipoMulta.query.get(TipoMulta.query.filter_by(tipo_multa = 'Multa por ración').first().id_tipo_multa)  
            if tipo_multa:
                # Calcular el monto total: monto_por_multa * cantidad_de_hijos y si no tiene hijos se multiplica por 1
                if beneficiaria.cantidad_hijos == 0:
                    monto_total = tipo_multa.monto * 1
                else:
                    monto_total = tipo_multa.monto * beneficiaria.cantidad_hijos
                
                nueva_multa = Multa(
                    fk_beneficiaria=beneficiaria.id_beneficiaria,
                    fk_tipo_multa=tipo_multa.id_tipo_multa,  
                    monto=monto_total, 
                    fecha_multa=datetime.now().date(),
                    pagado=0,  
                    observaciones=f'Multa por {beneficiaria.cantidad_hijos} comision de raciones en entrega'
                )
                db.session.add(nueva_multa)

        db.session.commit()

        return jsonify({'success': True, 'message': 'Entrega y víveres registrados correctamente'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
# Ruta para actualizar el estado de una entrega
@entregas.route('/api/entregas/<int:id_entrega>/update', methods=['PUT'])
def actualizar_entrega(id_entrega):
    try:
        estado = "Realizada"

        entrega = Entrega.query.get(id_entrega)
        if not entrega:
            return jsonify({'success': False, 'message': 'Entrega no encontrada'}), 404

        entrega.estado = estado
        db.session.commit()

        return jsonify({'success': True, 'message': 'Entrega actualizada correctamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
