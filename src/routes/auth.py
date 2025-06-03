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


@auth.route('/register', methods=['POST'])
def register():
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
