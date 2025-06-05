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
from sqlalchemy.orm import load_only

entregas = Blueprint('entregas', __name__)

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
        data = request.get_json()
        fk_representante = data.get('fk_representante')
        fecha_entrega = data.get('fecha_entrega')
        estado = data.get('estado', 'Pendiente')

        nueva_entrega = Entrega(fk_representante, fecha_entrega, estado)
        db.session.add(nueva_entrega)
        db.session.commit()  # Necesario para tener el id_racion

        beneficiarias_activas = Beneficiaria.query.filter_by(estado=True).all()

        for beneficiaria in beneficiarias_activas:
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
                    cantidad=raciones * 3
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



        