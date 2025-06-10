from flask import Blueprint, request, jsonify
from functionJWT import write_token, validate_token
from src.models.Usuario import Usuario
from src.models.Representante import Representante
from src.database.db import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"message": "Faltan datos"}), 400

    usuario = Usuario.query.filter_by(username=username).first()
    
    if usuario and check_password_hash(usuario.contrasena, password):
        representante = usuario.representante 
        rol = representante.fk_cargo if representante else None

        token = write_token({
            "id_usuario": usuario.id_usuario,
            "username": usuario.username,
            "fullname": usuario.fullname,
            "rol": rol
        }).decode('utf-8')

        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401


@auth.route('/verify/token')
def verify():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token requerido"}), 403
    try:
        token = token.split(" ")[1]
        return validate_token(token, output=True)
    except Exception as e:
        return jsonify({"message": "Token inválido", "error": str(e)}), 403


# Ruta para crear usuario
@auth.route('/api/usuarios/create', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')
    fk_representante = data.get('fk_representante')

    if not all([username, password, fullname, fk_representante]):
        return jsonify({"message": "Faltan datos"}), 400

    if Usuario.query.filter_by(username=username).first():
        return jsonify({"message": "El usuario ya existe"}), 409

    hashed_password = generate_password_hash(password)

    nuevo_usuario = Usuario(
        username=username,
        contrasena=hashed_password,
        fullname=fullname,
        fk_representante=fk_representante
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Usuario creado exitosamente"}), 201

# Ruta para actualizar usuario
@auth.route('/api/usuarios/update/<int:id_usuario>', methods=['PUT'])
def update_user(id_usuario):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')  # puede estar vacío si no desea cambiarla
    fullname = data.get('fullname')
    fk_representante = data.get('fk_representante')

    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    if username != usuario.username:
        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user and existing_user.id_usuario != id_usuario:
            return jsonify({"message": "El nombre de usuario ya está en uso"}), 409
        usuario.username = username

    if fullname:
        usuario.fullname = fullname

    if fk_representante:
        usuario.fk_representante = fk_representante

    if password:
        usuario.contrasena = generate_password_hash(password)

    db.session.commit()
    return jsonify({"message": "Usuario actualizado correctamente"}), 200

# Ruta para obtener todos los usuarios
@auth.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token requerido"}), 403
    try:
        token = token.split(" ")[1]
        validate_token(token)
    except Exception as e:
        return jsonify({"message": "Token inválido", "error": str(e)}), 403

    usuarios = Usuario.query.all()
    data = []
    for u in usuarios:
        representante = u.representante
        rol_nombre = None
        estado = None

        if representante:
            rol_nombre = representante.cargo.cargo if representante.cargo else None
            estado = representante.estado

        data.append({
            "id_usuario": u.id_usuario,
            "username": u.username,
            "fullname": u.fullname,
            "rol": rol_nombre,
            "estado": estado
        })

    return jsonify({"data": data}), 200

# NUEVA RUTA: Obtener usuario específico por ID
@auth.route('/api/usuarios/<int:id_usuario>', methods=['GET'])
def get_usuario_by_id(id_usuario):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token requerido"}), 403
    try:
        token = token.split(" ")[1]
        validate_token(token)
    except Exception as e:
        return jsonify({"message": "Token inválido", "error": str(e)}), 403

    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    data = {
        "id_usuario": usuario.id_usuario,
        "username": usuario.username,
        "fullname": usuario.fullname,
        "fk_representante": usuario.fk_representante
    }

    return jsonify(data), 200