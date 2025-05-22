from flask import request, jsonify
from functools import wraps
from functionJWT import validate_token

def role_required(roles):
    """Decorador para restringir acceso por rol"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"message": "Token requerido"}), 403

            try:
                token = token.split(" ")[1]  # Extraer el token después de "Bearer"
                user_data = validate_token(token, output=True)  # Decodificar el token

                # Si el resultado es un diccionario con 'error', el token no es válido
                if isinstance(user_data, dict) and "error" in user_data:
                    return jsonify(user_data), 403

                if user_data.get("rol") not in roles:
                    return jsonify({"message": "Acceso denegado"}), 403
                
                return f(*args, **kwargs)  # Continuar con la ruta si el rol es válido
            except Exception as e:
                return jsonify({"message": "Token inválido", "error": str(e)}), 403
        
        return wrapper
    return decorator