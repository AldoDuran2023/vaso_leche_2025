from jwt import encode, decode, exceptions
from os import getenv
from datetime import datetime, timedelta
from flask import jsonify

# los dias que durara el token
def expire_data(days: int):
    now = datetime.now()
    new_date = now + timedelta(days)
    return new_date

# funcion para crear el token de auth
def write_token(data:dict):
    # generamos el token
    token = encode(payload={**data, "exp": expire_data(2)}, key=getenv("SECRET"), algorithm="HS256")
    return token.encode("UTF-8")

# funcion para validar el token
def validate_token(token, output=False):
    try:
        if output:
            return decode(token, key=getenv("SECRET"), algorithms=["HS256"])
        decode(token, key=getenv("SECRET"), algorithms=["HS256"])
    # nos pasa algo que no es token
    except exceptions.DecodeError:
        response = {
            "message": "invalidate Token"
        }
        return jsonify(response), 404
    # cuando el token ha expirado
    except exceptions.ExpiredSignatureError:
        response = {
            "message": "expirate Token"
        }
        return jsonify(response), 404