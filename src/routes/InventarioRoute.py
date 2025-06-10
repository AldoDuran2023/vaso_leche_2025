from flask import Blueprint, request, jsonify
from src.models.Inventario import Inventario
from utils.paginador import paginar_query
from src.models.TipoViver import TipoViveres
from src.models.IngresoViver import IngresoViveres
from src.database.db import db
from utils.export_utils import export_to_excel, export_to_word, export_to_pdf


inventarios_bp = Blueprint('inventarios', __name__)

def get_inventario_data():
    inventarios = db.session.query(Inventario).join(Inventario.tipo_viver).all()
    return [{
        'N°': idx + 1,
        'Viveres': inv.tipo_viver.viver,
        'Tipo de Unidad': inv.tipo_viver.tipo_unidad,
        'Cantidad Total': inv.cantidad_total,
        'Fecha de Actualización': inv.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')
    } for idx, inv in enumerate(inventarios)]
    
def get_detalle_ingreso_viveres(id_ingreso: int):
    ingreso = db.session.query(IngresoViveres).filter_by(idIngreso_Viveres=id_ingreso).first()
    if not ingreso:
        return []

    junta = ingreso.junta_directiva

    data = []
    for idx, detalle in enumerate(ingreso.detalle_ingresos, start=1):  # ← CORREGIDO AQUÍ
        viver = detalle.tipo_viver
        data.append({
            'N°': idx,
            'Fecha de Ingreso': ingreso.fecha_ingreso.strftime('%d/%m/%Y'),
            'Responsable': ingreso.responsable,
            'Junta Directiva': junta.anio,
            'Vívere': viver.viver,
            'Tipo de Unidad': viver.tipo_unidad,
            'Cantidad': detalle.cantidad,
        })

    return data

    
# Rutas Para exportar datos de las inventarios_bp
@inventarios_bp.route('/api/ingreso-viveres/<int:id_ingreso>/export/pdf', methods=['GET'])
def export_detalle_ingreso_pdf(id_ingreso):
    data = get_detalle_ingreso_viveres(id_ingreso)
    return export_to_pdf(data, "Detalle de Ingreso de Viveres", f"detalle_ingreso_viveres_{id_ingreso}.pdf")


@inventarios_bp.route('/api/inventarios_bp/export/excel', methods=['GET'])
def export_excel():
    data = get_inventario_data()
    return export_to_excel(data, "inventarios_bp.xlsx")

@inventarios_bp.route('/api/inventarios_bp/export/word', methods=['GET'])
def export_word():
    data = get_inventario_data()
    return export_to_word(data, "Reporte de inventarios_bp", "inventarios_bp.docx")

@inventarios_bp.route('/api/inventarios_bp/export/pdf', methods=['GET'])
def export_pdf():
    data = get_inventario_data()
    return export_to_pdf(data, "Reporte de inventarios_bp", "inventarios_bp.pdf")


@inventarios_bp.route('/api/inventarios', methods=['GET'])
def listar_inventarios():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = Inventario.query.order_by(Inventario.fecha_actualizacion.desc())

        # Campos que quieres devolver
        fields = ['id_inventario', 'fk_tipo_viver', 'cantidad_total', 'fecha_actualizacion']

        resultado = paginar_query(query, page, per_page, 'inventarios.listar_inventarios', fields)

        # Formatear fechas
        for item in resultado['data']:
            item['fecha_actualizacion'] = item['fecha_actualizacion'].isoformat()

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error al listar los inventarios"
        }), 500

# Ruta para obtener todos los tipos de viveres
@inventarios_bp.route('/api/tipo_viveres', methods=['GET']) # Added leading slash for consistency
def listar_tipo_viveres():
    try:
        tipo_viveres = TipoViveres.query.all() # Changed this line
        
        result = [
            {
                "id": tv.id_viver, # Changed to id_viver based on your model
                "nombre": tv.viver,
                "unidad": tv.tipo_unidad
            } for tv in tipo_viveres
        ]
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error al listar los tipos de víveres"
        }), 500